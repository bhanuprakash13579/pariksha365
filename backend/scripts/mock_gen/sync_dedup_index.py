"""Pull existing ``quiz_questions`` from the production DB and emit a dedup
signature file that the static-GK generator consults before writing new Qs.

Credential lives in ``backend/.env.local`` as ``PRODUCTION_DB_URL`` — that
file is gitignored. Never hard-code the URL here; never log it.

Output: ``backend/seeds/_dedup/existing_quiz_signatures.json`` — a JSON doc
with two lookup sets:

  * ``stem_signatures`` — normalised-stem shingles (case-folded,
    whitespace-collapsed, punctuation stripped, trimmed to 160 chars).
    Exact matches here block duplicate creation.
  * ``topic_first_option`` — ``{topic_code}|{first_option_normalised}``
    tuples. Catches near-duplicates that reword the stem but keep the same
    option set.

Rerun before every static-GK generation batch::

    python -m scripts.mock_gen.sync_dedup_index
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

log = logging.getLogger("sync_dedup_index")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def _normalise_stem(raw: str, max_len: int = 160) -> str:
    """Collapse a question stem into a signature suitable for exact-match dedup.

    Case-fold, strip non-word characters, collapse whitespace, trim to
    ``max_len``. 160 chars is enough to make unique stems distinguishable
    without being fragile to trailing verbiage.
    """
    if not raw:
        return ""
    s = raw.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s[:max_len]


def _normalise_option(raw: str) -> str:
    if not raw:
        return ""
    s = raw.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s[:60]


def _load_env_local(env_path: Path) -> dict:
    """Parse a minimal .env file — enough for a single-line
    ``KEY=value`` format. Avoids a python-dotenv dependency.
    """
    out: dict = {}
    if not env_path.exists():
        return out
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _connect(url: str):
    """Lazily import psycopg so --help works without the library installed."""
    try:
        import psycopg  # type: ignore

        return psycopg.connect(url)
    except ImportError:
        pass
    try:
        import psycopg2  # type: ignore

        return psycopg2.connect(url)
    except ImportError as e:
        raise RuntimeError(
            "Neither 'psycopg' nor 'psycopg2' is installed. "
            "Install one with: pip install psycopg[binary] "
            "or pip install psycopg2-binary"
        ) from e


def sync(env_local_path: Path, out_path: Path, dry_run: bool = False) -> int:
    env = _load_env_local(env_local_path)
    db_url = os.environ.get("PRODUCTION_DB_URL") or env.get("PRODUCTION_DB_URL")
    if not db_url:
        log.error(
            "PRODUCTION_DB_URL not set; put it in %s or export it.", env_local_path
        )
        return 2
    log.info("connecting to production DB (credential redacted)…")

    stem_sigs: set[str] = set()
    topic_first_sigs: set[str] = set()
    fuzzy_list: List[dict] = []
    # Count rows per (subject, topic_code, topic) so we can export the user's
    # existing taxonomy — the generator must honour this naming rather than
    # inventing its own parallel set of topic_codes.
    taxonomy_counts: dict = {}

    with _connect(db_url) as conn, conn.cursor() as cur:
        # Robust against either psycopg or psycopg2 cursor APIs
        cur.execute(
            """
            SELECT id::text, question_text, options, topic_code, subject, topic
            FROM quiz_questions
            """
        )
        rows = cur.fetchall()
        log.info("fetched %d rows from quiz_questions", len(rows))
        for row in rows:
            _id, stem, opts, topic_code, subject, topic = row
            tax_key = f"{subject}|{topic_code}|{topic}"
            taxonomy_counts[tax_key] = taxonomy_counts.get(tax_key, 0) + 1
            stem_sig = _normalise_stem(stem or "")
            if stem_sig:
                stem_sigs.add(stem_sig)
            first_opt_norm = ""
            if isinstance(opts, list) and opts:
                first = opts[0]
                if isinstance(first, dict):
                    # Production schema stores options as [{option_text, is_correct}, ...];
                    # keep fallbacks in case the shape ever changes.
                    first_opt_norm = _normalise_option(
                        first.get("option_text")
                        or first.get("text")
                        or first.get("body")
                        or ""
                    )
                else:
                    first_opt_norm = _normalise_option(str(first))
            if topic_code and first_opt_norm:
                topic_first_sigs.add(f"{topic_code}|{first_opt_norm}")
            # Keep a fuzzy-match-ready list of short shingles for later Levenshtein checks
            if stem_sig:
                fuzzy_list.append({"id": _id, "stem_sig": stem_sig, "topic_code": topic_code})

    # Build an ordered taxonomy summary — one row per (subject, topic_code,
    # topic) with its existing Q count. This is what the generator should
    # reuse when assigning topic_codes to new Qs so we don't fork the taxonomy.
    taxonomy_rows = sorted(
        ({"subject": k.split("|", 2)[0] or None,
          "topic_code": k.split("|", 2)[1] or None,
          "topic": k.split("|", 2)[2] or None,
          "existing_q_count": v}
         for k, v in taxonomy_counts.items()),
        key=lambda r: (r["subject"] or "", r["topic_code"] or ""),
    )

    payload = {
        "schema_version": 2,
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "PRODUCTION_DB.quiz_questions (credential redacted)",
        "row_count": len(fuzzy_list),
        "stem_signature_count": len(stem_sigs),
        "topic_first_signature_count": len(topic_first_sigs),
        "existing_taxonomy_size": len(taxonomy_rows),
        "existing_taxonomy": taxonomy_rows,
        "stem_signatures": sorted(stem_sigs),
        "topic_first_signatures": sorted(topic_first_sigs),
        "fuzzy_candidates": fuzzy_list,
        "notes": (
            "Consumers should reject new Qs whose normalised stem appears in "
            "stem_signatures OR whose (topic_code|first_option) pair appears "
            "in topic_first_signatures. For Levenshtein fuzzy matching, walk "
            "fuzzy_candidates filtered to the same topic_code first. "
            "Generators MUST reuse topic_codes from existing_taxonomy when a "
            "new Q fits — don't fork the naming."
        ),
    }

    if dry_run:
        log.info(
            "dry-run: would write %d stem sigs + %d topic/first sigs to %s",
            len(stem_sigs), len(topic_first_sigs), out_path,
        )
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    log.info(
        "wrote %s — %d stem sigs, %d topic/first sigs",
        out_path, len(stem_sigs), len(topic_first_sigs),
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    backend_dir = Path(__file__).resolve().parents[2]
    ap.add_argument("--env-local", default=str(backend_dir / ".env.local"))
    ap.add_argument(
        "--out",
        default=str(backend_dir / "seeds" / "_dedup" / "existing_quiz_signatures.json"),
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return sync(Path(args.env_local), Path(args.out), args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
