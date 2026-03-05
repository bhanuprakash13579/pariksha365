"""
Admin Analytics Service
=======================
All analytics are computed via single SQL aggregate queries (no Python loops over full datasets).
Results are cached in-memory for 5 minutes so repeated dashboard loads don't hit the DB.
Zero extra cost — uses the existing Railway Postgres/SQLite database.
"""
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

# ── Simple in-memory TTL cache ──────────────────────────────────────────────
_cache: dict = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < _CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _cache_set(key: str, data):
    _cache[key] = {"data": data, "ts": time.time()}


# ── Analytics Queries ────────────────────────────────────────────────────────

async def get_overview(db: AsyncSession) -> dict:
    """Master analytics overview — all panels in one call."""
    cached = _cache_get("admin_overview")
    if cached:
        return cached

    result = {}

    # 1. Platform-level totals (single query)
    totals = (await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM users)           AS total_users,
            (SELECT COUNT(*) FROM test_series WHERE is_published = 1) AS total_tests,
            (SELECT COUNT(*) FROM attempts)        AS total_attempts,
            (SELECT COUNT(*) FROM attempts WHERE status = 'submitted') AS completed_attempts
    """))).mappings().first()
    result["totals"] = dict(totals) if totals else {}

    # 2. Top 10 most attempted tests
    top_tests_rows = (await db.execute(text("""
        SELECT
            ts.title,
            ts.category,
            COUNT(a.id)                                              AS attempt_count,
            ROUND(
                100.0 * SUM(CASE WHEN a.status = 'submitted' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(a.id), 0), 1
            )                                                        AS completion_rate,
            ROUND(AVG(r.total_score), 1)                             AS avg_score
        FROM test_series ts
        LEFT JOIN attempts a ON a.test_series_id = ts.id
        LEFT JOIN results  r ON r.attempt_id = a.id
        WHERE ts.is_published = 1
        GROUP BY ts.id, ts.title, ts.category
        ORDER BY attempt_count DESC
        LIMIT 10
    """))).mappings().all()
    result["top_tests"] = [dict(r) for r in top_tests_rows]

    # 3. Category popularity (attempts per exam group)
    cat_popularity_rows = (await db.execute(text("""
        SELECT
            COALESCE(ts.category, 'Other')        AS category,
            COUNT(a.id)                           AS attempt_count,
            COUNT(DISTINCT ts.id)                 AS test_count,
            COUNT(DISTINCT a.user_id)             AS unique_students
        FROM test_series ts
        LEFT JOIN attempts a ON a.test_series_id = ts.id
        WHERE ts.is_published = 1
        GROUP BY ts.category
        ORDER BY attempt_count DESC
    """))).mappings().all()
    result["category_popularity"] = [dict(r) for r in cat_popularity_rows]

    # 4. Weekly trend — last 7 days vs previous 7 days
    week_trend_rows = (await db.execute(text("""
        SELECT
            DATE(started_at) AS day,
            COUNT(*)         AS attempt_count
        FROM attempts
        WHERE started_at >= DATE('now', '-13 days')
        GROUP BY day
        ORDER BY day ASC
    """))).mappings().all()
    result["weekly_trend"] = [dict(r) for r in week_trend_rows]

    # 5. Content gap: categories with < 5 published tests (using available data)
    coverage_rows = (await db.execute(text("""
        SELECT
            category,
            COUNT(*) AS test_count
        FROM test_series
        WHERE is_published = 1
        GROUP BY category
        ORDER BY test_count ASC
    """))).mappings().all()
    result["coverage"] = [dict(r) for r in coverage_rows]

    # 6. Top 5 most active users (attempt count)
    top_users_rows = (await db.execute(text("""
        SELECT
            u.name,
            u.email,
            COUNT(a.id)                                              AS attempt_count,
            ROUND(AVG(r.accuracy_percentage), 1)                     AS avg_accuracy
        FROM users u
        LEFT JOIN attempts a ON a.user_id = u.id
        LEFT JOIN results  r ON r.attempt_id = a.id
        GROUP BY u.id, u.name, u.email
        ORDER BY attempt_count DESC
        LIMIT 5
    """))).mappings().all()
    result["top_users"] = [dict(r) for r in top_users_rows]

    # 7. Overall completion rate and average score trends
    health_rows = (await db.execute(text("""
        SELECT
            ROUND(100.0 * COUNT(CASE WHEN a.status = 'submitted' THEN 1 END) / NULLIF(COUNT(a.id), 0), 1) AS overall_completion_rate,
            ROUND(AVG(r.accuracy_percentage), 1)                                                           AS overall_avg_accuracy,
            ROUND(AVG(r.percentile), 1)                                                                    AS avg_percentile
        FROM attempts a
        LEFT JOIN results r ON r.attempt_id = a.id
    """))).mappings().first()
    result["health"] = dict(health_rows) if health_rows else {}

    _cache_set("admin_overview", result)
    logger.info("[AdminAnalytics] Overview computed and cached for 5 minutes.")
    return result
