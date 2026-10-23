# Entry point for production servers (gunicorn, Docker, etc.)
from app import app

if __name__ == "__main__":
    app.run()
