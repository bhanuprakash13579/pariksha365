#!/usr/bin/env python3
"""Combined integrity check for the AP TET / AP DSC-SGT private-module seed JSON.

Run after every content-authoring wave, before committing:

    python3 backend/scripts/verify_tet_sgt_seeds.py

Checks (all must pass):
  1. Per-question 4-check audit: exactly 4 options, exactly 1 marked
     is_correct, no duplicate option text, correct_letter (if present)
     points at the actual is_correct option.
  2. Per-module exact-duplicate-stem detection (same stem repeated within
     ap_dsc_sgt, or within ap_tet — cross-module repeats are fine, since
     the two modules are separate universes and some facts legitimately
     overlap). The generic stem "Choose the correct sentence:" is exempted
     since it's intentionally reused with different options each time.
  3. TET GK-scope scan: AP TET has NO General Knowledge & Current Affairs
     section per the official exam pattern. Any TET question whose
     `section` or `subject` field contains the string "general knowledge"
     is flagged — this catches the exact mistake made twice in the
     2026-07-20 session (once as a real GK file, once as a mislabeled
     EVS geography question).

Exits non-zero if any check fails.
"""
import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "seeds", "private_modules")
GENERIC_STEM_EXEMPTIONS = {"Choose the correct sentence:"}


def check_module(mod: str) -> int:
    issues = 0
    files = sorted(glob.glob(os.path.join(ROOT, mod, "*.json")))
    seen_stems: dict[str, str] = {}

    for path in files:
        fname = os.path.basename(path)
        data = json.loads(open(path, encoding="utf-8").read())
        for i, q in enumerate(data):
            opts = q.get("options", [])
            texts = [o.get("option_text", "") for o in opts]
            n_correct = sum(1 for o in opts if o.get("is_correct"))

            if len(opts) != 4 or n_correct != 1 or len(set(texts)) != len(texts):
                print(f"[FAIL] {mod}/{fname}#{i}: option-count={len(opts)} "
                      f"n_correct={n_correct} dup_options={len(texts) != len(set(texts))}")
                issues += 1

            letter = q.get("correct_letter")
            if letter:
                idx = "ABCD".index(letter)
                if idx >= len(opts) or not opts[idx].get("is_correct"):
                    print(f"[LETTER] {mod}/{fname}#{i}: correct_letter={letter} "
                          f"doesn't match is_correct option")
                    issues += 1

            if mod == "ap_tet":
                for key in ("section", "subject"):
                    val = (q.get(key) or "").lower()
                    if "general knowledge" in val:
                        print(f"[GK-SCOPE] {mod}/{fname}#{i}: {key}={q.get(key)!r} "
                              f"— TET has no GK section per official pattern")
                        issues += 1

            stem = (q.get("stem") or "").strip()
            if stem and stem not in GENERIC_STEM_EXEMPTIONS:
                if stem in seen_stems:
                    print(f"[DUP] {mod}: '{stem[:60]}' -- first={seen_stems[stem]} "
                          f"again={fname}#{i}")
                    issues += 1
                else:
                    seen_stems[stem] = f"{fname}#{i}"

    total = sum(len(json.loads(open(p, encoding='utf-8').read())) for p in files)
    print(f"{mod}: {total} Qs · {len(files)} files")
    return issues


def main() -> int:
    total_issues = 0
    for mod in ("ap_dsc_sgt", "ap_tet"):
        total_issues += check_module(mod)
    print(f"\nTOTAL issues: {total_issues}")
    if total_issues:
        print("FAILED — fix the issues above before committing.")
        return 1
    print("OK — all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
