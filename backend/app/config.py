from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    app_name: str = "Tebita SLA System"
    secret_key: str = "tebita-sla-secret-key-change-in-production"
    access_token_expire_minutes: int = 480  # 8 hours
    algorithm: str = "HS256"
    
    # Database
    database_url: str = "sqlite:///./tebita.db"
    
    # CORS - Allow specific origins for credentials support
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://192.168.100.88:5173",  # Local Network Access
        "*",  # Allow all origins for development
    ]
    
    # Celery/Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Email Notifications
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@tebitambulance.com"
    SMTP_FROM_NAME: str = "Tebita SLA System"
    FRONTEND_URL: str = "http://localhost:5174"
    
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""



settings = Settings()
