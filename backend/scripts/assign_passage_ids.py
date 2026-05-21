#!/usr/bin/env python3
"""
assign_passage_ids.py
=====================
1. Scans all ENG_RC seed files to find questions that share a passage.
2. Assigns a stable `passage_id` (short hash) to every question in each group.
3. Fixes "broken" questions whose stems say "(Same X passage.)" or
   "In the same passage..." without embedding the passage text —
   re-writes their stem to include the full passage.
4. Saves the updated seed files back to disk.

Run from repo root:
    python3 backend/scripts/assign_passage_ids.py [--dry-run]
"""
import argparse
import glob
import hashlib
import json
import os
import re

SEEDS_ROOT = "backend/seeds/static_gk"


def extract_passage(stem: str) -> str | None:
    """Return passage text if the stem contains a PASSAGE: '...' block.
    Handles two formats:
      1. PASSAGE: 'text'  or  PASSAGE: "text"  (quoted)
      2. Passage: text\\n\\n question text       (unquoted, double-newline separator)
    """
    # Format 1 — quoted
    m = re.search(r"(?:PASSAGE|Passage)[:\s]+['\"](.+?)['\"]", stem, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Format 2 — unquoted; passage is everything before the first blank line
    m = re.match(r"(?:PASSAGE|Passage)[:\s]+(.+?)\n\n", stem, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def passage_id(passage_text: str) -> str:
    return "RC_" + hashlib.md5(passage_text.encode()).hexdigest()[:10].upper()


def is_back_reference(stem: str) -> bool:
    """True when the stem references a previous passage without embedding it."""
    markers = [
        r"\(same .+? passage\)",
        r"in the same passage",
        r"based on the same passage",
        r"from the same passage",
        r"in the .+?-car passage",
        r"in the .+? passage",
    ]
    for pat in markers:
        if re.search(pat, stem, re.IGNORECASE):
            return True
    return False


def process_file(path: str, dry_run: bool) -> int:
    with open(path) as f:
        data = json.load(f)

    is_list = isinstance(data, list)
    q_list = data if is_list else data.get("questions", [])

    # ── Pass 1: extract all passages that appear in this file ──────────────
    # Map passage_text → list of question indices that embed it
    passage_to_indices: dict[str, list[int]] = {}
    idx_to_passage: dict[int, str] = {}

    for i, q in enumerate(q_list):
        if q.get("topic_code") != "ENG_RC":
            continue
        p = extract_passage(q.get("stem", ""))
        if p:
            passage_to_indices.setdefault(p, []).append(i)
            idx_to_passage[i] = p

    # Filter to passages that appear in 2+ questions (i.e., shared passages)
    shared_passages = {p: idxs for p, idxs in passage_to_indices.items() if len(idxs) >= 2}

    # ── Pass 2: find back-reference questions and map them to their passage ─
    # Strategy: a back-reference follows an embedded question; we attribute it
    # to the LAST embedded passage seen before it.
    changes = 0
    last_passage = None
    last_passage_id_val = None

    for i, q in enumerate(q_list):
        if q.get("topic_code") != "ENG_RC":
            continue
        stem = q.get("stem", "")
        p = extract_passage(stem)

        if p:
            last_passage = p
            last_passage_id_val = passage_id(p)
            # Assign passage_id to this question if its passage is shared
            if p in shared_passages:
                q["passage_id"] = last_passage_id_val
                changes += 1
        elif is_back_reference(stem) and last_passage:
            # Fix: prepend the full passage to the stem
            pid = passage_id(last_passage)
            # Build the cleaned question part (strip back-reference prefix)
            cleaned = re.sub(
                r"^\s*\(same .+? passage\\.?\)\s*",
                "",
                stem,
                flags=re.IGNORECASE,
            ).strip()
            cleaned = re.sub(
                r"^(?:in|based on|from) the same passage[,.]?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()
            cleaned = re.sub(
                r"^in the .+?-car passage[,.]?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()
            # If cleaned stem is empty or just punctuation, keep original
            if not cleaned or len(cleaned) < 10:
                cleaned = stem
            new_stem = f"Passage: '{last_passage}'\n\n{cleaned}"
            q["stem"] = new_stem
            q["passage_id"] = pid
            changes += 1
        # Also assign passage_id to shared-passage questions we missed in first loop
        if p and p in shared_passages and "passage_id" not in q:
            q["passage_id"] = passage_id(p)
            changes += 1

    if changes == 0:
        return 0

    if not dry_run:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(glob.glob(f"{SEEDS_ROOT}/**/*.json", recursive=True))
    files = [f for f in files if not os.path.basename(f).startswith("_")]

    total_changes = 0
    for f in files:
        try:
            n = process_file(f, dry_run=args.dry_run)
            if n:
                print(f"  {'[DRY] ' if args.dry_run else ''}Updated {n} questions in {f}")
                total_changes += n
        except Exception as e:
            print(f"  SKIP {f}: {e}")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Total questions updated: {total_changes}")


if __name__ == "__main__":
    main()
