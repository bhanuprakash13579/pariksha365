"""
One-time script to create an Admin role and admin user in the local SQLite database.
Run with: python create_admin.py
"""
import asyncio
import uuid
from app.core.database import async_session_maker, engine, Base
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.future import select
import app.models  # ensure all models are loaded

ADMIN_EMAIL = "admin@pariksha365.in"
ADMIN_PASSWORD = "Admin@365"
ADMIN_NAME = "Admin"

async def main():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # 1. Ensure "Admin" role exists
        stmt = select(Role).where(Role.name == "Admin")
        result = await db.execute(stmt)
        admin_role = result.scalars().first()
        
        if not admin_role:
            admin_role = Role(name="Admin")
            db.add(admin_role)
            await db.commit()
            await db.refresh(admin_role)
            print(f"✅ Created 'Admin' role (id: {admin_role.id})")
        else:
            print(f"ℹ️  'Admin' role already exists (id: {admin_role.id})")

        # 2. Ensure "Student" role exists too
        stmt2 = select(Role).where(Role.name == "Student")
        result2 = await db.execute(stmt2)
        student_role = result2.scalars().first()
        if not student_role:
            student_role = Role(name="Student")
            db.add(student_role)
            await db.commit()
            print("✅ Created 'Student' role")

        # 3. Create admin user
        stmt3 = select(User).where(User.email == ADMIN_EMAIL)
        result3 = await db.execute(stmt3)
        existing = result3.scalars().first()
        
        if existing:
            # Update role to admin if not already
            if existing.role_id != admin_role.id:
                existing.role_id = admin_role.id
                await db.commit()
                print(f"✅ Updated existing user '{ADMIN_EMAIL}' to Admin role")
            else:
                print(f"ℹ️  Admin user '{ADMIN_EMAIL}' already exists with Admin role")
        else:
            admin_user = User(
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                password_hash=get_password_hash(ADMIN_PASSWORD),
                role_id=admin_role.id,
                is_active=True,
            )
            db.add(admin_user)
            await db.commit()
            print(f"✅ Created admin user: {ADMIN_EMAIL}")

        print(f"\n🔑 Admin Credentials:")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")

asyncio.run(main())
