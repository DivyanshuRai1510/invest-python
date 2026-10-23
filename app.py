from flask import Flask, render_template
from flask_login import current_user

from config import Config
from extensions import db, login_manager
from icons import category_gradient, category_icon, icon
from models import SECTOR_OPTIONS, Connection, Message

POPULAR = ["AI", "HealthTech", "AgriTech", "FinTech", "Hydrogen", "Robotics"]


def inr(value):
    """Indian digit grouping: 1234567 -> 12,34,567"""
    s = str(int(value or 0))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB uploads

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "error"

    from routes.account import bp as account_bp
    from routes.api import bp as api_bp
    from routes.auth import bp as auth_bp
    from routes.company import bp as company_bp
    from routes.main import bp as main_bp
    from routes.messages import bp as messages_bp
    from routes.swipe import bp as swipe_bp

    for bp in (main_bp, auth_bp, company_bp, swipe_bp, messages_bp, account_bp, api_bp):
        app.register_blueprint(bp)

    app.jinja_env.filters["crore"] = lambda v: f"₹{(v or 0) / 1e7:.2f} Cr"
    app.jinja_env.filters["inr"] = inr
    app.jinja_env.globals.update(icon=icon, category_icon=category_icon, category_gradient=category_gradient)

    @app.context_processor
    def inject_globals():
        unread = notes = 0
        if current_user.is_authenticated:
            unread = Message.query.filter_by(recipient_id=current_user.id, read_at=None).count()
            if current_user.role == "founder" and current_user.company:
                notes = Connection.query.filter_by(company_id=current_user.company.id, kind="interested").count()
        return {"popular": POPULAR, "sector_options": SECTOR_OPTIONS,
                "unread_count": unread, "notification_count": notes}

    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_error(e):
        code = getattr(e, "code", 500) or 500
        return render_template("error.html", code=code), code

    with app.app_context():
        db.create_all()
        if app.config["SEED_DEMO_DATA"]:
            from seed import seed_if_empty
            seed_if_empty()

    @app.cli.command("reseed")
    def reseed():
        """Wipe the database and reload all sample data."""
        from seed import seed_all
        db.drop_all()
        db.create_all()
        seed_all()
        print("Database reset. Sample data loaded.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
