"""Sync static-GK seed topic_codes into the production ``subject_taxonomy``.

Walk every JSON under ``backend/seeds/static_gk`` and ensure each distinct
``topic_code`` is resolvable in the prod taxonomy — either as its own row
or attached as an alias on an existing ``(subject, topic)`` row.

Idempotent. Safe to re-run after every content wave; intended to be the
last step of a wave alongside ``git commit`` + ``git push``.

Credential is read from ``backend/.env.local`` (gitignored, never logged).

Usage::

    python3 backend/scripts/sync_taxonomy_from_seeds.py
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

# Reuse the prod-DB connector from the EPFO seed script (same env file format).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.seed_epfo_module_prod import _load_env_local, _connect  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds" / "static_gk"
ENV_LOCAL = ROOT / ".env.local"


def main() -> int:
    triples: dict[str, tuple[str, str]] = {}
    for jf in SEEDS.rglob("*.json"):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("subject") and data.get("topic") and data.get("topic_code"):
            triples.setdefault(data["topic_code"], (data["subject"], data["topic"]))

    print(f"seed topic_codes: {len(triples)}")

    env = _load_env_local(ENV_LOCAL)
    url = os.environ.get("PRODUCTION_DB_URL") or env.get("PRODUCTION_DB_URL")
    if not url:
        print(f"PRODUCTION_DB_URL not set in {ENV_LOCAL} or env")
        return 2

    inserted = aliased = skipped = 0
    with _connect(url) as conn, conn.cursor() as cur:
        cur.execute("SELECT id, subject, topic, topic_code, aliases FROM subject_taxonomy")
        rows = cur.fetchall()
        by_code = {r[3]: r for r in rows}
        by_subject_topic = {(r[1], r[2]): r for r in rows}
        alias_lookup = {}
        for r in rows:
            for a in r[4] or []:
                alias_lookup[a] = r

        for tc, (subj, topic) in triples.items():
            if tc in by_code or tc in alias_lookup:
                skipped += 1
                continue
            pair = (subj, topic)
            if pair in by_subject_topic:
                row = by_subject_topic[pair]
                row_id, _, _, _, aliases = row
                aliases = list(aliases or [])
                if tc not in aliases:
                    aliases.append(tc)
                cur.execute(
                    "UPDATE subject_taxonomy SET aliases = %s WHERE id = %s",
                    (json.dumps(aliases), row_id),
                )
                aliased += 1
            else:
                new_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO subject_taxonomy (id, subject, topic, topic_code, aliases) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (new_id, subj, topic, tc, json.dumps([])),
                )
                inserted += 1
                by_code[tc] = (new_id, subj, topic, tc, [])
                by_subject_topic[pair] = by_code[tc]
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM subject_taxonomy")
        total = cur.fetchone()[0]

    print(f"inserted new rows:    {inserted}")
    print(f"aliased into row:     {aliased}")
    print(f"skipped (already in): {skipped}")
    print(f"total taxonomy rows:  {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
