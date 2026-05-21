#!/usr/bin/env python3
"""
migrate_topic_codes_db.py
=========================
Updates topic_code on existing quiz_questions rows in the production DB
to match the canonical taxonomy, using the same TOPIC_CODE_MAP that
normalize_topic_codes.py applies to seed JSON files.

Reads PRODUCTION_DB_URL from backend/.env.local (never committed to git).

Usage:
    python3 backend/scripts/migrate_topic_codes_db.py [--dry-run] [--stats]
"""
import argparse
import os
import sys
from collections import defaultdict

import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.topic_code_map import TOPIC_CODE_MAP

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env.local")
load_dotenv(ENV_PATH)


def get_conn():
    url = os.environ.get("PRODUCTION_DB_URL")
    if not url:
        sys.exit("ERROR: PRODUCTION_DB_URL not found in backend/.env.local")
    return psycopg2.connect(url)


def run_migration(dry_run: bool = False, stats: bool = False):
    conn = get_conn()
    cur = conn.cursor()

    # Fetch all distinct non-canonical topic_codes present in the table
    cur.execute("SELECT topic_code, COUNT(*) FROM quiz_questions GROUP BY topic_code ORDER BY topic_code")
    rows = cur.fetchall()

    updates: dict[str, list[str, int]] = {}  # old_code → (new_code, count)
    skipped_codes: dict[str, int] = {}

    for old_code, count in rows:
        if not old_code:
            continue
        new_code = TOPIC_CODE_MAP.get(old_code)
        if new_code and new_code != old_code:
            updates[old_code] = (new_code, count)
        else:
            skipped_codes[old_code] = count

    total_rows = sum(c for _, c in updates.values())

    if stats or dry_run:
        print(f"\n{'[DRY RUN] ' if dry_run else ''}DB migration stats:")
        print(f"  Distinct codes in DB:     {len(rows)}")
        print(f"  Codes needing remapping:  {len(updates)}")
        print(f"  Rows to be updated:       {total_rows:,}")
        print(f"  Codes already canonical:  {len(skipped_codes)}")
        print(f"\n  Remappings ({len(updates)}):")
        for old, (new, cnt) in sorted(updates.items(), key=lambda x: -x[1][1]):
            print(f"    {old:<55} → {new}  ({cnt} rows)")

    if not dry_run:
        updated_total = 0
        for old_code, (new_code, count) in updates.items():
            cur.execute(
                "UPDATE quiz_questions SET topic_code = %s WHERE topic_code = %s",
                (new_code, old_code),
            )
            updated_total += cur.rowcount
        conn.commit()
        print(f"\n✓ Committed {updated_total:,} row updates across {len(updates)} code remappings.")
    else:
        print(f"\n○ Dry run complete — no changes written.")

    cur.close()
    conn.close()
    return len(updates), total_rows


def main():
    parser = argparse.ArgumentParser(description="Migrate topic_codes in quiz_questions to canonical forms")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    parser.add_argument("--stats", action="store_true", help="Show detailed stats")
    args = parser.parse_args()

    run_migration(dry_run=args.dry_run, stats=args.stats or True)


if __name__ == "__main__":
    main()
