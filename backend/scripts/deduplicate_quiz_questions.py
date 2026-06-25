#!/usr/bin/env python3
"""
Deduplicates quiz_questions by normalized question_text.

For each group with identical text (case-insensitive, whitespace-collapsed):
  - Keeps the earliest created_at row (smallest UUID as tiebreaker)
  - Remaps quiz_attempts + flagged_questions to the kept ID in one SQL pass
  - Deletes duplicates in one SQL pass (CASCADE handles remaining FKs)

All three operations run inside a single transaction — zero partial commits.

Usage (from backend directory):
    DATABASE_URL=postgresql+asyncpg://... python scripts/deduplicate_quiz_questions.py
"""
import asyncio
import os
import re
import sys

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    sys.exit("ERROR: DATABASE_URL environment variable not set.")

DATABASE_URL = re.sub(r"^postgres://", "postgresql+asyncpg://", DATABASE_URL)
DATABASE_URL = re.sub(r"^postgresql://", "postgresql+asyncpg://", DATABASE_URL)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Normalization expression used consistently across all three queries.
# Window functions identify: rn=1 → kept, rn>1 → duplicate.
_NORM = r"lower(regexp_replace(trim(question_text), '\s+', ' ', 'g'))"
_RANK = f"ROW_NUMBER() OVER (PARTITION BY {_NORM} ORDER BY created_at ASC NULLS LAST, id ASC)"
_KEPT = f"FIRST_VALUE(id) OVER (PARTITION BY {_NORM} ORDER BY created_at ASC NULLS LAST, id ASC)"


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        before = (await db.execute(text("SELECT COUNT(*) FROM quiz_questions"))).scalar()
        print(f"Questions before : {before}")

        # Preview how many duplicates exist
        dup_info = (await db.execute(text(f"""
            SELECT COUNT(*) FROM (
                SELECT {_RANK} AS rn FROM quiz_questions
            ) t WHERE rn > 1
        """))).scalar()
        print(f"Duplicate rows   : {dup_info}")

        if not dup_info:
            print("Nothing to do.")
            return

        # Step 1: Remap quiz_attempts (server-side join — one round trip)
        print("Remapping quiz_attempts...")
        r1 = await db.execute(text(f"""
            WITH ranked AS (
                SELECT id, {_KEPT} AS kept_id, {_RANK} AS rn
                FROM quiz_questions
            ),
            dupes AS (SELECT id AS dupe_id, kept_id FROM ranked WHERE rn > 1)
            UPDATE quiz_attempts
            SET question_id = dupes.kept_id
            FROM dupes
            WHERE quiz_attempts.question_id = dupes.dupe_id
        """))
        print(f"  quiz_attempts remapped : {r1.rowcount}")

        # Step 2: Remap flagged_questions (stored as text UUID, no FK) — skip if table absent
        flagged_exists = (await db.execute(text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='flagged_questions')"
        ))).scalar()
        if flagged_exists:
            print("Remapping flagged_questions...")
            r2 = await db.execute(text(f"""
                WITH ranked AS (
                    SELECT id, {_KEPT} AS kept_id, {_RANK} AS rn
                    FROM quiz_questions
                ),
                dupes AS (SELECT id::text AS dupe_id, kept_id::text AS kept_id FROM ranked WHERE rn > 1)
                UPDATE flagged_questions
                SET question_id = dupes.kept_id
                FROM dupes
                WHERE flagged_questions.question_id = dupes.dupe_id
                  AND flagged_questions.question_source IN ('quiz', 'pyq')
            """))
            print(f"  flagged_questions remapped : {r2.rowcount}")
        else:
            print("Skipping flagged_questions (table not in prod yet)")

        # Step 3: Delete duplicates (CASCADE removes any remaining FK references)
        print("Deleting duplicates...")
        r3 = await db.execute(text(f"""
            WITH ranked AS (
                SELECT id, {_RANK} AS rn FROM quiz_questions
            )
            DELETE FROM quiz_questions
            WHERE id IN (SELECT id FROM ranked WHERE rn > 1)
        """))
        print(f"  Deleted : {r3.rowcount} rows")

        await db.commit()

        after = (await db.execute(text("SELECT COUNT(*) FROM quiz_questions"))).scalar()
        print(f"\nQuestions after  : {after}")
        print(f"Net reduction    : {before - after}")
        print("Done.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
