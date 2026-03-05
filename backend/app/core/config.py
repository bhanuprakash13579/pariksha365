from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pariksha365 Platform"
    API_V1_STR: str = "/api/v1"
    
    # POSTGRES
    PGHOST: str = ""
    PGPORT: str = ""
    PGUSER: str = ""
    PGPASSWORD: str = ""
    PGDATABASE: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    DATABASE_URL: str
    
    # SECURITY
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # STRIPE
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # AI MODELS / THIRD PARTY
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    CLOUDINARY_URL: str = ""
    
    # Cloudflare R2 Storage Config
    R2_ENDPOINT_URL: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "pariksha365-tests"
    R2_PUBLIC_DOMAIN: str = ""
    
    # FRONTEND URL (for payment redirects etc.)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # GOOGLE OAUTH CLIENT IDS (from frontend)
    GOOGLE_CLIENT_IDS: list[str] = [
        "592393648560-0csjsd0dvukv94qg05np14rj1v3o9gg2.apps.googleusercontent.com", # iOS
        "592393648560-70fdb8qfubom1sllvmb29ststk1h1k0v.apps.googleusercontent.com", # Web (LoginScreen)
        "592393648560-o4ou87jvmv6tj3uura8ls27td06pv0o5.apps.googleusercontent.com", # Web (App.tsx)
        "592393648560-tk26aam18hnsd38dskfkt64td6l23ebv.apps.googleusercontent.com", # Android (LoginScreen)
        "592393648560-rpddhav13tiikcpgki71kvlegmi3s91c.apps.googleusercontent.com", # Android (App.tsx)
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
