-- ============================================================================
-- EMERGENCY FIX: Restore admin-panel visibility by flipping every category
-- and subcategory to is_enabled=TRUE.
--
-- When to run:
--   * Admin reports "unable to login as admin" but authentication is fine,
--     just the admin dashboard looks empty / broken.
--   * Most commonly happens when a fresh migration added the is_enabled flag
--     with NOT NULL DEFAULT FALSE and pre-existing rows went silently dark.
--
-- What it does:
--   * UPDATE categories SET is_enabled = TRUE  (idempotent — no-op if already true)
--   * UPDATE subcategories SET is_enabled = TRUE
--   * Does NOT touch exam_stages.is_enabled (admin manages those explicitly).
--
-- Alternative: call POST /api/v1/categories/admin/restore-visibility via the
-- admin UI (requires admin JWT; does the same thing with authz).
--
-- USAGE:
--   psql "$PRODUCTION_DB_URL" -v ON_ERROR_STOP=1 -f \
--     backend/migrations/manual/FIX_restore_admin_visibility.sql
-- ============================================================================

BEGIN;

UPDATE categories    SET is_enabled = TRUE WHERE is_enabled = FALSE;
UPDATE subcategories SET is_enabled = TRUE WHERE is_enabled = FALSE;

-- Sanity: report counts.
SELECT
    (SELECT COUNT(*) FROM categories    WHERE is_enabled = TRUE) AS visible_categories,
    (SELECT COUNT(*) FROM subcategories WHERE is_enabled = TRUE) AS visible_subcategories;

COMMIT;
