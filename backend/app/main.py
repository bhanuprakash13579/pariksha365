from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth_router, user_router, admin_router, test_series_router, attempt_router, payment_router, course_router, category_router, analytics_router, search_router, quiz_router, exam_structure_router, private_module_router
import app.models

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically drop and create database tables on startup (WIPES DATA!)
    async with engine.begin() as conn:
        if os.getenv("WIPE_DB_ON_STARTUP") == "True":
            print("WIPE_DB_ON_STARTUP flag is enabled. Dropping all tables...")
            if engine.dialect.name == "postgresql":
                from sqlalchemy import text
                print("Postgres dialect detected. Dropping old dependent tables via CASCADE...")
                await conn.execute(text("DROP TABLE IF EXISTS options CASCADE;"))
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    from app.core.database import SessionLocal
    from app.models.category import Category
    from app.models.subcategory import SubCategory
    from sqlalchemy.future import select

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

        # ADMIN BOOTSTRAP — simple and unconditional.
        #
        # Contract (user-preferred, 2026-04-21): as long as
        # ADMIN_BOOTSTRAP_PASSWORD is set in the Railway env, the admin user
        # logs in with exactly that password. Every time. No force flag, no
        # dance with another env var.
        #
        # If the admin user does not exist, create it. If it exists, re-hash
        # the password to match the env value and make sure role +
        # is_active are correct. Idempotent: same env value on every boot
        # means no effective change.
        #
        # Trade-off: if you change the admin password via the UI, the next
        # redeploy will reset it back to ADMIN_BOOTSTRAP_PASSWORD. This is
        # the desired behaviour — the env var is the single source of truth.
        admin_boot_pw = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "").strip()
        if admin_boot_pw:
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

                user_res = await db.execute(select(User).where(User.email == admin_email))
                admin_user = user_res.scalars().first()
                if admin_user is None:
                    admin_user = User(
                        name=admin_name,
                        email=admin_email,
                        password_hash=get_password_hash(admin_boot_pw),
                        role_id=admin_role.id,
                        is_active=True,
                    )
                    db.add(admin_user)
                    await db.commit()
                    print(f"ADMIN BOOTSTRAP: created admin user {admin_email}")
                else:
                    admin_user.role_id = admin_role.id
                    admin_user.password_hash = get_password_hash(admin_boot_pw)
                    admin_user.is_active = True
                    await db.commit()
                    print(
                        f"ADMIN BOOTSTRAP: ensured {admin_email} has env-matching password "
                        "(role + is_active reconciled)."
                    )
            except Exception as e:
                print(f"ADMIN BOOTSTRAP failed: {e!r}")

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
