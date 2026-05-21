#!/usr/bin/env python3
"""
update_coordination_manifest.py
================================
Run this after any batch of question generation to refresh the coordination manifest.
Both Antigravity and Claude Code should run this after every session.

Usage:
    python3 update_coordination_manifest.py
"""

import json
import glob
import os
import datetime

MANIFEST_PATH = "backend/seeds/static_gk/_coordination_manifest.json"
SEEDS_PATH = "backend/seeds/static_gk"


def main():
    all_codes = set()
    q_total = 0
    subject_counts = {}

    for f in glob.glob(f"{SEEDS_PATH}/**/*.json", recursive=True):
        if os.path.basename(f).startswith("_"):
            continue
        try:
            with open(f) as fh:
                data = json.load(fh)
            # Support both plain-list format and dict-wrapped {topic_code, questions:[...]} format
            if isinstance(data, list):
                q_list = data
                tc = q_list[0].get("topic_code", "") if q_list else ""
                subj = q_list[0].get("subject", "unknown") if q_list else "unknown"
            else:
                q_list = data.get("questions", [])
                tc = data.get("topic_code", "") or (q_list[0].get("topic_code", "") if q_list else "")
                subj = data.get("subject", "") or (q_list[0].get("subject", "unknown") if q_list else "unknown")
            qs = len(q_list)
            if tc:
                all_codes.add(tc)
                q_total += qs
                subject_counts[subj] = subject_counts.get(subj, 0) + qs
        except Exception:
            pass

    # Load existing manifest
    with open(MANIFEST_PATH) as fh:
        manifest = json.load(fh)

    # Update fields
    manifest["covered_topic_codes"] = sorted(list(all_codes))
    manifest["stats"]["total_files"] = len(all_codes)
    manifest["stats"]["total_questions"] = q_total
    manifest["stats"]["remaining"] = 50000 - q_total
    manifest["stats"]["by_subject"] = subject_counts
    manifest["last_updated"] = datetime.datetime.now(
        datetime.timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(MANIFEST_PATH, "w") as fh:
        json.dump(manifest, fh, indent=2)

    print("✅ Coordination manifest updated!")
    print(f"   Topic codes: {len(all_codes)}")
    print(f"   Total questions: {q_total:,}")
    print(f"   Remaining to target: {50000 - q_total:,}")
    print()
    print("📊 By subject:")
    for subj in sorted(subject_counts.keys()):
        print(f"   {subj:<30} {subject_counts[subj]:>6,} questions")


if __name__ == "__main__":
    main()
