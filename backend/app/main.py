from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth_router, user_router, admin_router, test_series_router, attempt_router, payment_router, course_router, category_router, analytics_router, search_router, quiz_router, exam_structure_router, private_module_router, config_router
import app.models

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically drop and create database tables on startup (WIPES DATA!)
    try:
        async with engine.begin() as conn:
            if os.getenv("WIPE_DB_ON_STARTUP") == "True":
                print("WIPE_DB_ON_STARTUP flag is enabled. Dropping all tables...")
                if engine.dialect.name == "postgresql":
                    from sqlalchemy import text
                    print("Postgres dialect detected. Dropping old dependent tables via CASCADE...")
                    await conn.execute(text("DROP TABLE IF EXISTS options CASCADE;"))
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("STARTUP: Base.metadata.create_all completed")
    except Exception as create_err:
        # Don't let a schema-creation problem block the rest of startup —
        # in particular, the admin bootstrap MUST run so the user can always
        # log in with the env-var password even if a new model has a
        # migration-style problem.
        print(f"STARTUP: create_all failed (continuing anyway): {create_err!r}")

    from app.core.database import SessionLocal
    from app.models.category import Category
    from app.models.subcategory import SubCategory
    from sqlalchemy.future import select

    # ADMIN BOOTSTRAP — runs BEFORE other startup work so a problem in
    # category seeding or self-heal can never block the admin from logging in.
    # Wrapped in its own session so failures here don't poison later work.
    async with SessionLocal() as db:
        admin_boot_pw = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "").strip()
        if not admin_boot_pw:
            print(
                "ADMIN BOOTSTRAP: ADMIN_BOOTSTRAP_PASSWORD env var is EMPTY — "
                "skipping. Set it on Railway to enable env-driven admin password."
            )
        else:
            try:
                from app.models.role import Role
                from app.models.user import User
                from app.core.security import get_password_hash
                admin_email = (
                    os.getenv("ADMIN_BOOTSTRAP_EMAIL", "").strip()
                    or "admin@pariksha365.in"
                )
                admin_name = os.getenv("ADMIN_BOOTSTRAP_NAME", "Admin").strip() or "Admin"

                role_res = await db.execute(select(Role).where(Role.name == "Admin"))
                admin_role = role_res.scalars().first()
                if admin_role is None:
                    admin_role = Role(name="Admin")
                    db.add(admin_role)
                    await db.commit()
                    await db.refresh(admin_role)
                    print(f"ADMIN BOOTSTRAP: created 'Admin' role id={admin_role.id}")

                new_hash = get_password_hash(admin_boot_pw)
                user_res = await db.execute(select(User).where(User.email == admin_email))
                admin_user = user_res.scalars().first()
                if admin_user is None:
                    admin_user = User(
                        name=admin_name,
                        email=admin_email,
                        password_hash=new_hash,
                        role_id=admin_role.id,
                        is_active=True,
                    )
                    db.add(admin_user)
                    await db.commit()
                    print(
                        f"ADMIN BOOTSTRAP_SUCCESS: created admin user "
                        f"email={admin_email} hash_prefix={new_hash[:7]}... "
                        f"hash_len={len(new_hash)} env_pw_len={len(admin_boot_pw)}"
                    )
                else:
                    admin_user.role_id = admin_role.id
                    admin_user.password_hash = new_hash
                    admin_user.is_active = True
                    await db.commit()
                    print(
                        f"ADMIN BOOTSTRAP_SUCCESS: rehashed admin password "
                        f"email={admin_email} hash_prefix={new_hash[:7]}... "
                        f"hash_len={len(new_hash)} env_pw_len={len(admin_boot_pw)} "
                        f"is_active={admin_user.is_active}"
                    )
            except Exception as e:
                # Loud failure — visible in Railway logs.
                print(f"ADMIN BOOTSTRAP_FAILED: {type(e).__name__}: {e!r}")

    async with SessionLocal() as db:
        result = await db.execute(select(Category).limit(1))
        if not result.scalars().first():
            print("Seeding default Exam Categories...")
            defaults = [
                {"name": "Bank", "icon": "library-outline", "subs": []},
                {"name": "Judicial", "icon": "hammer-outline", "subs": []},
                {"name": "ESIC", "icon": "medkit-outline", "subs": []},
                {"name": "Railway", "icon": "train-outline", "subs": []},
                {"name": "Defence", "icon": "shield-checkmark-outline", "subs": []},
                {"name": "PSUs", "icon": "business-outline", "subs": []},
                {"name": "UPSC", "icon": "ribbon-outline", "subs": []},
                {"name": "SSC", "icon": "clipboard-outline", "subs": []},
                {"name": "Police", "icon": "shield-half-outline", "subs": []},
                {"name": "PSCs", "icon": "newspaper-outline", "subs": []},
                {"name": "Post-Office", "icon": "mail-outline", "subs": []}
            ]
            # Note: is_enabled=True explicitly — default-False on the column
            # once hid all 11 pre-seeded categories from the admin UI, making
            # it look as if the admin login was broken. See memory:
            # feedback_migration_preserve_visibility for the original incident.
            for i, c in enumerate(defaults):
                cat_db = Category(name=c["name"], icon_name=c["icon"], order=i, is_enabled=True)
                db.add(cat_db)
                await db.commit()
                await db.refresh(cat_db)
                for j, sub in enumerate(c["subs"]):
                    db.add(SubCategory(category_id=cat_db.id, name=sub, order=j, is_enabled=True))
            await db.commit()

        # SELF-HEAL: ensure new test_series timing columns exist on prod
        # Postgres. ``Base.metadata.create_all`` only creates *new* tables —
        # it does not ALTER existing ones. Without this block, the new
        # ``total_duration_minutes`` / ``has_sectional_timing`` columns added
        # in this release would silently be missing on a long-running
        # database and every TestSeries query would crash with UndefinedColumn.
        try:
            from sqlalchemy import text as _sql_text
            if engine.dialect.name == "postgresql":
                await db.execute(_sql_text(
                    "ALTER TABLE test_series "
                    "ADD COLUMN IF NOT EXISTS total_duration_minutes INTEGER;"
                ))
                await db.execute(_sql_text(
                    "ALTER TABLE test_series "
                    "ADD COLUMN IF NOT EXISTS has_sectional_timing BOOLEAN "
                    "NOT NULL DEFAULT FALSE;"
                ))
                # Current-Affairs lifecycle columns on quiz_questions. Admin
                # uses these to filter and refresh the CA pool from the
                # admin panel without touching the static-GK rows.
                await db.execute(_sql_text(
                    "ALTER TABLE quiz_questions "
                    "ADD COLUMN IF NOT EXISTS is_current_affair BOOLEAN "
                    "NOT NULL DEFAULT FALSE;"
                ))
                await db.execute(_sql_text(
                    "ALTER TABLE quiz_questions "
                    "ADD COLUMN IF NOT EXISTS event_date DATE;"
                ))
                await db.execute(_sql_text(
                    "ALTER TABLE quiz_questions "
                    "ADD COLUMN IF NOT EXISTS valid_until DATE;"
                ))
                await db.execute(_sql_text(
                    "ALTER TABLE quiz_questions "
                    "ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMPTZ;"
                ))
                await db.execute(_sql_text(
                    "ALTER TABLE quiz_questions "
                    "ADD COLUMN IF NOT EXISTS is_published BOOLEAN "
                    "NOT NULL DEFAULT TRUE;"
                ))
                await db.commit()
        except Exception as alter_err:
            # Don't block startup — log and continue. A failed ALTER usually
            # means the column already exists with an incompatible type, which
            # admin can fix by hand; in the worst case the app keeps running on
            # the old schema and student attempts use the legacy section-sum
            # timer fallback.
            print(f"STARTUP: timing-column ALTER skipped due to: {alter_err!r}")

        # SELF-HEAL: Cashfree payment integration — new columns on the
        # existing payments table and a new enum value for the provider.
        try:
            # Add CASHFREE value to the paymentprovider enum (IF NOT EXISTS
            # was added in Postgres 9.3 — all modern versions support it).
            await db.execute(_sql_text(
                "ALTER TYPE paymentprovider ADD VALUE IF NOT EXISTS 'CASHFREE';"
            ))
            # New columns on payments (safe to run repeatedly via IF NOT EXISTS)
            await db.execute(_sql_text(
                "ALTER TABLE payments ADD COLUMN IF NOT EXISTS "
                "payment_type VARCHAR DEFAULT 'COURSE';"
            ))
            await db.execute(_sql_text(
                "ALTER TABLE payments ADD COLUMN IF NOT EXISTS "
                "exam_stage_id UUID REFERENCES exam_stages(id) ON DELETE SET NULL;"
            ))
            await db.commit()
        except Exception as cf_alter_err:
            print(f"STARTUP: Cashfree schema self-heal skipped: {cf_alter_err!r}")

        # SELF-HEAL: If EVERY category in the DB is currently is_enabled=False,
        # that almost certainly means a migration or an accidental toggle hid
        # them all, which cripples the admin UI. Flip them all back to True.
        # This runs on every startup but is a no-op when any category is
        # already visible. This is the same one-liner we manually applied
        # after the original 2026-04-19 admin-login incident.
        try:
            from sqlalchemy import func as _sql_func, update as _sql_update
            total = (await db.execute(select(_sql_func.count()).select_from(Category))).scalar_one()
            enabled = (
                await db.execute(
                    select(_sql_func.count()).select_from(Category).where(Category.is_enabled.is_(True))
                )
            ).scalar_one()
            if total > 0 and enabled == 0:
                print(
                    f"SELF-HEAL: {total} categories all disabled — restoring "
                    "is_enabled=True to prevent admin-panel-looks-broken state."
                )
                await db.execute(_sql_update(Category).values(is_enabled=True))
                await db.execute(_sql_update(SubCategory).values(is_enabled=True))
                await db.commit()
        except Exception as e:  # defensive — never block startup
            print(f"SELF-HEAL check skipped due to: {e!r}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Gzip large JSON responses. Course/tests listings and the EPFO bank can be
# hundreds of KB; on a cold Railway→browser hop that's often the single biggest
# wall-clock cost. minimum_size=1000 means small responses (health, auth tokens)
# skip the compression cost entirely.
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://pariksha365.in",
        "https://www.pariksha365.in",
        "https://api.pariksha365.in",
        "https://pariksha365-production-v2.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "traceback": traceback.format_exc()},
    )

app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(user_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(admin_router.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(test_series_router.router, prefix=f"{settings.API_V1_STR}/tests", tags=["test-series"])
app.include_router(course_router.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(attempt_router.router, prefix=f"{settings.API_V1_STR}/attempts", tags=["attempts"])
app.include_router(payment_router.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])
app.include_router(category_router.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(analytics_router.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(search_router.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(quiz_router.router, prefix=f"{settings.API_V1_STR}/quiz", tags=["quiz"])
app.include_router(exam_structure_router.public_router, prefix=f"{settings.API_V1_STR}/exam-structure", tags=["exam-structure"])
app.include_router(exam_structure_router.admin_router, prefix=f"{settings.API_V1_STR}/admin/exam-structure", tags=["admin-exam-structure"])
app.include_router(private_module_router.router, prefix=f"{settings.API_V1_STR}/private", tags=["private-modules"])
app.include_router(config_router.router, prefix=f"{settings.API_V1_STR}/config", tags=["config"])

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount the uploads directory to serve uploaded images (e.g. from the Scraper Hub)
os.makedirs("uploads/images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Privacy Policy - Pariksha365</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }
            h1, h2, h3 { color: #2c3e50; }
            .container { background-color: #f9f9f9; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Privacy Policy for Pariksha365</h1>
            <p><strong>Last Updated: February 23, 2026</strong></p>
            
            <h2>1. Introduction</h2>
            <p>Welcome to Pariksha365. This Privacy Policy outlines how we collect, use, and protect your information when you use our mobile application and related services.</p>
            
            <h2>2. Information We Collect</h2>
            <ul>
                <li><strong>Personal Information:</strong> When you register, we collect information such as your name, email address, and profile details (e.g., via Google or Apple Sign-In).</li>
                <li><strong>Usage Data:</strong> We collect data regarding your mock test attempts, scores, analytics, and interaction with the app to provide personalized insights and rankings.</li>
                <li><strong>Device Information:</strong> We may collect non-identifiable device information to ensure app stability and fix crashes.</li>
            </ul>
            
            <h2>3. How We Use Your Information</h2>
            <ul>
                <li>To provide, maintain, and improve the Pariksha365 platform.</li>
                <li>To generate test performance analytics, rankings, and percentiles.</li>
                <li>To manage your account and communicate important updates.</li>
            </ul>
            
            <h2>4. Data Sharing and Security</h2>
            <p>We do not sell your personal information to third parties. We use industry-standard security measures to protect your data. Your password and sensitive data are encrypted.</p>
            
            <h2>5. Children's Privacy</h2>
            <p>Our services are generally intended for users preparing for competitive exams (typically ages 16+). We do not knowingly collect personal information from children under the age of 13 without parental consent.</p>
            
            <h2>6. Account and Data Deletion</h2>
            <p>You have the right to request the deletion of your personal data and account at any time. We provide a simple, automated way for you to delete your account entirely.</p>
            <h3>How to Delete Your Account:</h3>
            <ol>
                <li>Open the Pariksha365 mobile application.</li>
                <li>Tap on the <strong>Profile</strong> icon or navigate to the <strong>Settings</strong> menu.</li>
                <li>Tap the <strong>Delete Account</strong> button at the bottom of the screen.</li>
                <li>Confirm your request when prompted.</li>
            </ol>
            <h3>Data Retention and Deletion Practices:</h3>
            <ul>
                <li><strong>What is deleted immediately:</strong> Your personal profile, email, authentication tokens, and device identifiers are wiped from our active databases immediately upon request.</li>
                <li><strong>What is retained:</strong> Anonymous, aggregated test attempt data (stripped of any personally identifiable information) may be retained for analytical purposes to calculate historical percentiles.</li>
                <li><strong>Backup Retention:</strong> Your encrypted data may persist in routine secure backups for up to 90 days before being completely purged from all systems.</li>
            </ul>
            
            <h2>7. Contact Us</h2>
            <p>If you have any questions regarding this Privacy Policy, please contact us at: support@pariksha365.in</p>
        </div>
    </body>
    </html>
    """
