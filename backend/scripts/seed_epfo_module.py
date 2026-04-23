#!/usr/bin/env python3
"""Seed the EPFO APFC question bank into the ``private_modules`` universe.

Idempotent:
  * creates the ``epfo-apfc`` module row if absent,
  * replaces all questions on every run (delete-then-insert for clean updates),
  * does NOT grant any access — whitelist management is handled exclusively via
    the admin panel so the authoritative list lives in the DB, not in source.

Usage:
    python3 backend/scripts/seed_epfo_module.py [--json PATH] [--email extra@x.com]*

The optional ``--email`` flag still exists as an escape hatch (e.g. rehydrating
access after a DB wipe), but production flow is: run the seed, then whitelist
emails from Admin → Private Modules.
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Allow running from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.models.private_module import (  # noqa: E402
    PrivateModule, PrivateModuleQuestion, PrivateModuleAccess,
)


MODULE_SLUG = "epfo-apfc"
MODULE_NAME = "EPFO APFC MCQ Bank"
MODULE_DESC = (
    "~2000 exam-style MCQs across 15 subject areas — EPF Act, EPS, EDLI, "
    "SS Code 2020, Labour Laws, Economy, Polity, Accounting, History, "
    "Science, Current Affairs, Geography and more. Isolated practice: "
    "wrong answers only surface follow-ups from the EPFO bank itself."
)


async def upsert_module(db: AsyncSession) -> PrivateModule:
    stmt = select(PrivateModule).where(PrivateModule.slug == MODULE_SLUG)
    m = (await db.execute(stmt)).scalars().first()
    if m is None:
        m = PrivateModule(slug=MODULE_SLUG, name=MODULE_NAME, description=MODULE_DESC,
                          is_active=True)
        db.add(m)
        await db.commit()
        await db.refresh(m)
        print(f"[seed] Created module {MODULE_SLUG} id={m.id}")
    else:
        m.name = MODULE_NAME
        m.description = MODULE_DESC
        m.is_active = True
        await db.commit()
        print(f"[seed] Updated module {MODULE_SLUG} id={m.id}")
    return m


async def replace_questions(db: AsyncSession, module: PrivateModule, data: list[dict]) -> int:
    await db.execute(delete(PrivateModuleQuestion)
                     .where(PrivateModuleQuestion.module_id == module.id))
    await db.commit()

    rows = []
    for q in data:
        rows.append(PrivateModuleQuestion(
            module_id=module.id,
            qnum=q.get("qnum"),
            section=q.get("section"),
            subject=q["subject"],
            topic=q["topic"],
            topic_code=q["topic_code"],
            difficulty="MEDIUM",
            question_text=q["stem"],
            options=q["options"],
            explanation=q.get("explanation") or "",
        ))
    db.add_all(rows)
    await db.commit()
    print(f"[seed] Inserted {len(rows)} questions")
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
        db.add(PrivateModuleAccess(module_id=module.id, email=email,
                                   note="seed script"))
        await db.commit()
        print(f"[seed] granted access: {email}")


async def main():
    ap = argparse.ArgumentParser()
    default_json = Path(__file__).resolve().parents[1] / "seeds" / "epfo_apfc_bank.json"
    ap.add_argument("--json", default=os.environ.get("EPFO_JSON", str(default_json)),
                    help="Path to the classified questions JSON file.")
    ap.add_argument("--email", action="append", default=[],
                    help="Extra email to grant access to (may be repeated).")
    args = ap.parse_args()

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"ERROR: {json_path} not found. Run /tmp/parse_epfo_pdf.py then "
              f"/tmp/classify_epfo.py first.")
        sys.exit(1)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    print(f"[seed] Loaded {len(data)} questions from {json_path}")

    async with SessionLocal() as db:
        module = await upsert_module(db)
        await replace_questions(db, module, data)
        if args.email:
            await grant_access(db, module, args.email)
        else:
            print("[seed] no --email passed; manage access from the admin panel.")

    print("[seed] done.")


if __name__ == "__main__":
    asyncio.run(main())
