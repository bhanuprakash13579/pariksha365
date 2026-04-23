"""Seed the EPFO APFC bank straight into the production DB.

Uses the same credential pattern as scripts/mock_gen/sync_dedup_index.py —
``PRODUCTION_DB_URL`` in ``backend/.env.local`` (gitignored). The URL is never
logged.

This script:
  * creates the 5 private_modules tables if they don't exist yet (idempotent
    DDL — matches the alembic migration 20260424_01);
  * upserts the ``epfo-apfc`` module;
  * replaces all its questions with the 1966 rows from
    ``backend/seeds/epfo_apfc_bank.json``;
  * does NOT grant any access by default — whitelist management is handled via
    the admin panel so the authoritative list lives in the DB, not in source.

Usage::

    python3 backend/scripts/seed_epfo_module_prod.py
    python3 backend/scripts/seed_epfo_module_prod.py --email teammate@gmail.com  # optional escape hatch
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid
from pathlib import Path

log = logging.getLogger("seed_epfo_prod")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


MODULE_SLUG = "epfo-apfc"
MODULE_NAME = "EPFO APFC MCQ Bank"
MODULE_DESC = (
    "~2000 exam-style MCQs across 15 subject areas — EPF Act, EPS, EDLI, "
    "SS Code 2020, Labour Laws, Economy, Polity, Accounting, History, "
    "Science, Current Affairs, Geography and more. Isolated practice: "
    "wrong answers only surface follow-ups from the EPFO bank itself."
)


def _load_env_local(env_path: Path) -> dict:
    out: dict = {}
    if not env_path.exists():
        return out
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _connect(url: str):
    try:
        import psycopg  # type: ignore
        return psycopg.connect(url)
    except ImportError:
        pass
    try:
        import psycopg2  # type: ignore
        return psycopg2.connect(url)
    except ImportError as e:
        raise RuntimeError(
            "Neither 'psycopg' nor 'psycopg2' is installed. "
            "Install one with: pip install psycopg[binary] "
            "or pip install psycopg2-binary"
        ) from e


DDL = """
CREATE TABLE IF NOT EXISTS private_modules (
    id UUID PRIMARY KEY,
    slug VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_private_modules_slug ON private_modules (slug);

CREATE TABLE IF NOT EXISTS private_module_questions (
    id UUID PRIMARY KEY,
    module_id UUID NOT NULL REFERENCES private_modules(id) ON DELETE CASCADE,
    qnum INTEGER,
    section VARCHAR,
    subject VARCHAR NOT NULL,
    topic VARCHAR NOT NULL,
    topic_code VARCHAR NOT NULL,
    difficulty VARCHAR NOT NULL DEFAULT 'MEDIUM',
    question_text TEXT NOT NULL,
    options JSON NOT NULL,
    explanation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_pmq_module_id ON private_module_questions (module_id);
CREATE INDEX IF NOT EXISTS ix_pmq_subject ON private_module_questions (subject);
CREATE INDEX IF NOT EXISTS ix_pmq_topic_code ON private_module_questions (topic_code);
CREATE INDEX IF NOT EXISTS ix_pmq_module_subject_topic
    ON private_module_questions (module_id, subject, topic_code);

CREATE TABLE IF NOT EXISTS private_module_access (
    id UUID PRIMARY KEY,
    module_id UUID NOT NULL REFERENCES private_modules(id) ON DELETE CASCADE,
    email VARCHAR NOT NULL,
    note VARCHAR,
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_private_module_access_module_email UNIQUE (module_id, email)
);
CREATE INDEX IF NOT EXISTS ix_pma_module_id ON private_module_access (module_id);
CREATE INDEX IF NOT EXISTS ix_pma_email ON private_module_access (email);

CREATE TABLE IF NOT EXISTS private_module_attempts (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES private_modules(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES private_module_questions(id) ON DELETE CASCADE,
    was_correct BOOLEAN NOT NULL DEFAULT FALSE,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_pmat_user_id ON private_module_attempts (user_id);
CREATE INDEX IF NOT EXISTS ix_pmat_module_id ON private_module_attempts (module_id);
CREATE INDEX IF NOT EXISTS ix_pmat_question_id ON private_module_attempts (question_id);

CREATE TABLE IF NOT EXISTS private_module_weak_topics (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES private_modules(id) ON DELETE CASCADE,
    subject VARCHAR NOT NULL,
    topic VARCHAR,
    topic_code VARCHAR NOT NULL,
    accuracy FLOAT NOT NULL DEFAULT 0.0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_private_module_weak_user_mod_code UNIQUE (user_id, module_id, topic_code)
);
CREATE INDEX IF NOT EXISTS ix_pmwt_user_id ON private_module_weak_topics (user_id);
CREATE INDEX IF NOT EXISTS ix_pmwt_module_id ON private_module_weak_topics (module_id);
CREATE INDEX IF NOT EXISTS ix_pmwt_topic_code ON private_module_weak_topics (topic_code);
"""


def run(db_url: str, data: list[dict], emails: list[str]) -> None:
    log.info("connecting to production DB (credential redacted)…")
    with _connect(db_url) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            # 1. DDL
            log.info("ensuring private-module tables exist…")
            cur.execute(DDL)

            # 2. Upsert module
            cur.execute(
                "SELECT id FROM private_modules WHERE slug = %s", (MODULE_SLUG,)
            )
            row = cur.fetchone()
            if row:
                module_id = row[0]
                cur.execute(
                    "UPDATE private_modules SET name=%s, description=%s, is_active=TRUE "
                    "WHERE id=%s",
                    (MODULE_NAME, MODULE_DESC, module_id),
                )
                log.info("updated existing module id=%s", module_id)
            else:
                module_id = uuid.uuid4()
                cur.execute(
                    "INSERT INTO private_modules (id, slug, name, description, is_active) "
                    "VALUES (%s, %s, %s, %s, TRUE)",
                    (str(module_id), MODULE_SLUG, MODULE_NAME, MODULE_DESC),
                )
                log.info("created module slug=%s id=%s", MODULE_SLUG, module_id)

            # 3. Replace questions
            cur.execute(
                "DELETE FROM private_module_questions WHERE module_id = %s",
                (str(module_id),),
            )
            log.info("cleared previous questions, loading %d new rows…", len(data))

            # Batched insert — one round-trip instead of 1966.
            rows = [
                (
                    str(uuid.uuid4()),
                    str(module_id),
                    q.get("qnum"),
                    q.get("section"),
                    q["subject"],
                    q["topic"],
                    q["topic_code"],
                    "MEDIUM",
                    q["stem"],
                    json.dumps(q["options"]),
                    q.get("explanation") or "",
                )
                for q in data
            ]
            try:
                from psycopg2.extras import execute_values  # type: ignore
                execute_values(
                    cur,
                    "INSERT INTO private_module_questions "
                    "(id, module_id, qnum, section, subject, topic, topic_code, "
                    "difficulty, question_text, options, explanation) VALUES %s",
                    rows,
                    page_size=500,
                )
            except ImportError:
                # psycopg3 path
                cur.executemany(
                    "INSERT INTO private_module_questions "
                    "(id, module_id, qnum, section, subject, topic, topic_code, "
                    "difficulty, question_text, options, explanation) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    rows,
                )
            log.info("inserted %d questions", len(rows))

            # 4. Grant access — only when explicitly requested via --email.
            #    Default flow is zero auto-grants; admins whitelist emails
            #    through the admin panel so the DB is the single source of truth.
            if emails:
                for raw in emails:
                    email = raw.strip().lower()
                    if not email or "@" not in email:
                        continue
                    cur.execute(
                        "SELECT 1 FROM private_module_access "
                        "WHERE module_id=%s AND LOWER(email)=%s",
                        (str(module_id), email),
                    )
                    if cur.fetchone():
                        log.info("access already granted: %s", email)
                        continue
                    cur.execute(
                        "INSERT INTO private_module_access "
                        "(id, module_id, email, note) VALUES (%s, %s, %s, %s)",
                        (str(uuid.uuid4()), str(module_id), email, "seed script"),
                    )
                    log.info("granted access: %s", email)
            else:
                log.info("no --email passed; manage access from the admin panel.")

        conn.commit()
        log.info("committed.")


def main() -> int:
    ap = argparse.ArgumentParser()
    default_json = Path(__file__).resolve().parent.parent / "seeds" / "epfo_apfc_bank.json"
    default_env = Path(__file__).resolve().parent.parent / ".env.local"
    ap.add_argument("--json", default=str(default_json))
    ap.add_argument("--env", default=str(default_env))
    ap.add_argument("--email", action="append", default=[])
    args = ap.parse_args()

    env = _load_env_local(Path(args.env))
    db_url = os.environ.get("PRODUCTION_DB_URL") or env.get("PRODUCTION_DB_URL")
    if not db_url:
        log.error("PRODUCTION_DB_URL not set in %s or env.", args.env)
        return 2

    json_path = Path(args.json)
    if not json_path.exists():
        log.error("Question JSON not found at %s", json_path)
        return 2
    data = json.loads(json_path.read_text(encoding="utf-8"))
    log.info("loaded %d questions from %s", len(data), json_path.name)

    run(db_url, data, list(args.email))
    log.info("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
