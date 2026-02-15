from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Udaan API"
    env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    video_signing_secret: str = "video-secret"
    database_url: str = "sqlite:///./udaan.db"
    local_storage_path: str = "./storage"
    public_base_url: str = "http://localhost:8000"

    admin_email: str = ""
    admin_password: str = ""
    admin_full_name: str = ""
    admin_phone: str = ""
    admin_grade: str = ""

    superadmin_email: str = "meet@dashovia.com"
    superadmin_password: str = "Mahantam#6559"
    superadmin_full_name: str = "Meet Jethwa"
    superadmin_phone: str = "9000000000"
    superadmin_grade: str = "NA"

    teacher_name: str = "Arts Teacher"

    sonar_api_key: str = ""
    openai_api_key: str = ""
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""
    admin_subscription_price_inr: int = 11000
    superadmin_commission_pct: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
