#!/usr/bin/env python3
"""
normalize_topic_codes.py
========================
Rewrites topic_code fields in all static-GK seed JSON files to their
canonical taxonomy equivalents using TOPIC_CODE_MAP from topic_code_map.py.

Also adds new canonical entries to taxonomy_data.py if missing.

Usage:
    python3 backend/scripts/normalize_topic_codes.py [--dry-run] [--stats]
"""
import argparse
import glob
import json
import os
import sys
import re
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.topic_code_map import TOPIC_CODE_MAP, NEW_CANONICAL_CODES

SEEDS_PATH = "backend/seeds/static_gk"
TAXONOMY_DATA_PATH = "backend/app/services/taxonomy_data.py"


def load_canonical_set() -> set:
    with open(TAXONOMY_DATA_PATH) as f:
        content = f.read()
    return set(re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*"([A-Z][A-Z_0-9]+)"', content))


def normalize_seeds(dry_run: bool = False, stats: bool = False) -> dict:
    changed_files = 0
    changed_questions = 0
    unmapped_codes: dict[str, int] = defaultdict(int)
    mapping_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    files = sorted(glob.glob(f"{SEEDS_PATH}/**/*.json", recursive=True))
    files = [f for f in files if not os.path.basename(f).startswith("_")]

    for fpath in files:
        try:
            with open(fpath) as f:
                data = json.load(f)
        except Exception as e:
            print(f"SKIP {fpath}: {e}")
            continue

        is_list = isinstance(data, list)
        q_list = data if is_list else data.get("questions", [])

        file_changed = False
        for q in q_list:
            old_code = q.get("topic_code", "")
            if not old_code:
                continue
            new_code = TOPIC_CODE_MAP.get(old_code, old_code)
            if new_code != old_code:
                mapping_counts[old_code][new_code] += 1
                if not dry_run:
                    q["topic_code"] = new_code
                file_changed = True
                changed_questions += 1
            else:
                unmapped_codes[old_code] += 1

        if file_changed:
            changed_files += 1
            if not dry_run:
                with open(fpath, "w") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

    result = {
        "changed_files": changed_files,
        "changed_questions": changed_questions,
        "unique_mappings_applied": len(mapping_counts),
    }

    if stats:
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Normalization stats:")
        print(f"  Files modified: {changed_files}")
        print(f"  Questions updated: {changed_questions}")
        print(f"  Unique code mappings applied: {len(mapping_counts)}")
        print(f"\nTop 20 mappings applied:")
        top = sorted(mapping_counts.items(), key=lambda x: sum(x[1].values()), reverse=True)[:20]
        for old, new_dict in top:
            for new, cnt in new_dict.items():
                print(f"  {old:<55} → {new}  ({cnt} Qs)")

        # Find codes not in TOPIC_CODE_MAP and not canonical
        with open(TAXONOMY_DATA_PATH) as f:
            content = f.read()
        canonical = set(re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*"([A-Z][A-Z_0-9]+)"', content))
        canonical_codes = {c[2] for c in canonical}
        still_non_canonical = {c: n for c, n in unmapped_codes.items() if c not in canonical_codes}
        if still_non_canonical:
            print(f"\nCodes with no mapping AND not in taxonomy ({len(still_non_canonical)}):")
            for c, n in sorted(still_non_canonical.items(), key=lambda x: -x[1])[:30]:
                print(f"  {c}  ({n} Qs)")

    return result


def add_new_canonicals(dry_run: bool = False) -> int:
    """Append NEW_CANONICAL_CODES entries to taxonomy_data.py if missing."""
    with open(TAXONOMY_DATA_PATH) as f:
        content = f.read()

    existing_codes = set(re.findall(r'"([A-Z][A-Z_0-9]{3,})"', content))
    added = 0
    new_lines = []

    for subject, topic, code, aliases in NEW_CANONICAL_CODES:
        if code in existing_codes:
            continue
        aliases_repr = json.dumps(aliases)
        line = f'    ("{subject}", "{topic}", "{code}", {aliases_repr}),\n'
        new_lines.append((subject, line))
        added += 1

    if new_lines and not dry_run:
        # Group by subject and insert before the closing bracket of each subject section
        # Simpler: just append before TAXONOMY_EXPANDED closing bracket
        insert_point = content.rfind("]")  # last ] closes TAXONOMY_EXPANDED
        insertion = "\n    # ─── New canonicals added by normalize_topic_codes.py ───\n"
        for subject, line in new_lines:
            insertion += line
        new_content = content[:insert_point] + insertion + content[insert_point:]
        with open(TAXONOMY_DATA_PATH, "w") as f:
            f.write(new_content)

    if added:
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Added {added} new canonical entries to taxonomy_data.py:")
        for subject, line in new_lines:
            print(f"  {line.strip()}")

    return added


def main():
    parser = argparse.ArgumentParser(description="Normalize topic_codes in seed files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    parser.add_argument("--stats", action="store_true", help="Show detailed stats")
    args = parser.parse_args()

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Normalizing topic codes in seed files...")

    # 1. Add new canonical codes to taxonomy_data.py
    added = add_new_canonicals(dry_run=args.dry_run)

    # 2. Rewrite seed files
    result = normalize_seeds(dry_run=args.dry_run, stats=True)

    print(f"\n{'✓' if not args.dry_run else '○'} Done:")
    print(f"  New taxonomy entries added: {added}")
    print(f"  Seed files updated: {result['changed_files']}")
    print(f"  Questions renormalized: {result['changed_questions']}")


if __name__ == "__main__":
    main()
