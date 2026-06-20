#!/usr/bin/env python3
"""Seed the SSC CGL AAO Paper III question bank into the private_modules universe.

Idempotent:
  * creates the ``ssc-cgl-aao-paper3`` module row if absent,
  * replaces ALL questions on every run (delete-then-insert),
  * does NOT grant access — manage whitelist exclusively via admin panel.

Structure:
  Each question's ``section`` field corresponds to a milestone chapter group.
  Students unlock milestone-based practice as they study chapter by chapter.

  Milestone 1  — Accounting Basics         (Part 0 + Ch 1-2)
  Milestone 2  — Verification & Bills      (Ch 3)
  Milestone 3  — Final Accounts            (Ch 4)
  Milestone 4  — Assets & Inventory        (Ch 5)
  Milestone 5a — NPO & Self-Balancing      (Ch 6)
  Milestone 5b — CAG & Finance Commission  (Ch 7)
  Milestone 6  — Micro Economics           (Ch 8-9)
  Milestone 7  — Production & Markets      (Ch 10-11)
  Milestone 8  — Indian Economy & Reforms  (Ch 12-13)
  Milestone 9  — Money, Banking & Fiscal   (Ch 14-15)
  Milestone 10 — IT in Governance          (Ch 16) — Full Paper Ready

Usage:
    cd /home/bhanu/Desktop/pariksha365
    python3 backend/scripts/seed_aao_module.py [--json PATH]
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models.private_module import (
    PrivateModule, PrivateModuleQuestion, PrivateModuleAccess,
)

MODULE_SLUG = "ssc-cgl-aao-paper3"
MODULE_NAME = "SSC CGL AAO — Paper III (Finance & Economics)"
MODULE_DESC = (
    "Exhaustive MCQ bank for SSC CGL Tier 2 Paper III (AAO). "
    "Covers all 16 chapters: Part A — Finance & Accounts (Ch 0–7: "
    "GAAP, Double Entry, BRS, Final Accounts, Depreciation, Inventory, "
    "NPO, CAG, Finance Commission) and Part B — Economics & Governance "
    "(Ch 8–16: Demand-Supply, Costs, Market Forms, Indian Economy, "
    "Reforms, Money & Banking, Fiscal Policy, Budget, BoP, GST, "
    "e-Governance, Digital India). "
    "Practice milestone-by-milestone: each section unlocks after completing "
    "the corresponding chapters. Paper III = 100 Qs / 200 marks / 120 mins. "
    "Calculator allowed. Negative marking: −0.5."
)


async def upsert_module(db: AsyncSession) -> PrivateModule:
    stmt = select(PrivateModule).where(PrivateModule.slug == MODULE_SLUG)
    m = (await db.execute(stmt)).scalars().first()
    if m is None:
        m = PrivateModule(
            slug=MODULE_SLUG,
            name=MODULE_NAME,
            description=MODULE_DESC,
            is_active=True,
        )
        db.add(m)
        await db.commit()
        await db.refresh(m)
        print(f"[seed] Created module '{MODULE_SLUG}' id={m.id}")
    else:
        m.name = MODULE_NAME
        m.description = MODULE_DESC
        m.is_active = True
        await db.commit()
        print(f"[seed] Updated module '{MODULE_SLUG}' id={m.id}")
    return m


async def replace_questions(db: AsyncSession, module: PrivateModule, data: list[dict]) -> int:
    await db.execute(
        delete(PrivateModuleQuestion).where(PrivateModuleQuestion.module_id == module.id)
    )
    await db.commit()

    rows = []
    for q in data:
        difficulty = (q.get("difficulty") or "MEDIUM").upper()
        if difficulty not in {"EASY", "MEDIUM", "HARD"}:
            difficulty = "MEDIUM"

        # Derive correct_letter from options if not explicitly set
        correct_letter = q.get("correct_letter")
        if not correct_letter:
            letters = "ABCD"
            for idx, opt in enumerate(q.get("options", [])):
                if opt.get("is_correct"):
                    correct_letter = letters[idx]
                    break
            correct_letter = correct_letter or "A"

        rows.append(PrivateModuleQuestion(
            module_id=module.id,
            qnum=q.get("qnum"),
            section=q.get("section") or "",
            subject=q.get("subject") or "Finance & Accounts",
            topic=q.get("topic") or "",
            topic_code=q.get("topic_code") or "AAO_GENERAL",
            difficulty=difficulty,
            question_text=q.get("stem") or q.get("question_text") or "",
            options=q.get("options") or [],
            explanation=q.get("explanation") or "",
        ))

    db.add_all(rows)
    await db.commit()

    sections: dict[str, int] = {}
    for q in data:
        s = q.get("section") or "Unknown"
        sections[s] = sections.get(s, 0) + 1
    print(f"[seed] Inserted {len(rows)} questions across {len(sections)} milestones:")
    for s, c in sections.items():
        print(f"         {c:4d}  {s}")
    return len(rows)


async def grant_access(db: AsyncSession, module: PrivateModule, emails: list[str]) -> None:
    for raw in emails:
        email = raw.strip().lower()
        if not email or "@" not in email:
            continue
        existing = (await db.execute(
            select(PrivateModuleAccess).where(
                PrivateModuleAccess.module_id == module.id,
                PrivateModuleAccess.email == email,
            )
        )).scalars().first()
        if existing:
            print(f"[seed] access already exists: {email}")
            continue
        db.add(PrivateModuleAccess(module_id=module.id, email=email, note="seed script"))
        await db.commit()
        print(f"[seed] granted access: {email}")


async def main():
    ap = argparse.ArgumentParser(description="Seed AAO Paper III private module")
    default_json = Path(__file__).resolve().parents[1] / "seeds" / "aao_paper3_bank.json"
    ap.add_argument("--json", default=os.environ.get("AAO_JSON", str(default_json)),
                    help="Path to aao_paper3_bank.json")
    ap.add_argument("--email", action="append", default=[],
                    help="Email to grant access (repeatable). Use admin panel instead.")
    args = ap.parse_args()

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"ERROR: {json_path} not found.")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    print(f"[seed] Loaded {len(data)} questions from {json_path.name}")

    async with SessionLocal() as db:
        module = await upsert_module(db)
        await replace_questions(db, module, data)
        if args.email:
            await grant_access(db, module, args.email)
        else:
            print("[seed] No --email passed. Grant access via Admin → Private Modules.")

    print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(main())
