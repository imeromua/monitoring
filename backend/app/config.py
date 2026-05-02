from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Telegram
    BOT_TOKEN: str
    SUPERADMIN_TELEGRAM_ID: int
    MINI_APP_URL: str = "https://your-domain.com"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 8

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    REPORT_RECIPIENTS: str  # comma-separated emails

    # Reports
    REPORTS_DIR: str = "/tmp/reports"
    REPORT_TTL_HOURS: int = 2

    @property
    def report_recipients_list(self) -> list[str]:
        return [e.strip() for e in self.REPORT_RECIPIENTS.split(",")]

    @property
    def reports_path(self) -> Path:
        path = Path(self.REPORTS_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
