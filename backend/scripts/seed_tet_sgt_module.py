#!/usr/bin/env python3
"""Seed the AP TET and AP DSC-SGT question banks into the private_modules universe.

Same email-gated pattern as EPFO APFC and SSC CGL AAO. Two modules:

    ap-dsc-sgt   AP DSC — SGT (Secondary Grade Teacher)   160 Q / 80 marks / 150 min
    ap-tet       AP TET (Teacher Eligibility Test)         150 Q / 150 marks / 150 min

Idempotent:
  * creates the module row if absent, else updates name/description,
  * replaces ALL questions for that module on every run (delete-then-insert),
  * does NOT grant access unless --email is passed (manage the whitelist in the
    Admin → Private Modules panel instead).

Chapters:
  Each question's ``section`` field is the CHAPTER a candidate drills. A student
  opens one exam section → one chapter → studies & practises only that chapter,
  never the whole syllabus at once (identical to the AAO milestone model). The
  ``subject`` field is the exam section (e.g. "Educational Psychology"); ``topic``
  / ``topic_code`` drive the module-scoped weak-topic engine.

Content lives as many small per-chapter JSON files under
    backend/seeds/private_modules/<ap_dsc_sgt|ap_tet>/*.json
so the banks can be filled chapter-by-chapter across generation waves. Every file
is a JSON list of question dicts (same shape as aao_paper3_bank.json).

Usage:
    cd /home/bhanu/Desktop/pariksha365
    python3 backend/scripts/seed_tet_sgt_module.py --module ap-dsc-sgt
    python3 backend/scripts/seed_tet_sgt_module.py --module ap-tet
    python3 backend/scripts/seed_tet_sgt_module.py --all
    python3 backend/scripts/seed_tet_sgt_module.py --all --email someone@example.com
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

SEEDS_ROOT = Path(__file__).resolve().parents[1] / "seeds" / "private_modules"

MODULES: dict[str, dict] = {
    "ap-dsc-sgt": {
        "dir": "ap_dsc_sgt",
        "name": "AP DSC — SGT (Secondary Grade Teacher)",
        "description": (
            "Chapter-by-chapter MCQ practice for the AP DSC SGT written test "
            "(160 Q · 80 marks · 150 min). Study one chapter at a time — Full-Mock "
            "has exactly-timed papers."
        ),
    },
    "ap-tet": {
        "dir": "ap_tet",
        "name": "AP TET (Teacher Eligibility Test)",
        "description": (
            "Chapter-by-chapter MCQ practice for AP TET (150 Q · 150 marks · "
            "150 min, no negative marking). Study one chapter at a time — "
            "Full-Mock has exactly-timed papers."
        ),
    },
}


def load_bank(module_dir: str) -> list[dict]:
    """Concatenate every *.json question list under the module's seed directory."""
    base = SEEDS_ROOT / module_dir
    if not base.exists():
        print(f"[seed] WARNING: {base} does not exist yet — no questions loaded.")
        return []
    data: list[dict] = []
    for jf in sorted(base.glob("*.json")):
        try:
            chunk = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[seed] ERROR reading {jf.name}: {e}")
            continue
        if isinstance(chunk, dict) and "questions" in chunk:
            chunk = chunk["questions"]
        if not isinstance(chunk, list):
            print(f"[seed] WARNING: {jf.name} is not a list — skipped.")
            continue
        data.extend(chunk)
        print(f"[seed]   {len(chunk):4d}  {jf.name}")
    return data


async def upsert_module(db: AsyncSession, slug: str, name: str, desc: str) -> PrivateModule:
    m = (await db.execute(
        select(PrivateModule).where(PrivateModule.slug == slug)
    )).scalars().first()
    if m is None:
        m = PrivateModule(slug=slug, name=name, description=desc, is_active=True)
        db.add(m)
        await db.commit()
        await db.refresh(m)
        print(f"[seed] Created module '{slug}' id={m.id}")
    else:
        m.name, m.description, m.is_active = name, desc, True
        await db.commit()
        print(f"[seed] Updated module '{slug}' id={m.id}")
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
        rows.append(PrivateModuleQuestion(
            module_id=module.id,
            qnum=q.get("qnum"),
            section=q.get("section") or "",
            subject=q.get("subject") or "",
            topic=q.get("topic") or "",
            topic_code=q.get("topic_code") or "TETSGT_GENERAL",
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
    print(f"[seed] Inserted {len(rows)} questions across {len(sections)} chapters:")
    for s, c in sorted(sections.items()):
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


async def seed_one(db: AsyncSession, slug: str, emails: list[str]) -> None:
    cfg = MODULES[slug]
    print(f"\n===== Seeding {slug} =====")
    data = load_bank(cfg["dir"])
    print(f"[seed] Loaded {len(data)} questions for {slug}")
    module = await upsert_module(db, slug, cfg["name"], cfg["description"])
    await replace_questions(db, module, data)
    if emails:
        await grant_access(db, module, emails)
    else:
        print("[seed] No --email passed. Grant access via Admin → Private Modules.")


async def main():
    ap = argparse.ArgumentParser(description="Seed AP TET / AP DSC-SGT private modules")
    ap.add_argument("--module", choices=list(MODULES.keys()),
                    help="Seed just this module")
    ap.add_argument("--all", action="store_true", help="Seed both modules")
    ap.add_argument("--email", action="append", default=[],
                    help="Email to grant access (repeatable). Prefer the admin panel.")
    args = ap.parse_args()

    if not args.module and not args.all:
        ap.error("pass --module <slug> or --all")

    slugs = list(MODULES.keys()) if args.all else [args.module]
    async with SessionLocal() as db:
        for slug in slugs:
            await seed_one(db, slug, args.email)
    print("\n[seed] Done.")


if __name__ == "__main__":
    asyncio.run(main())
