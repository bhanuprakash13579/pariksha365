#!/usr/bin/env python3
"""One-time data-migration: consolidate the `topic` field on every AP TET / AP
DSC-SGT private-module question so that all questions sharing the same
`topic_code` also share the same `topic` string.

Why: the frontend's "chapters" screen (PrivateModuleTopicsScreen) groups
practice sets by the exact (topic, topic_code) pair returned from
get_subject_topics(), which does `GROUP BY topic, topic_code`. Content was
authored with a UNIQUE, fine-grained `topic` label per question (meant only
as an internal completeness-tracking label, e.g. "Bruner -- Spiral
curriculum"), so 99%+ of "chapters" ended up with exactly 1 question --
unusable for practice. `topic_code` was always the correctly-designed
chapter-level grouping (56-59 distinct codes, most with 10-40+ Qs already).

This script does not delete or reorder any question data -- it only
rewrites the `topic` string field to a single canonical chapter name per
topic_code, chosen automatically from the most common `section` value
within that group (stripped of the "Subject Name Chapter Number --" prefix
and "(Complete)"/"Deep Practice" suffixes). Run once, then commit + reseed.

Usage:
    python3 backend/scripts/fix_tet_sgt_topic_grouping.py           # dry run, prints mapping
    python3 backend/scripts/fix_tet_sgt_topic_grouping.py --apply   # writes files
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "seeds", "private_modules")

STRIP_PATTERNS = [
    r"^.*?·\s*Ch\d*[A-Za-z]?\s*[—-]\s*",   # "Subject · Ch5 — " prefix
    r"^.*?·\s*",                            # any remaining "Subject · " prefix
]
SUFFIX_PATTERNS = [
    r"\s*\(Complete\)\s*$",
    r"\s*—\s*Deep Practice\s*\d*\s*$",
    r"\s*—\s*Deep\s*\d*\s*$",
    r"\s*\(Teaching Methods.*?\)\s*$",
]


def clean_section_to_topic(section: str) -> str:
    name = section
    for pat in STRIP_PATTERNS:
        name = re.sub(pat, "", name)
    for pat in SUFFIX_PATTERNS:
        name = re.sub(pat, "", name)
    return name.strip(" —-")


MANUAL_OVERRIDES = {
    "TETSGT_EDPSY_PERSONALITY": "Personality: Theories & Defense Mechanisms",
    "TETSGT_CDP_PERSONALITY": "Personality: Theories & Defense Mechanisms",
    "TETSGT_SOC_METHODOLOGY": "Methodology of Teaching Social Studies",
    "TETSGT_SOCIAL_METHODOLOGY": "Methodology of Teaching Social Studies",
    "TETSGT_SCI_METHODOLOGY": "Methodology of Teaching Science",
    "TETSGT_ENG_METHOD": "Methodology of Teaching English",
}


def build_mapping(mod: str) -> dict[str, str]:
    section_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for path in glob.glob(os.path.join(ROOT, mod, "*.json")):
        data = json.loads(open(path, encoding="utf-8").read())
        for q in data:
            section_counts[q["topic_code"]][q["section"]] += 1

    mapping = {}
    for code, counter in section_counts.items():
        if code in MANUAL_OVERRIDES:
            mapping[code] = MANUAL_OVERRIDES[code]
            continue
        best_section = counter.most_common(1)[0][0]
        mapping[code] = clean_section_to_topic(best_section)
    return mapping


def apply_mapping(mod: str, mapping: dict[str, str], apply: bool) -> int:
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, mod, "*.json"))):
        data = json.loads(open(path, encoding="utf-8").read())
        file_changed = False
        for q in data:
            new_topic = mapping[q["topic_code"]]
            if q["topic"] != new_topic:
                q["topic"] = new_topic
                changed += 1
                file_changed = True
        if file_changed and apply:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
    return changed


def main() -> int:
    apply = "--apply" in sys.argv
    total = 0
    for mod in ("ap_dsc_sgt", "ap_tet"):
        mapping = build_mapping(mod)
        print(f"=== {mod}: {len(mapping)} topic_codes -> canonical topic names ===")
        for code, name in sorted(mapping.items()):
            print(f"  {code:35s} -> {name}")
        n = apply_mapping(mod, mapping, apply)
        print(f"{mod}: {n} questions {'updated' if apply else 'would be updated'}\n")
        total += n
    if not apply:
        print(f"DRY RUN — {total} questions would change. Re-run with --apply to write.")
    else:
        print(f"APPLIED — {total} questions updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
