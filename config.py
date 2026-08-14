import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect(("dpg-d9mnkj61egvs73ei202g-a.oregon-postgres.render.com", 5432))
            s.close()
            db_url = "postgresql://nutrimeal_db_user:9KzZDtQKehdCwmkefUnFoX7Ljm21onP5@dpg-d9mnkj61egvs73ei202g-a.oregon-postgres.render.com/nutrimeal_db?sslmode=require"
        except Exception:
            db_url = f"sqlite:///{os.path.join(BASE_DIR, 'nutrition_app.db')}"
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

