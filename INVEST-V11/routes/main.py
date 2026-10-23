from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from extensions import db
from models import SECTOR_OPTIONS, Company, Event, EventRSVP, Product, ProductEnquiry, User

bp = Blueprint("main", __name__)

CR = 10_000_000
STOP_WORDS = {"startup", "startups", "related", "company", "companies", "the", "and", "for", "in", "of"}
PROFIT_RANGES = {"lt1": (None, 1), "1-10": (1, 10), "10-50": (10, 50), "gt50": (50, None)}
STAGES = ["Bootstrapped", "Seed", "Series A", "Series B", "Series B+"]
COMPANY_SORTS = {
    "relevant": Company.id,
    "profit": Company.annual_profit.desc(),
    "value": Company.market_value.desc(),
    "growth": Company.growth_percent.desc(),
    "newest": Company.founded.desc(),
}
PRODUCT_SORTS = {
    "relevant": Product.id,
    "price_asc": Product.price.asc(),
    "price_desc": Product.price.desc(),
    "rating": Product.rating.desc(),
}
PER_PAGE_COMPANIES = 12
PER_PAGE_PRODUCTS = 12
PER_PAGE_INVESTORS = 12
PER_PAGE_EVENTS = 10


def _like(text):
    return f"%{text}%"


def _qargs():
    """Current query-string arguments without the page number, so pager links keep filters."""
    return {k: v for k, v in request.args.items() if k != "page"}


def _view():
    return "grid" if request.args.get("view") == "grid" else "list"


@bp.route("/")
def home():
    return render_template(
        "home.html",
        featured_products=Product.query.filter(Product.badge != "").order_by(Product.rating.desc()).limit(8).all(),
        featured_companies=Company.query.order_by(Company.market_value.desc()).limit(4).all(),
        events=Event.query.filter(Event.start_date >= datetime.utcnow()).order_by(Event.start_date).limit(4).all(),
        stats={"startups": Company.query.count(),
               "investors": User.query.filter_by(role="investor").count(),
               "products": Product.query.count(),
               "events": Event.query.count()},
        categories=SECTOR_OPTIONS,
    )


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    stage = request.args.get("stage", "").strip()
    location = request.args.get("location", "").strip()
    profit = request.args.get("profit", "").strip()
    sort = request.args.get("sort", "relevant")
    page = request.args.get("page", 1, type=int)

    query = Company.query
    words = [w for w in q.split() if len(w) > 1 and w.lower() not in STOP_WORDS]
    if words:
        conds = []
        for w in words:
            like = _like(w)
            conds += [Company.name.ilike(like), Company.tagline.ilike(like),
                      Company.description.ilike(like), Company.category.ilike(like)]
        query = query.filter(or_(*conds))
    if category:
        query = query.filter(Company.category == category)
    if stage:
        query = query.filter(Company.funding_stage == stage)
    if location:
        query = query.filter(Company.location.ilike(_like(location)))
    if profit in PROFIT_RANGES:
        lo, hi = PROFIT_RANGES[profit]
        if lo is not None:
            query = query.filter(Company.annual_profit >= lo * CR)
        if hi is not None:
            query = query.filter(Company.annual_profit < hi * CR)

    results = query.order_by(COMPANY_SORTS.get(sort, Company.id)).paginate(
        page=page, per_page=PER_PAGE_COMPANIES, error_out=False)
    return render_template("search.html", results=results, q=q, category=category, stage=stage,
                           location=location, profit=profit, sort=sort, view=_view(),
                           categories=SECTOR_OPTIONS, stages=STAGES, qargs=_qargs())


# ---------- Products ----------

@bp.route("/products")
def products():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "relevant")
    page = request.args.get("page", 1, type=int)

    query = Product.query
    if q:
        like = _like(q)
        query = query.filter(or_(Product.name.ilike(like), Product.maker.ilike(like),
                                 Product.description.ilike(like)))
    if category:
        query = query.filter(Product.category == category)
    results = query.order_by(PRODUCT_SORTS.get(sort, Product.id)).paginate(
        page=page, per_page=PER_PAGE_PRODUCTS, error_out=False)
    return render_template("products.html", results=results, q=q, category=category, sort=sort,
                           view=_view(), categories=SECTOR_OPTIONS, qargs=_qargs())


@bp.route("/products/<int:pid>")
def product_detail(pid):
    product = db.get_or_404(Product, pid)
    more = (Product.query.filter(Product.category == product.category, Product.id != product.id)
            .limit(4).all())
    is_owner = bool(current_user.is_authenticated and product.company
                    and product.company.owner_id == current_user.id)
    return render_template("product_detail.html", product=product, more=more, is_owner=is_owner)


@bp.post("/products/<int:pid>/enquire")
def enquire(pid):
    product = db.get_or_404(Product, pid)
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    if not name or "@" not in email or not message:
        flash("Enter your name, a valid email and a message.", "error")
    else:
        db.session.add(ProductEnquiry(
            product_id=product.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            name=name, email=email, message=message))
        db.session.commit()
        flash(f"Your enquiry was sent to {product.maker}.", "success")
    return redirect(url_for("main.product_detail", pid=pid))


# ---------- Events ----------

@bp.route("/events")
def events():
    location = request.args.get("location", "").strip()
    page = request.args.get("page", 1, type=int)
    query = Event.query
    if location:
        query = query.filter(Event.location.ilike(_like(location)))
    results = query.order_by(Event.start_date).paginate(page=page, per_page=PER_PAGE_EVENTS, error_out=False)
    registered = set()
    if current_user.is_authenticated:
        registered = {r.event_id for r in EventRSVP.query.filter_by(user_id=current_user.id)}
    locations = sorted({e.location for e in Event.query.all()})
    return render_template("events.html", results=results, registered=registered,
                           location=location, locations=locations, qargs=_qargs())


@bp.post("/events/<int:eid>/rsvp")
@login_required
def rsvp(eid):
    db.get_or_404(Event, eid)
    existing = EventRSVP.query.filter_by(user_id=current_user.id, event_id=eid).first()
    if existing:
        db.session.delete(existing)
        flash("Registration cancelled.", "success")
    else:
        db.session.add(EventRSVP(user_id=current_user.id, event_id=eid))
        flash("You are registered for this event.", "success")
    db.session.commit()
    return redirect(request.form.get("next") or url_for("main.events"))


# ---------- Investors ----------

@bp.route("/investors")
def investors():
    q = request.args.get("q", "").strip()
    sector = request.args.get("sector", "").strip()
    location = request.args.get("location", "").strip()
    page = request.args.get("page", 1, type=int)

    query = User.query.filter(User.role == "investor")
    if q:
        like = _like(q)
        query = query.filter(or_(User.name.ilike(like), User.firm.ilike(like), User.title.ilike(like)))
    if sector:
        query = query.filter(User.sectors.ilike(_like(sector)))
    if location:
        query = query.filter(User.location.ilike(_like(location)))
    results = query.order_by(User.name).paginate(page=page, per_page=PER_PAGE_INVESTORS, error_out=False)
    return render_template("investors.html", results=results, q=q, sector=sector, location=location,
                           sectors=SECTOR_OPTIONS, qargs=_qargs())


@bp.route("/investors/<int:uid>")
def investor(uid):
    user = db.get_or_404(User, uid)
    if user.role != "investor":
        abort(404)
    sectors = user.sector_list()
    matches = []
    if sectors:
        matches = (Company.query.filter(Company.category.in_(sectors))
                   .order_by(Company.market_value.desc()).limit(6).all())
    return render_template("investor.html", investor=user, matches=matches)
