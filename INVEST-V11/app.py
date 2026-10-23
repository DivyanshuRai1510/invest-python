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


def company_cover_url(category):
    """A category-relevant editorial cover; gradient fallback remains if remote images fail."""
    c = (category or "").lower()
    photos = [
        (("hydrogen", "fuel cell", "clean energy", "energy", "solar", "sustain"), "photo-1473341304170-971146b5b4b9"),
        (("health", "medical", "biotech"), "photo-1576091160399-112ba8d25d1d"),
        (("agri", "farm", "food"), "photo-1500382017468-9049fed747ef"),
        (("fintech", "finance", "bank"), "photo-1460925895917-afdab827c52f"),
        (("robot", "manufact", "automation"), "photo-1485827404703-89b55fcc595e"),
        (("ai", "deeptech", "software", "iot", "technology"), "photo-1518770660439-4636190af475"),
        (("education", "edtech"), "photo-1523580494863-6f3031224c94"),
    ]
    photo = next((image for keys, image in photos if any(key in c for key in keys)), "photo-1486406146926-c627a92ad1ab")
    return f"https://images.unsplash.com/{photo}?auto=format&fit=crop&w=2000&q=85"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 9 * 1024 * 1024  # 8 MB attachment budget plus multipart overhead

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
    app.jinja_env.globals.update(icon=icon, category_icon=category_icon, category_gradient=category_gradient, company_cover_url=company_cover_url)

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
        # Refresh old demo placeholder portraits to stable real-photo headshots.
        from models import User, Company as CompanyModel, Product as ProductModel
        from seed_images import investor_avatar_url, user_avatar_url, company_image_url, product_image_url
        for demo_user in User.query.filter(User.avatar.like('%picsum.photos%')).all():
            demo_user.avatar = investor_avatar_url(demo_user.name) if demo_user.role == 'investor' else user_avatar_url(demo_user.name)
        # Refresh old placeholder seed art on existing local databases as well as new installs.
        for demo_company in CompanyModel.query.filter(
                db.or_(CompanyModel.logo.like('%picsum.photos%'),
                       CompanyModel.logo.like('%images.unsplash.com%'))).all():
            # Editorial industry photos belong in the cover, not in the company-logo slot.
            # Empty logo uses the branded initials fallback in the template macro.
            demo_company.logo = ""
        for demo_product in ProductModel.query.filter(
                db.or_(ProductModel.image.like('%picsum.photos%'),
                       ProductModel.image.like('%images.unsplash.com%'))).all():
            # Replace old generic/demo imagery with the product's sector-matched image.
            demo_product.image = product_image_url(demo_product.name, demo_product.category)
        db.session.commit()
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
