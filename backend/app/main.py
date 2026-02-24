from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth_router, user_router, admin_router, test_series_router, attempt_router, payment_router, course_router, category_router
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically drop and create database tables on startup (WIPES DATA!)
    async with engine.begin() as conn:
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
                {"name": "UPSC Civil Services", "icon": "ribbon-outline", "subs": ["UPSC CSE", "UPSC EPFO (APFC)", "UPSC CDS"]},
                {"name": "State Govt. Exams", "icon": "business-outline", "subs": ["UPPSC", "BPSC", "MPSC", "APPSC", "TSPSC"]},
                {"name": "SSC Exams", "icon": "hammer-outline", "subs": ["SSC CGL", "SSC CHSL", "SSC MTS", "SSC GD"]},
                {"name": "Railways", "icon": "train-outline", "subs": ["RRB NTPC", "RRB Group D", "RRB ALP"]},
                {"name": "Defence Exams", "icon": "shield-checkmark-outline", "subs": ["NDA", "AFCAT", "Airforce X & Y"]},
                {"name": "Teaching Exams", "icon": "book-outline", "subs": ["CTET", "UPTET", "KVS", "Super TET"]}
            ]
            for i, c in enumerate(defaults):
                cat_db = Category(name=c["name"], icon_name=c["icon"], order=i)
                db.add(cat_db)
                await db.commit()
                await db.refresh(cat_db)
                for j, sub in enumerate(c["subs"]):
                    db.add(SubCategory(category_id=cat_db.id, name=sub, order=j))
            await db.commit()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace abstract with true domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(user_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(admin_router.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(test_series_router.router, prefix=f"{settings.API_V1_STR}/tests", tags=["test-series"])
app.include_router(course_router.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(attempt_router.router, prefix=f"{settings.API_V1_STR}/attempts", tags=["attempts"])
app.include_router(payment_router.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])
app.include_router(category_router.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])

from fastapi.responses import HTMLResponse

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
            
            <h2>6. Your Rights</h2>
            <p>You have the right to access, update, or request the deletion of your personal data. You can delete your account directly inside the app settings at any time.</p>
            
            <h2>7. Contact Us</h2>
            <p>If you have any questions regarding this Privacy Policy, please contact us at: support@pariksha365.in</p>
        </div>
    </body>
    </html>
    """
