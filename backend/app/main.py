from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth_router, user_router, admin_router, test_series_router, attempt_router, payment_router, course_router, category_router, analytics_router, search_router, quiz_router, exam_structure_router, private_module_router, config_router
import app.models

import asyncio
import os


async def _admin_bootstrap_with_timeout(timeout_seconds: int = 20) -> None:
    """Re-hash the env-var admin password into the DB.

    Wrapped in asyncio.wait_for so a slow/locked Railway DB can NEVER block
    the app from starting. On timeout we log and move on — admin login will
    keep working with whatever hash is already in the DB.
    """
    from app.core.database import SessionLocal
    from sqlalchemy.future import select

    admin_boot_pw = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "").strip()
    if not admin_boot_pw:
        print("ADMIN BOOTSTRAP: ADMIN_BOOTSTRAP_PASSWORD env var is EMPTY — skipping.")
        return

    async def _run() -> None:
        from app.models.role import Role
        from app.models.user import User
        from app.core.security import get_password_hash
        admin_email = (os.getenv("ADMIN_BOOTSTRAP_EMAIL", "").strip()
                       or "admin@pariksha365.in")
        admin_name = os.getenv("ADMIN_BOOTSTRAP_NAME", "Admin").strip() or "Admin"
        async with SessionLocal() as db:
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
                admin_user = User(name=admin_name, email=admin_email,
                                  password_hash=new_hash, role_id=admin_role.id,
                                  is_active=True)
                db.add(admin_user)
                await db.commit()
                print(f"ADMIN BOOTSTRAP_SUCCESS: created admin user {admin_email}")
            else:
                admin_user.role_id = admin_role.id
                admin_user.password_hash = new_hash
                admin_user.is_active = True
                await db.commit()
                print(f"ADMIN BOOTSTRAP_SUCCESS: rehashed password for {admin_email}")

    try:
        await asyncio.wait_for(_run(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        print(f"ADMIN BOOTSTRAP_TIMEOUT: exceeded {timeout_seconds}s — continuing without rehash.")
    except Exception as e:
        print(f"ADMIN BOOTSTRAP_FAILED: {type(e).__name__}: {e!r}")


async def _background_schema_selfheal() -> None:
    """All the slow stuff: create_all, ALTER TABLEs, category seeding, visibility flip.

    Runs AFTER the app starts serving requests so a slow/locked DB never
    blocks login. Each block is independent and never raises out — failures
    just print and move on.
    """
    from app.core.database import SessionLocal
    from app.models.category import Category
    from app.models.subcategory import SubCategory
    from sqlalchemy import text as _sql_text, func as _sql_func, update as _sql_update
    from sqlalchemy.future import select

    # 1. metadata.create_all — only run if explicitly requested. Once tables
    #    exist this is a no-op but the table-introspection round-trips still
    #    add 5-15s per startup on a busy DB. Set RUN_CREATE_ALL=1 on first
    #    deploy or after model additions.
    if os.getenv("RUN_CREATE_ALL") == "1":
        try:
            async with engine.begin() as conn:
                if os.getenv("WIPE_DB_ON_STARTUP") == "True":
                    print("WIPE_DB_ON_STARTUP: dropping all tables.")
                    if engine.dialect.name == "postgresql":
                        await conn.execute(_sql_text("DROP TABLE IF EXISTS options CASCADE;"))
                    await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            print("BG: create_all completed")
        except Exception as e:
            print(f"BG: create_all failed: {e!r}")

    # 2. ALTER TABLE self-heal — every post-baseline column on the hot-path
    #    tables (test_series, quiz_questions, questions) is added here with
    #    IF NOT EXISTS so a redeploy onto a DB that's missing any of them
    #    auto-repairs before the first user request. Each ALTER is run in its
    #    OWN transaction so one failure doesn't poison the rest of the heal —
    #    that's the bug that broke quizzes today: a single statement raised,
    #    Postgres marked the txn as aborted, and the remaining ALTERs (which
    #    would have added passage_id, diagram_svg, etc.) silently no-op'd.
    if engine.dialect.name == "postgresql":
        heal_stmts = (
            # --- test_series (mocks / PYQs) ----------------------------------
            "ALTER TABLE test_series ADD COLUMN IF NOT EXISTS total_duration_minutes INTEGER;",
            "ALTER TABLE test_series ADD COLUMN IF NOT EXISTS has_sectional_timing BOOLEAN NOT NULL DEFAULT FALSE;",
            "ALTER TABLE test_series ADD COLUMN IF NOT EXISTS cdn_url VARCHAR;",
            # --- quiz_questions (daily quiz / weak-topic / CA) ---------------
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS is_current_affair BOOLEAN NOT NULL DEFAULT FALSE;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS event_date DATE;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS valid_until DATE;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMPTZ;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS is_published BOOLEAN NOT NULL DEFAULT TRUE;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS passage_id VARCHAR;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS diagram_svg TEXT;",
            "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS explanation_svg TEXT;",
            "CREATE INDEX IF NOT EXISTS ix_quiz_questions_passage_id ON quiz_questions (passage_id);",
            # --- questions (test-series MCQs) --------------------------------
            "ALTER TABLE questions ADD COLUMN IF NOT EXISTS diagram_svg TEXT;",
            "ALTER TABLE questions ADD COLUMN IF NOT EXISTS explanation_svg TEXT;",
            # --- users (Apple Sign-In) ----------------------------------------
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS apple_sub VARCHAR;",
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_apple_sub ON users (apple_sub);",
        )
        ok = 0
        for stmt in heal_stmts:
            try:
                async with SessionLocal() as db:
                    await db.execute(_sql_text(stmt))
                    await db.commit()
                ok += 1
            except Exception as e:
                # Failures are expected for ALTERs on tables that don't exist
                # yet (fresh DB before create_all). Log and continue.
                print(f"BG: heal skipped — {stmt[:60]}…: {e!r}")
        print(f"BG: column self-heal applied {ok}/{len(heal_stmts)} statements")

    # 3. Cashfree enum + payment columns. Idempotent.
    try:
        async with SessionLocal() as db:
            await db.execute(_sql_text("ALTER TYPE paymentprovider ADD VALUE IF NOT EXISTS 'CASHFREE';"))
            await db.execute(_sql_text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS payment_type VARCHAR DEFAULT 'COURSE';"))
            await db.execute(_sql_text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS exam_stage_id UUID REFERENCES exam_stages(id) ON DELETE SET NULL;"))
            await db.commit()
            print("BG: Cashfree schema self-heal completed")
    except Exception as e:
        print(f"BG: Cashfree schema self-heal skipped: {e!r}")

    # 4. Category seeding — only if the table is empty.
    try:
        async with SessionLocal() as db:
            result = await db.execute(select(Category).limit(1))
            if not result.scalars().first():
                print("BG: seeding default exam categories")
                defaults = [
                    {"name": "Bank", "icon": "library-outline"},
                    {"name": "Judicial", "icon": "hammer-outline"},
                    {"name": "ESIC", "icon": "medkit-outline"},
                    {"name": "Railway", "icon": "train-outline"},
                    {"name": "Defence", "icon": "shield-checkmark-outline"},
                    {"name": "PSUs", "icon": "business-outline"},
                    {"name": "UPSC", "icon": "ribbon-outline"},
                    {"name": "SSC", "icon": "clipboard-outline"},
                    {"name": "Police", "icon": "shield-half-outline"},
                    {"name": "PSCs", "icon": "newspaper-outline"},
                    {"name": "Post-Office", "icon": "mail-outline"},
                ]
                for i, c in enumerate(defaults):
                    db.add(Category(name=c["name"], icon_name=c["icon"], order=i, is_enabled=True))
                await db.commit()
    except Exception as e:
        print(f"BG: category seeding skipped: {e!r}")

    # 5. Visibility self-heal — flip is_enabled back to True if every row is False.
    try:
        async with SessionLocal() as db:
            total = (await db.execute(select(_sql_func.count()).select_from(Category))).scalar_one()
            enabled = (await db.execute(select(_sql_func.count()).select_from(Category).where(Category.is_enabled.is_(True)))).scalar_one()
            if total > 0 and enabled == 0:
                print(f"BG SELF-HEAL: {total} categories all disabled — restoring.")
                await db.execute(_sql_update(Category).values(is_enabled=True))
                await db.execute(_sql_update(SubCategory).values(is_enabled=True))
                await db.commit()
    except Exception as e:
        print(f"BG: visibility self-heal skipped: {e!r}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ZERO blocking before yield — Uvicorn starts accepting connections
    # (including Railway's /health check) within milliseconds of container
    # boot. Previously _admin_bootstrap blocked for up to 20s which caused
    # Railway to mark the service unhealthy on every deploy, detach the
    # custom domain, and break login until the domain was manually
    # re-attached. Now both tasks run entirely in the background.
    asyncio.create_task(_admin_bootstrap_with_timeout(timeout_seconds=60))
    asyncio.create_task(_background_schema_selfheal())
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
    is_dev = os.getenv("ENV", "production").lower() in ("dev", "development", "local")
    content: dict = {"detail": "Internal Server Error"}
    if is_dev:
        content["traceback"] = traceback.format_exc()
    return JSONResponse(status_code=500, content=content)

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
