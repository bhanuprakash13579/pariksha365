#!/usr/bin/env python3
"""
Deduplicates quiz_questions by normalized question_text.

For each group of questions with identical text (case-insensitive, whitespace-collapsed):
  - Keeps the earliest created_at row (smallest UUID as tiebreaker)
  - Remaps quiz_attempts and flagged_questions from deleted IDs → kept ID
  - Deletes the duplicate rows (CASCADE cleans any remaining FKs)

Usage (from backend directory):
    DATABASE_URL=postgresql+asyncpg://... python scripts/deduplicate_quiz_questions.py

Or with an existing .env:
    source .env && python scripts/deduplicate_quiz_questions.py
"""
import asyncio
import os
import re
import sys
from collections import defaultdict

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    sys.exit("ERROR: DATABASE_URL environment variable not set.")

# Normalize to asyncpg driver
DATABASE_URL = re.sub(r"^postgres://", "postgresql+asyncpg://", DATABASE_URL)
DATABASE_URL = re.sub(r"^postgresql://", "postgresql+asyncpg://", DATABASE_URL)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


def _normalize(s: str) -> str:
    """Collapse whitespace and lowercase for comparison."""
    if not s:
        return ""
    return re.sub(r"\s+", " ", s.strip().lower())


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("Fetching all quiz questions...")
        rows = (await db.execute(
            text("SELECT id::text, question_text, created_at FROM quiz_questions ORDER BY created_at ASC NULLS LAST, id ASC")
        )).fetchall()
        print(f"Total questions in DB: {len(rows)}")

        # Group by normalized question_text; first entry per group = kept (earliest)
        groups: dict[str, list] = defaultdict(list)
        for row_id, question_text, created_at in rows:
            norm = _normalize(question_text or "")
            groups[norm].append(row_id)

        duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
        if not duplicate_groups:
            print("No duplicate questions found.")
            return

        total_to_delete = sum(len(v) - 1 for v in duplicate_groups.values())
        print(f"Found {len(duplicate_groups)} duplicate groups → {total_to_delete} rows to delete\n")

        # Build remap: duplicate_id → kept_id
        remap: dict[str, str] = {}
        for norm, group in duplicate_groups.items():
            kept_id = group[0]
            for dupe_id in group[1:]:
                remap[dupe_id] = kept_id

        dupe_ids = list(remap.keys())

        # Remap quiz_attempts: point attempts on deleted questions to the kept question
        print(f"Remapping quiz_attempts ({len(dupe_ids)} duplicate IDs)...")
        remapped_attempts = 0
        for dupe_id, kept_id in remap.items():
            result = await db.execute(
                text("UPDATE quiz_attempts SET question_id = :kept::uuid WHERE question_id = :dupe::uuid"),
                {"kept": kept_id, "dupe": dupe_id}
            )
            remapped_attempts += result.rowcount

        # Remap flagged_questions (stored as plain string, no FK)
        print(f"Remapping flagged_questions...")
        remapped_flags = 0
        for dupe_id, kept_id in remap.items():
            result = await db.execute(
                text("""
                    UPDATE flagged_questions
                    SET question_id = :kept
                    WHERE question_id = :dupe
                      AND question_source IN ('quiz', 'pyq')
                """),
                {"kept": kept_id, "dupe": dupe_id}
            )
            remapped_flags += result.rowcount

        # Delete duplicates in batches of 100
        print(f"Deleting {len(dupe_ids)} duplicate questions...")
        deleted = 0
        batch_size = 100
        for i in range(0, len(dupe_ids), batch_size):
            batch = dupe_ids[i : i + batch_size]
            placeholders = ", ".join(f":id{j}" for j in range(len(batch)))
            params = {f"id{j}": bid for j, bid in enumerate(batch)}
            result = await db.execute(
                text(f"DELETE FROM quiz_questions WHERE id::text IN ({placeholders})"),
                params
            )
            deleted += result.rowcount
            print(f"  Deleted batch {i // batch_size + 1}: {result.rowcount} rows")

        await db.commit()

        print(f"\n--- Summary ---")
        print(f"  Duplicate groups found : {len(duplicate_groups)}")
        print(f"  Questions deleted      : {deleted}")
        print(f"  Attempts remapped      : {remapped_attempts}")
        print(f"  Flags remapped         : {remapped_flags}")

        # Print a few examples of what was deduped
        print("\nSample groups (kept → deleted):")
        for norm, group in list(duplicate_groups.items())[:8]:
            preview = norm[:80] + ("..." if len(norm) > 80 else "")
            print(f"  kept={group[0]}  ({len(group)-1} duplicate{'s' if len(group)-1>1 else ''} removed)")
            print(f"  text: {preview}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
