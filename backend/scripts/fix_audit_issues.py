"""Fix the 13 logic mismatch issues identified in the Gemini audit report.

Fixes:
  1–4. QNT_AGES.json Q12/15/16/17: correct_letter D→A
  5.   QA_SURDS_B2.json Q9: explanation "D is correct" → "B is correct"
  6.   QNT_AGES_III_MIXED.json Q19: correct_letter C→D
  7.   QNT_RATIO_PROPORTION.json Q19: correct_letter A→D + fix stem wording
  8.   QNT_SHORTCUT_NUMBER_SYSTEM.json Q18: correct_letter A→D
  9–11. QNT_PARTNERSHIP.json Q9/13/16: correct_letter D→A
  12. QNT_RACES_GAMES_MIXED.json Q20: correct_letter B→A
  13. QA_RATIO_ADV_B2.json Q6: fix stem (206→126) + explanation

Also converts deprecated string-array options to v2 format in all affected files.

Usage:
    python3 -m scripts.fix_audit_issues [--dry-run] [--skip-db]
"""
from __future__ import annotations
import argparse
import json
import os
import uuid
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
SEEDS_ROOT = Path(__file__).resolve().parent.parent / "seeds" / "static_gk" / "quant"
_NS_QUIZ_Q = uuid.UUID("11111111-0000-0000-0000-000000000004")

def _qid_to_uuid(qid: str) -> str:
    return str(uuid.uuid5(_NS_QUIZ_Q, qid))

# ── CORRECTIONS REGISTRY ─────────────────────────────────────────────────────
# Each entry: (seed_file, question_id_or_idx, new_correct_letter, explanation_fix, stem_fix)
# explanation_fix: (old_text, new_text) or None
# stem_fix: (old_text, new_text) or None

CORRECTIONS = [
    # 1. Ages Q12 — oldest age is 9×4=36=option A, not D
    {
        "file": "QNT_AGES.json",
        "qid": "sgk_QNT_AGES_00012",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation calculates 36 (opt A), but correct_letter was D",
    },
    # 2. Ages Q15 — son's age=12=option A, not D
    {
        "file": "QNT_AGES.json",
        "qid": "sgk_QNT_AGES_00015",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation calculates S=12 (opt A), but correct_letter was D",
    },
    # 3. Ages Q16 — Asha=8=option A, not D
    {
        "file": "QNT_AGES.json",
        "qid": "sgk_QNT_AGES_00016",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation calculates Asha=8 (opt A), but correct_letter was D",
    },
    # 4. Ages Q17 — average 4 years ago=25=option A, not D
    {
        "file": "QNT_AGES.json",
        "qid": "sgk_QNT_AGES_00017",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation calculates avg=25 (opt A), but correct_letter was D",
    },
    # 5. Surds Q9 — explanation says 'D is correct' but answer is sqrt(29)=opt B
    {
        "file": "QA_SURDS_B2.json",
        "qid": None,  # Will use index 8
        "qidx": 8,
        "new_correct_letter": "B",  # Already correct, but fix explanation text
        "expl_fix": ("D is correct. √(3+x) = 4", "B is correct. √(3+x) = 4"),
        "stem_fix": None,
        "note": "Explanation starts with 'D is correct' but computes sqrt(29)=opt B",
    },
    # 6. Ages III Q19 — son's age=10=option D, not C
    {
        "file": "QNT_AGES_III_MIXED.json",
        "qid": "sgk_QNT_AGES_III_MIXED_00019",
        "new_correct_letter": "D",
        "expl_fix": ("Pick option D", "Option D (10 years) is correct."),
        "stem_fix": None,
        "note": "Explanation calculates s=10 (opt D), but correct_letter was C",
    },
    # 7. Ratio Proportion Q19 — total=7500=option D; P gets 1500 LESS (stem said MORE)
    {
        "file": "QNT_RATIO_PROPORTION.json",
        "qid": "sgk_QNT_RATIO_PROPORTION_00019",
        "new_correct_letter": "D",
        "expl_fix": None,
        "stem_fix": (
            "If P gets Rs 1500 more than he would if divided equally",
            "If P gets Rs 1500 less than he would if divided equally",
        ),
        "note": "P gets 3/10<1/2 so he gets LESS with 3:7. Total=7500=opt D; was A",
    },
    # 8. Number System Q18 — 4^100+5^100 mod 7=6=option D, not A
    {
        "file": "QNT_SHORTCUT_NUMBER_SYSTEM.json",
        "qid": "sgk_QNT_SHORTCUT_NUMBER_SYSTEM_00018",
        "new_correct_letter": "D",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation shows sum mod 7=6 (opt D); correct_letter was A",
    },
    # 9. Partnership Q9 — A-C difference=6000=option A, not D
    {
        "file": "QNT_PARTNERSHIP.json",
        "qid": "sgk_QNT_PARTNERSHIP_00009",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation calculates diff=6000 (opt A); correct_letter was D",
    },
    # 10. Partnership Q13 — total profit=800=option A, not D
    {
        "file": "QNT_PARTNERSHIP.json",
        "qid": "sgk_QNT_PARTNERSHIP_00013",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation: T=800 (opt A); correct_letter was D",
    },
    # 11. Partnership Q16 — total profit=4200=option A, not D
    {
        "file": "QNT_PARTNERSHIP.json",
        "qid": "sgk_QNT_PARTNERSHIP_00016",
        "new_correct_letter": "A",
        "expl_fix": None,
        "stem_fix": None,
        "note": "Explanation: Total=4200 (opt A); correct_letter was D",
    },
    # 12. Races Q20 — A beats C by 720m=option A, not B
    {
        "file": "QNT_RACES_GAMES_MIXED.json",
        "qid": "sgk_QNT_RACES_GAMES_MIXED_00020",
        "new_correct_letter": "A",
        "expl_fix": (
            "A beats C by 2000 − 1280 = 720 m. Hmm — 720 is option A. Let me verif",
            "A beats C by 2000 − 1280 = 720 m. Option A (720 m) is correct.",
        ),
        "stem_fix": None,
        "note": "Explanation computes 720m=opt A; correct_letter was B",
    },
    # 13. Ratio Adv Q6 — stem has wrong total (206→126); with 126, 50p coins=108=opt D
    {
        "file": "QA_RATIO_ADV_B2.json",
        "qid": None,
        "qidx": 5,  # Q6 is index 5
        "new_correct_letter": "D",
        "expl_fix": (
            "10.5x = 206. x = 206/10.5 ≈ 19.62. This doesn't give an integer, indicating the total ₹206 has a rounding issue. If total were ₹210: 10.5x=210→x=20; 50p coins=9×20=180. For exam purposes with ₹206: the closest answer among",
            "10.5x = 126 → x = 12. 50 paise coins = 9 × 12 = 108. Option D is correct.",
        ),
        "stem_fix": ("₹206", "₹126"),
        "note": "Stem had ₹206 (non-integer x); fix to ₹126 so x=12, 50p coins=108=opt D",
    },
]


def fix_question_in_file(path: Path, correction: dict, dry_run: bool) -> dict:
    """Apply a correction to a seed JSON file. Returns info about what was changed."""
    data = json.loads(path.read_text())
    is_dict = isinstance(data, dict)
    questions = data.get("questions", []) if is_dict else data

    qid = correction.get("qid")
    qidx = correction.get("qidx")
    new_cl = correction["new_correct_letter"]
    expl_fix = correction.get("expl_fix")
    stem_fix = correction.get("stem_fix")

    changed = False
    target_q = None

    for i, q in enumerate(questions):
        q_id = q.get("id")
        if qid and q_id == qid:
            target_q = q
            break
        elif qidx is not None and i == qidx:
            target_q = q
            break

    if target_q is None:
        return {"status": "NOT_FOUND", "file": str(path), "qid": qid or f"idx={qidx}"}

    old_cl = target_q.get("correct_letter")
    info = {"file": str(path), "qid": qid or f"idx={qidx}", "changes": []}

    # 1. Fix correct_letter
    if old_cl != new_cl:
        if not dry_run:
            target_q["correct_letter"] = new_cl
        info["changes"].append(f"correct_letter: {old_cl} → {new_cl}")
        changed = True

    # 2. Fix is_correct flags in options (for both string and object formats)
    opts = target_q.get("options", [])
    correct_idx = ord(new_cl) - ord("A")
    new_options = []
    opts_changed = False
    for j, o in enumerate(opts):
        if isinstance(o, str):
            new_options.append({"option_text": o, "is_correct": (j == correct_idx)})
            opts_changed = True
        else:
            expect_correct = (j == correct_idx)
            if o.get("is_correct", False) != expect_correct:
                new_options.append({**o, "is_correct": expect_correct})
                opts_changed = True
            else:
                new_options.append(o)
    if opts_changed:
        if not dry_run:
            target_q["options"] = new_options
        info["changes"].append("is_correct flags updated in options")
        changed = True

    # 3. Fix explanation text
    if expl_fix:
        old_text, new_text = expl_fix
        expl = target_q.get("explanation", "")
        if old_text in expl:
            if not dry_run:
                target_q["explanation"] = expl.replace(old_text, new_text, 1)
            info["changes"].append(f"explanation: replaced '{old_text[:40]}...'")
            changed = True

    # 4. Fix stem text
    if stem_fix:
        old_text, new_text = stem_fix
        stem = target_q.get("stem", "")
        if old_text in stem:
            if not dry_run:
                target_q["stem"] = stem.replace(old_text, new_text, 1)
            info["changes"].append(f"stem: replaced '{old_text[:40]}'")
            changed = True

    if changed and not dry_run:
        if is_dict:
            data["questions"] = questions
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            path.write_text(json.dumps(questions, ensure_ascii=False, indent=2))

    info["status"] = "CHANGED" if changed else "NO_CHANGE"
    return info


def convert_deprecated_schema_file(path: Path, dry_run: bool) -> dict:
    """Convert string-array options to {option_text, is_correct} format."""
    data = json.loads(path.read_text())
    is_dict = isinstance(data, dict)
    questions = data.get("questions", []) if is_dict else data

    n_converted = 0
    for q in questions:
        opts = q.get("options", [])
        if not opts or not isinstance(opts[0], str):
            continue
        cl = (q.get("correct_letter") or "").strip().upper()
        correct_idx = ord(cl) - ord("A") if cl and cl in "ABCD" else -1
        new_opts = [
            {"option_text": o, "is_correct": (i == correct_idx)}
            for i, o in enumerate(opts)
        ]
        if not dry_run:
            q["options"] = new_opts
        n_converted += 1

    if n_converted > 0 and not dry_run:
        if is_dict:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            path.write_text(json.dumps(questions, ensure_ascii=False, indent=2))

    return {"file": str(path), "converted": n_converted}


def update_prod_db(corrections: list, dry_run: bool) -> None:
    """Update quiz_questions table in prod DB for the corrected questions."""
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 not available — skipping DB update")
        return

    # Load .env.local for PRODUCTION_DB_URL
    env_path = Path(__file__).resolve().parent.parent / ".env.local"
    db_url = None
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("PRODUCTION_DB_URL="):
                db_url = line.split("=", 1)[1].strip()
                break
    if not db_url:
        db_url = os.getenv("PRODUCTION_DB_URL")
    if not db_url:
        print("PRODUCTION_DB_URL not found — skipping DB update")
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    for corr in corrections:
        qid = corr.get("qid")
        if not qid:
            print(f"  Skipping DB update for {corr['file']} idx={corr.get('qidx')} (no ID)")
            continue

        row_uuid = _qid_to_uuid(qid)
        new_cl = corr["new_correct_letter"]
        correct_idx = ord(new_cl) - ord("A")

        # Fetch current row
        cur.execute(
            "SELECT id, options, explanation FROM quiz_questions WHERE id = %s",
            (row_uuid,),
        )
        row = cur.fetchone()
        if not row:
            print(f"  NOT IN DB: {qid} (uuid={row_uuid})")
            continue

        _, old_opts, old_expl = row

        # Fix is_correct flags
        if isinstance(old_opts, list):
            new_opts = []
            for i, o in enumerate(old_opts):
                if isinstance(o, dict):
                    new_opts.append({**o, "is_correct": (i == correct_idx)})
                else:
                    new_opts.append(o)
        else:
            new_opts = old_opts

        # Fix explanation text
        new_expl = old_expl
        expl_fix = corr.get("expl_fix")
        if expl_fix and old_expl:
            old_text, new_text = expl_fix
            if old_text in old_expl:
                new_expl = old_expl.replace(old_text, new_text, 1)

        # Fix stem (question_text)
        new_stem = None
        stem_fix = corr.get("stem_fix")
        if stem_fix:
            cur.execute("SELECT question_text FROM quiz_questions WHERE id = %s", (row_uuid,))
            stem_row = cur.fetchone()
            if stem_row:
                old_stem = stem_row[0] or ""
                old_text, new_text = stem_fix
                if old_text in old_stem:
                    new_stem = old_stem.replace(old_text, new_text, 1)

        if dry_run:
            print(f"  [DRY RUN] Would update {qid} (uuid={row_uuid})")
            print(f"    new correct_idx={correct_idx}, expl_changed={new_expl != old_expl}")
            continue

        if new_stem:
            cur.execute(
                "UPDATE quiz_questions SET options=%s, explanation=%s, question_text=%s WHERE id=%s",
                (json.dumps(new_opts), new_expl, new_stem, row_uuid),
            )
        else:
            cur.execute(
                "UPDATE quiz_questions SET options=%s, explanation=%s WHERE id=%s",
                (json.dumps(new_opts), new_expl, row_uuid),
            )
        print(f"  UPDATED {qid} (uuid={row_uuid}), new_correct={new_cl}")

    if not dry_run:
        conn.commit()
        print("  DB commit done.")
    cur.close()
    conn.close()


def main():
    ap = argparse.ArgumentParser(description="Fix audit-identified seed file and DB issues")
    ap.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    ap.add_argument("--skip-db", action="store_true", help="Skip prod DB updates")
    ap.add_argument("--skip-schema-convert", action="store_true", help="Skip deprecated schema conversion")
    args = ap.parse_args()

    print(f"=== Fix Audit Issues {'[DRY RUN]' if args.dry_run else '[LIVE]'} ===\n")

    # ── Phase 1: Apply logic mismatch corrections ──────────────────────────
    print("Phase 1: Logic mismatch fixes")
    for corr in CORRECTIONS:
        path = SEEDS_ROOT / corr["file"]
        if not path.exists():
            print(f"  NOT FOUND: {corr['file']}")
            continue
        result = fix_question_in_file(path, corr, args.dry_run)
        status = result["status"]
        changes = result.get("changes", [])
        note = corr.get("note", "")
        q_label = corr.get("qid") or f"idx={corr.get('qidx')}"
        print(f"  [{status}] {corr['file']} | {q_label}")
        if changes:
            for c in changes:
                print(f"    - {c}")
        if status == "NOT_FOUND":
            print(f"    NOTE: {note}")

    # ── Phase 2: Convert deprecated schema files ───────────────────────────
    if not args.skip_schema_convert:
        print("\nPhase 2: Converting deprecated string-array options to v2 schema")
        DEPRECATED_FILES = [
            "QNT_PERCENTAGE_VIII_MIXED.json",
            "QNT_PIPES_CISTERNS_VII_MIXED.json",
            "QNT_PIPES_CISTERNS_VIII_MIXED.json",
            "QNT_BOATS_STREAMS_V_MIXED.json",
            "QNT_INTEREST_MIXED.json",
            "QNT_TIME_WORK_VII_MIXED.json",
            "QNT_PERMUTATION_COMBINATION_III_MIXED.json",
            "QNT_PROBABILITY_IV_MIXED.json",
            "QNT_PROFIT_LOSS_IX_MIXED.json",
            "QNT_NUMBER_SYSTEM_VII_MIXED.json",
            "QNT_MIXTURE_ALLIGATION_VIII_MIXED.json",
            "QNT_TRAINS_V_MIXED.json",
            "QNT_PROFIT_LOSS_IV_MIXED.json",
            "QNT_NUMBER_SYSTEM_VI_MIXED.json",
            "QNT_TIME_SPEED_DISTANCE_VI_MIXED.json",
            "QNT_MENSURATION_V_MIXED.json",
            "QNT_PERCENTAGE_IX_MIXED.json",
            "QNT_COMPOUND_INTEREST_VI_MIXED.json",
            "QNT_RATIO_PROPORTION_IX_MIXED.json",
            "QNT_SIMPLE_INTEREST_VI_MIXED.json",
            "QNT_PARTNERSHIP_VIII_MIXED.json",
            "QNT_TRIGONOMETRY_III_MIXED.json",
            "QNT_PROFIT_LOSS_VII_MIXED.json",
            "QNT_PIPES_CISTERNS_IX_MIXED.json",
            "QNT_COMPOUND_INTEREST_V_MIXED.json",
            "QNT_GEOMETRY_TRIANGLES_III_MIXED.json",
            "QNT_SIMPLE_INTEREST_V_MIXED.json",
            "QNT_ALGEBRA_III_MIXED.json",
            "QNT_TIME_WORK_VI_MIXED.json",
            "QNT_AVERAGES_VI_MIXED.json",
            "QNT_TIME_SPEED_DISTANCE_VIII_MIXED.json",
            "QNT_AVERAGES_MIXED.json",
            "QNT_TIME_SPEED_DISTANCE_VII_MIXED.json",
            "QNT_TRAINS_VI_MIXED.json",
            "QNT_TRAINS_PROG_e61c45c8.json",
        ]
        total_converted = 0
        for fname in DEPRECATED_FILES:
            path = SEEDS_ROOT / fname
            if not path.exists():
                continue
            result = convert_deprecated_schema_file(path, args.dry_run)
            n = result["converted"]
            if n > 0:
                total_converted += n
                print(f"  {'[DRY RUN] Would convert' if args.dry_run else 'Converted'} {n} questions in {fname}")
        print(f"  Total: {total_converted} questions converted")

    # ── Phase 3: Update prod DB ─────────────────────────────────────────────
    if not args.skip_db:
        print("\nPhase 3: Updating prod DB")
        update_prod_db(CORRECTIONS, args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
