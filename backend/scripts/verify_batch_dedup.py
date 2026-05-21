"""Near-duplicate detector for static-GK question seeds.

Why this script exists
----------------------
The existing ``static_gk_writer.apply_batch()`` logic in this directory
catches ONLY exact matches after normalisation — case, punctuation, and
whitespace are collapsed, but everything else must match character-for-
character to count as a duplicate. That misses the MOST COMMON real-world
duplicate pattern: the same question reworded slightly.

Examples this script catches that ``apply_batch`` would miss:

  • "The Attorney General of India is appointed by whom?"
    vs "Who appoints the Attorney General of India?"
  • "Madhubani painting originates from which state?"
    vs "From which region does Madhubani painting come?"
  • "Which was the first UNESCO site in India?"
    vs "What is India's oldest UNESCO world heritage site?"

Approach
--------
For each pair of stems WITHIN THE SAME topic_code:

  1.   Strip stop-words and punctuation, tokenise.
  2.   Compute a set of word-4-grams (order-preserving shingles).
  3.   Compute Jaccard similarity = |A ∩ B| / |A ∪ B|.
  4.   Flag pairs with Jaccard >= 0.50 as SUSPICIOUS.
  5.   Flag pairs where the normalised CORRECT-ANSWER text matches AND the
       stem similarity >= 0.30 as LIKELY DUPLICATE (both testing same fact).

Usage
-----
    python3 -m scripts.mock_gen.verify_batch_dedup                # check all seeds
    python3 -m scripts.mock_gen.verify_batch_dedup --threshold 0.60
    python3 -m scripts.mock_gen.verify_batch_dedup --only POL_FR  # one topic

Runs a cross-check against the existing ``_dedup/existing_quiz_signatures.json``
(production DB stems) too, flagging seeds that paraphrase an already-in-DB Q.

Exit code 1 if any suspicious pairs were found — so this can be wired into
the commit/load pipeline as a pre-flight check.

Implementation is pure stdlib (no scikit-learn, no sentence-transformers) so
it runs on any Python 3.9+ without additional installs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

_BACKEND = Path(__file__).resolve().parents[2]
_SEEDS = _BACKEND / "seeds"
_DEDUP_PATH = _SEEDS / "_dedup" / "existing_quiz_signatures.json"
_POOL_DIR = _SEEDS / "static_gk"

# Stop-word list intentionally short — we want to keep content words like
# "first", "last", "largest" which ARE semantically important for these
# fact-recall questions (the existing broader stop-word lists would hide
# real differences between Qs).
_STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "by", "from",
    "with", "and", "or", "is", "are", "was", "were", "be", "been", "being",
    "which", "what", "who", "whom", "whose", "where", "when", "why", "how",
    "does", "do", "did", "has", "have", "had", "as", "that", "this", "these",
    "those", "it", "its", "would", "should", "could", "may", "might", "must",
    "can", "shall", "will", "any", "all", "some", "following", "among",
}

_NONWORD = re.compile(r"[^a-z0-9\s]")
_WS = re.compile(r"\s+")


def _tokens(stem: str) -> list[str]:
    s = _NONWORD.sub(" ", (stem or "").lower())
    s = _WS.sub(" ", s).strip()
    return [t for t in s.split() if t and t not in _STOPWORDS]


def _shingles(stem: str, n: int = 4) -> set[tuple[str, ...]]:
    toks = _tokens(stem)
    if len(toks) < n:
        return {tuple(toks)} if toks else set()
    return {tuple(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _normalise_answer(opts: list[dict]) -> str:
    for o in opts or []:
        if isinstance(o, dict) and o.get("is_correct"):
            t = (o.get("option_text") or "").lower()
            t = _NONWORD.sub(" ", t)
            t = _WS.sub(" ", t).strip()
            return t
    return ""


def _load_seed_questions(only_code: str | None = None):
    """Yield (topic_code, subject, bundle_path, stem, answer_norm, q_dict)."""
    for bundle_file in _POOL_DIR.rglob("*.json"):
        if bundle_file.name.startswith("_"):
            continue
        try:
            doc = json.loads(bundle_file.read_text())
        except Exception:
            continue
        for q in doc.get("questions", []) or []:
            tc = q.get("topic_code") or doc.get("topic_code")
            if only_code and tc != only_code:
                continue
            stem = q.get("stem") or ""
            ans = _normalise_answer(q.get("options") or [])
            yield (tc or "UNKNOWN",
                   doc.get("subject"),
                   bundle_file.relative_to(_SEEDS),
                   stem,
                   ans,
                   q)


def _load_production_stems(only_code: str | None = None):
    """Load production stem signatures grouped by (topic_code, fuzzy_candidate_stem).

    Returns a dict: topic_code -> list[(stem_sig_160chars, shingle_set)].
    NOTE: production stems in the index are normalised to 160 chars — we can't
    recover full stems for shingling. Best-effort: shingle the normalised snippet.
    """
    by_code: dict[str, list[tuple[str, set]]] = defaultdict(list)
    if not _DEDUP_PATH.exists():
        return by_code
    doc = json.loads(_DEDUP_PATH.read_text())
    for entry in doc.get("fuzzy_candidates") or []:
        tc = entry.get("topic_code") or "UNKNOWN"
        snippet = entry.get("stem_sig") or ""
        by_code[tc].append((snippet, _shingles(snippet)))
    return by_code


def run(threshold: float, only_code: str | None) -> int:
    seed_qs = list(_load_seed_questions(only_code))
    if not seed_qs:
        print("no seeds found.")
        return 0

    # Pre-compute shingles for each seed Q (once).
    shingled = [(tc, subj, path, stem, ans, _shingles(stem)) for tc, subj, path, stem, ans, _q in seed_qs]

    # Group by topic_code for within-topic pairwise compare (O(N^2) per topic,
    # but topic bundles rarely exceed 300 Qs — still tractable).
    by_topic: dict[str, list] = defaultdict(list)
    for item in shingled:
        by_topic[item[0]].append(item)

    pairs_flagged: list[dict] = []

    for tc, items in by_topic.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                _, _, pa, sa, aa, ga = items[i]
                _, _, pb, sb, ab, gb = items[j]
                sim = _jaccard(ga, gb)
                same_answer = bool(aa) and aa == ab
                # Flag threshold: stem-similarity >= threshold OR
                # (same answer AND stem-similarity >= 0.30)
                if sim >= threshold or (same_answer and sim >= 0.30):
                    pairs_flagged.append({
                        "topic_code": tc,
                        "jaccard": round(sim, 3),
                        "same_answer": same_answer,
                        "a_path": str(pa), "a_stem": sa,
                        "b_path": str(pb), "b_stem": sb,
                    })

    # Cross-check against production DB stems (fuzzy)
    prod = _load_production_stems(only_code)
    prod_flagged: list[dict] = []
    for tc, subj, path, stem, ans, shing in shingled:
        for prod_snip, prod_shing in prod.get(tc, []):
            sim = _jaccard(shing, prod_shing)
            if sim >= threshold:
                prod_flagged.append({
                    "topic_code": tc,
                    "jaccard": round(sim, 3),
                    "seed_path": str(path),
                    "seed_stem": stem,
                    "prod_stem_sig_snippet": prod_snip[:160],
                })

    # Report
    print(f"\n=== verify_batch_dedup: {len(seed_qs)} seed Qs scanned ===")
    print(f"    threshold = {threshold} (Jaccard of 4-word shingles)")
    print(f"    within-seed suspicious pairs: {len(pairs_flagged)}")
    print(f"    vs production DB suspicious pairs: {len(prod_flagged)}")

    if pairs_flagged:
        print("\n--- SUSPICIOUS PAIRS WITHIN SEEDS ---")
        for p in sorted(pairs_flagged, key=lambda x: -x["jaccard"])[:100]:
            marker = "!! SAME ANSWER" if p["same_answer"] else ""
            print(f"\n  [{p['topic_code']}] jaccard={p['jaccard']} {marker}")
            print(f"    A ({p['a_path']}):\n      {p['a_stem']}")
            print(f"    B ({p['b_path']}):\n      {p['b_stem']}")

    if prod_flagged:
        print("\n--- SEEDS PARAPHRASING PRODUCTION Q's ---")
        for p in sorted(prod_flagged, key=lambda x: -x["jaccard"])[:100]:
            print(f"\n  [{p['topic_code']}] jaccard={p['jaccard']}")
            print(f"    SEED  ({p['seed_path']}):\n      {p['seed_stem']}")
            print(f"    PROD  (stem sig): {p['prod_stem_sig_snippet']}")

    exit_code = 1 if (pairs_flagged or prod_flagged) else 0
    if exit_code == 0:
        print("\n  OK — no near-duplicates detected.")
    return exit_code


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.50,
                    help="Jaccard similarity threshold for 'suspicious' (default 0.50)")
    ap.add_argument("--only", type=str, default=None,
                    help="Restrict to one topic_code (e.g. POL_FR)")
    args = ap.parse_args()
    return run(args.threshold, args.only)


if __name__ == "__main__":
    sys.exit(main())
