import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _db_uri():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return "mysql+pymysql://{u}:{p}@{h}:{port}/{n}?charset=utf8mb4".format(
        u=os.getenv("DB_USER", "root"),
        p=quote_plus(os.getenv("DB_PASSWORD", "")),
        h=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "3306"),
        n=os.getenv("DB_NAME", "customer_support_db"),
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
    SQLALCHEMY_DATABASE_URI = _db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "480"))
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
    UPLOAD_FOLDER = os.path.abspath(
        os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "uploads"))
    )
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
    MAX_CONTENT_LENGTH = (int(os.getenv("MAX_UPLOAD_MB", "5")) + 1) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt", "docx"}
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"

    MAIL_ENABLED = os.getenv("MAIL_ENABLED", "false").lower() == "true"
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "helpdesk@example.com")

    AI_PROVIDER = os.getenv("AI_PROVIDER", "none").lower()
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "15"))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    RATELIMIT_ENABLED = False
    MAIL_ENABLED = False
    AI_PROVIDER = "none"
    SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
