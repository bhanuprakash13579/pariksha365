-- ============================================================================
-- Manual schema-diff migration: per-ExamStage pricing + purchase entitlements.
--
-- BUSINESS RULE
-- -------------
-- Admin sets a price_inr and validity_days on each ExamStage. A purchase by a
-- student creates an entitlement row with expires_at = NOW() + validity_days
-- and grants access to the MOCK test_series under that stage. PYQ test_series
-- are ALWAYS free regardless of the stage's price (hard rule enforced in the
-- service layer, not the schema — the price column sits on the stage, which is
-- shared between MOCK and PYQ children).
--
-- SAFETY CHARACTERISTICS
-- ----------------------
-- * Purely additive. No DROP / RENAME / data change.
-- * Idempotent. Every statement guarded by IF NOT EXISTS.
-- * Defaults (price 0, validity 365) keep every existing stage FREE until the
--   admin explicitly prices it. No silent paywall.
-- ============================================================================

BEGIN;

-- 1. Pricing columns on exam_stages
ALTER TABLE exam_stages
    ADD COLUMN IF NOT EXISTS price_inr INTEGER NOT NULL DEFAULT 0;
ALTER TABLE exam_stages
    ADD COLUMN IF NOT EXISTS validity_days INTEGER NOT NULL DEFAULT 365;

-- Non-negative guard — bad data from a future admin-UI bug should error, not
-- quietly sell a stage for ₹-5.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_exam_stage_price_nonneg') THEN
        ALTER TABLE exam_stages
            ADD CONSTRAINT ck_exam_stage_price_nonneg CHECK (price_inr >= 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_exam_stage_validity_positive') THEN
        ALTER TABLE exam_stages
            ADD CONSTRAINT ck_exam_stage_validity_positive CHECK (validity_days >= 1);
    END IF;
END
$$;

-- 2. Entitlement rows — one per purchase, expires_at frozen at purchase time.
-- A user may have multiple rows per stage (re-purchase / extension); access is
-- determined by "exists a row with expires_at > NOW()".
CREATE TABLE IF NOT EXISTS exam_stage_purchases (
    id                       UUID PRIMARY KEY,
    user_id                  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exam_stage_id            UUID NOT NULL REFERENCES exam_stages(id) ON DELETE CASCADE,
    amount_paid_inr          INTEGER NOT NULL,
    validity_days_at_purchase INTEGER NOT NULL,
    purchased_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at               TIMESTAMPTZ NOT NULL,
    payment_id               UUID NULL REFERENCES payments(id) ON DELETE SET NULL,
    note                     VARCHAR NULL,
    CONSTRAINT ck_purchase_amount_nonneg CHECK (amount_paid_inr >= 0),
    CONSTRAINT ck_purchase_expiry_after CHECK (expires_at > purchased_at)
);

-- Fast entitlement lookup: "is user X allowed to access stage Y right now?"
CREATE INDEX IF NOT EXISTS ix_stage_purchases_user_stage_expiry
    ON exam_stage_purchases (user_id, exam_stage_id, expires_at);

CREATE INDEX IF NOT EXISTS ix_stage_purchases_user_id
    ON exam_stage_purchases (user_id);

-- 3. Bump alembic stamp so future Alembic ops build on top of this.
INSERT INTO alembic_version (version_num)
SELECT '20260420_01'
 WHERE NOT EXISTS (SELECT 1 FROM alembic_version WHERE version_num = '20260420_01');

-- If the table was already stamped at the previous version, advance it.
UPDATE alembic_version SET version_num = '20260420_01'
 WHERE version_num = '20260419_01';

COMMIT;

-- ============================================================================
-- Post-run sanity checks:
--
-- SELECT column_name FROM information_schema.columns
--  WHERE table_name='exam_stages' AND column_name IN ('price_inr','validity_days');
--   expect 2 rows
--
-- SELECT COUNT(*) FROM information_schema.tables
--  WHERE table_name = 'exam_stage_purchases';
--   expect 1
--
-- SELECT version_num FROM alembic_version;  -- expect '20260420_01'
-- ============================================================================
