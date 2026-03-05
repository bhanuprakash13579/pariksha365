import asyncio
from app.core.database import async_session_maker
from app.core.dependencies import get_current_user
from app.schemas.user_schema import UserResponse

async def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzI5MDk5MTIsInN1YiI6IjUzYzc5YzQ2LTA1NzItNDA1Yy1hNjg3LWMyMDk5MDdhOTIwYyIsInR5cGUiOiJhY2Nlc3MifQ.NC9eozVBBMzqplDv632uTEY553FS-Tlnl2Wgl8W7ZhM"
    async with async_session_maker() as db:
        user = await get_current_user(db, token)
        print("User fetched from DB:", user.email, user.role.name if user.role else "No Role")
        try:
            resp = UserResponse.model_validate(user)
            print("Success:", resp)
        except Exception as e:
            print("Error validating UserResponse:")
            print(e)

if __name__ == "__main__":
    asyncio.run(main())
