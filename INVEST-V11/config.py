import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Default: SQLite file next to the project. Set DATABASE_URL to use MySQL/Postgres on a server.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "invest.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEED_DEMO_DATA = os.environ.get("SEED_DEMO_DATA", "1") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
