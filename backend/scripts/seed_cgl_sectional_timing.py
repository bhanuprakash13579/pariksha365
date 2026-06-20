"""
Migration: Split SSC CGL Tier 1 "Full Paper" sections into 4 subject sections
and enable has_sectional_timing=True.

SSC CGL Tier 1 structure:
  Q1-25:   General Intelligence & Reasoning  (15 min)
  Q26-50:  General Awareness                 (15 min)
  Q51-75:  Quantitative Aptitude             (15 min)
  Q76-100: English Comprehension             (15 min)
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

TIER1_SECTIONS = [
    (1,  25,  "General Intelligence & Reasoning", 15, 1),
    (26, 50,  "General Awareness",                15, 2),
    (51, 75,  "Quantitative Aptitude",            15, 3),
    (76, 999, "English Comprehension",            15, 4),  # 999 catches any >100 edge cases
]


async def migrate_test(ts_id, old_sec_id, mpq, title):
    async with engine.begin() as conn:
        new_sec_ids = {}
        for (start, end, name, dur, ord_num) in TIER1_SECTIONS:
            ins = await conn.execute(text("""
                INSERT INTO sections (id, test_series_id, name, time_limit_minutes,
                                     marks_per_question, order_num)
                VALUES (gen_random_uuid(), :ts_id, :name, :dur, :mpq, :ord_num)
                RETURNING id
            """), {"ts_id": ts_id, "name": name, "dur": dur, "mpq": mpq, "ord_num": ord_num})
            new_sec_ids[(start, end)] = ins.fetchone()[0]

        # Bulk-update questions by range (4 queries instead of 100)
        for (start, end, _name, _dur, _ord) in TIER1_SECTIONS:
            await conn.execute(text("""
                UPDATE questions
                SET section_id = :new_sec_id
                WHERE section_id = :old_sec_id
                  AND order_num BETWEEN :start AND :end
            """), {
                "new_sec_id": new_sec_ids[(start, end)],
                "old_sec_id": old_sec_id,
                "start": start,
                "end": end,
            })

        # Catch any questions with order_num = NULL or unexpected values → English section
        await conn.execute(text("""
            UPDATE questions
            SET section_id = :english_sec_id
            WHERE section_id = :old_sec_id
        """), {"english_sec_id": new_sec_ids[(76, 999)], "old_sec_id": old_sec_id})

        await conn.execute(text("DELETE FROM sections WHERE id = :sec_id"), {"sec_id": old_sec_id})
        await conn.execute(text("""
            UPDATE test_series SET has_sectional_timing = TRUE WHERE id = :ts_id
        """), {"ts_id": ts_id})

    print(f"  done: {title[:65]}")


async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("""
            SELECT ts.id, ts.title, sec.id as sec_id, sec.marks_per_question
            FROM test_series ts
            JOIN sections sec ON sec.test_series_id = ts.id
            JOIN exam_stages es ON es.id = ts.exam_stage_id
            JOIN subcategories sc ON sc.id = es.subcategory_id
            JOIN categories c ON c.id = sc.category_id
            WHERE c.name ILIKE '%ssc%' AND sc.name = 'CGL' AND es.name = 'Tier 1'
              AND sec.name = 'Full Paper'
            ORDER BY ts.title
        """))
        tests = [dict(row._mapping) for row in res.fetchall()]

    print(f"Found {len(tests)} SSC CGL Tier 1 papers to restructure")
    print()

    for t in tests:
        await migrate_test(t["id"], t["sec_id"], t["marks_per_question"], t["title"])

    print()
    print(f"All done. {len(tests)} papers restructured with 4-section timing.")

    # Verify
    async with engine.connect() as conn:
        vres = await conn.execute(text("""
            SELECT ts.title, COUNT(sec.id) as sec_count, ts.has_sectional_timing
            FROM test_series ts
            LEFT JOIN sections sec ON sec.test_series_id = ts.id
            JOIN exam_stages es ON es.id = ts.exam_stage_id
            JOIN subcategories sc ON sc.id = es.subcategory_id
            JOIN categories c ON c.id = sc.category_id
            WHERE c.name ILIKE '%ssc%' AND sc.name = 'CGL' AND es.name = 'Tier 1'
            GROUP BY ts.id, ts.title, ts.has_sectional_timing
            ORDER BY ts.title
            LIMIT 5
        """))
        print()
        print("Verification (first 5 papers):")
        for row in vres.fetchall():
            d = dict(row._mapping)
            print(f"  sectional={d['has_sectional_timing']} | sections={d['sec_count']} | {d['title'][:55]}")


if __name__ == "__main__":
    asyncio.run(run())
