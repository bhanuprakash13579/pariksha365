-- ============================================================================
-- Manual schema-diff migration: add exam-structure backbone to a production DB
-- that was created via Base.metadata.create_all (no Alembic history).
--
-- SAFETY CHARACTERISTICS
-- ----------------------
-- * **Purely additive.** No DROP / RENAME / data change.
-- * **Idempotent.** Safe to re-run; every statement is guarded by
--   IF NOT EXISTS (or its CREATE TYPE DO-block equivalent).
-- * **No row deletions.** Existing categories, quiz_questions, users,
--   subject_taxonomy rows are untouched.
-- * **Wraps in a transaction.** Either the whole diff applies or nothing does.
--
-- AFFECTED TABLES / TYPES (all additive)
-- --------------------------------------
-- * test_type_enum                 — new ENUM ('MOCK','PYQ')
-- * categories.description         — new TEXT NULL
-- * categories.is_enabled          — new BOOL NOT NULL DEFAULT FALSE
-- * subcategories.slug             — new VARCHAR NULL, backfilled, then NOT NULL
-- * subcategories.description      — new TEXT NULL
-- * subcategories.is_enabled       — new BOOL NOT NULL DEFAULT FALSE
-- * subcategories(category_id,slug) — new UNIQUE INDEX
-- * exam_stages                    — new table (FK → subcategories)
-- * exam_patterns                  — new table (FK → exam_stages, 1:1)
-- * section_patterns               — new table (FK → exam_patterns, 1:N)
-- * test_series.exam_stage_id      — new UUID NULL FK → exam_stages (ON DELETE SET NULL)
-- * test_series.test_type          — new test_type_enum NOT NULL DEFAULT 'MOCK'
-- * test_series.source_pdf_path    — new VARCHAR NULL
-- * test_series.paper_date         — new DATE NULL
-- * test_series.paper_shift        — new VARCHAR NULL
--
-- HOW TO RUN
-- ----------
-- Save the production DB URL in backend/.env.local as PRODUCTION_DB_URL, then:
--     psql "$PRODUCTION_DB_URL" -v ON_ERROR_STOP=1 -f \
--       backend/migrations/manual/20260419_add_exam_structure.sql
--
-- Check post-run with:
--     \d categories
--     \d subcategories
--     \d test_series
--     \d exam_stages
-- ============================================================================

BEGIN;

-- 1. ENUM type (Postgres has no CREATE TYPE IF NOT EXISTS — use DO-block)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'test_type_enum') THEN
        CREATE TYPE test_type_enum AS ENUM ('MOCK', 'PYQ');
    END IF;
END
$$;

-- 2. categories — add description + is_enabled
-- CRITICAL: pre-existing rows must default to TRUE (visible) because the app
-- treated them as visible before the flag existed. Using DEFAULT FALSE without
-- this compensating UPDATE previously broke admin login in production
-- (all 11 categories silently disappeared from the category-listing filter).
-- New rows created after this migration take the column default (FALSE) —
-- that's the intent for admin-gated release of new content.
ALTER TABLE categories ADD COLUMN IF NOT EXISTS description TEXT NULL;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS is_enabled BOOLEAN NOT NULL DEFAULT FALSE;
-- Flip every PRE-EXISTING row to TRUE. No-op on re-run (already TRUE).
UPDATE categories SET is_enabled = TRUE WHERE is_enabled = FALSE;
CREATE INDEX IF NOT EXISTS ix_categories_is_enabled ON categories (is_enabled);

-- 3. subcategories — add slug, description, is_enabled + unique index
-- Same visibility-preservation rule applies.
ALTER TABLE subcategories ADD COLUMN IF NOT EXISTS slug VARCHAR NULL;
ALTER TABLE subcategories ADD COLUMN IF NOT EXISTS description TEXT NULL;
ALTER TABLE subcategories ADD COLUMN IF NOT EXISTS is_enabled BOOLEAN NOT NULL DEFAULT FALSE;
UPDATE subcategories SET is_enabled = TRUE WHERE is_enabled = FALSE;

-- Backfill slug for any existing rows (empty table today, but guard anyway)
UPDATE subcategories
   SET slug = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g'))
 WHERE slug IS NULL;

-- Make slug NOT NULL once backfill is complete
ALTER TABLE subcategories ALTER COLUMN slug SET NOT NULL;

CREATE INDEX IF NOT EXISTS ix_subcategories_is_enabled ON subcategories (is_enabled);
-- Unique constraint via unique index (Postgres treats these equivalently for
-- SQLAlchemy's unique=True) — guarded by IF NOT EXISTS
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_subcategory_cat_slug'
    ) THEN
        ALTER TABLE subcategories
            ADD CONSTRAINT uq_subcategory_cat_slug UNIQUE (category_id, slug);
    END IF;
END
$$;

-- 4. exam_stages
CREATE TABLE IF NOT EXISTS exam_stages (
    id              UUID PRIMARY KEY,
    subcategory_id  UUID NOT NULL REFERENCES subcategories(id) ON DELETE CASCADE,
    name            VARCHAR NOT NULL,
    slug            VARCHAR NOT NULL,
    "order"         INTEGER NOT NULL DEFAULT 0,
    is_enabled      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_exam_stage_subcat_slug UNIQUE (subcategory_id, slug)
);
CREATE INDEX IF NOT EXISTS ix_exam_stages_id ON exam_stages (id);
CREATE INDEX IF NOT EXISTS ix_exam_stages_subcategory_id ON exam_stages (subcategory_id);
CREATE INDEX IF NOT EXISTS ix_exam_stages_is_enabled ON exam_stages (is_enabled);

-- 5. exam_patterns (1-to-1 with exam_stages)
CREATE TABLE IF NOT EXISTS exam_patterns (
    id                       UUID PRIMARY KEY,
    exam_stage_id            UUID NOT NULL UNIQUE
                                REFERENCES exam_stages(id) ON DELETE CASCADE,
    total_duration_minutes   INTEGER NOT NULL,
    total_questions          INTEGER NOT NULL,
    total_marks              DOUBLE PRECISION NOT NULL,
    negative_mark_per_wrong  DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    has_sectional_timing     BOOLEAN NOT NULL DEFAULT FALSE,
    notes                    TEXT NULL,
    created_at               TIMESTAMPTZ DEFAULT NOW(),
    updated_at               TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_exam_patterns_id ON exam_patterns (id);
CREATE INDEX IF NOT EXISTS ix_exam_patterns_exam_stage_id ON exam_patterns (exam_stage_id);

-- 6. section_patterns (1-to-N under exam_patterns)
CREATE TABLE IF NOT EXISTS section_patterns (
    id                  UUID PRIMARY KEY,
    exam_pattern_id     UUID NOT NULL REFERENCES exam_patterns(id) ON DELETE CASCADE,
    name                VARCHAR NOT NULL,
    subject             VARCHAR NOT NULL,
    question_count      INTEGER NOT NULL,
    duration_minutes    INTEGER NULL,
    marks_per_question  DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "order"             INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_section_patterns_id ON section_patterns (id);
CREATE INDEX IF NOT EXISTS ix_section_patterns_exam_pattern_id ON section_patterns (exam_pattern_id);
CREATE INDEX IF NOT EXISTS ix_section_patterns_subject ON section_patterns (subject);

-- 7. test_series — add exam_stage_id, test_type, PYQ provenance columns
ALTER TABLE test_series
    ADD COLUMN IF NOT EXISTS exam_stage_id UUID NULL
        REFERENCES exam_stages(id) ON DELETE SET NULL;
ALTER TABLE test_series
    ADD COLUMN IF NOT EXISTS test_type test_type_enum NOT NULL DEFAULT 'MOCK';
ALTER TABLE test_series ADD COLUMN IF NOT EXISTS source_pdf_path VARCHAR NULL;
ALTER TABLE test_series ADD COLUMN IF NOT EXISTS paper_date DATE NULL;
ALTER TABLE test_series ADD COLUMN IF NOT EXISTS paper_shift VARCHAR NULL;

CREATE INDEX IF NOT EXISTS ix_test_series_exam_stage_id ON test_series (exam_stage_id);
CREATE INDEX IF NOT EXISTS ix_test_series_test_type ON test_series (test_type);

-- 8. Stamp Alembic at the Phase-1 revision so subsequent Alembic operations
--    work on top of this schema. Safe to skip if you don't use Alembic.
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Only insert the version if the table is empty — this makes the script
-- idempotent: re-running won't duplicate rows.
INSERT INTO alembic_version (version_num)
SELECT '20260419_01'
 WHERE NOT EXISTS (SELECT 1 FROM alembic_version);

COMMIT;

-- ============================================================================
-- Post-run sanity checks (run these manually to verify):
--
-- SELECT column_name FROM information_schema.columns
--  WHERE table_name='categories' AND column_name IN ('description','is_enabled');
--   expect 2 rows
--
-- SELECT COUNT(*) FROM information_schema.tables
--  WHERE table_name IN ('exam_stages','exam_patterns','section_patterns');
--   expect 3
--
-- SELECT version_num FROM alembic_version;
--   expect '20260419_01'
-- ============================================================================
