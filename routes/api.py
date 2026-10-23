from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from models import Company, Event, Product

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/companies")
def companies():
    q, category = request.args.get("q", "").strip(), request.args.get("category", "").strip()
    query = Company.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Company.name.ilike(like), Company.tagline.ilike(like),
                                 Company.category.ilike(like)))
    if category:
        query = query.filter(Company.category == category)
    return jsonify([c.to_dict() for c in query.order_by(Company.id)])


@bp.get("/companies/<slug>")
def company(slug):
    c = Company.query.filter_by(slug=slug).first_or_404()
    data = c.to_dict()
    data["sections"] = [{"type": s.type, "title": s.title, "content": s.content}
                        for s in c.sections if s.visible]
    return jsonify(data)


@bp.get("/products")
def products():
    return jsonify([{"id": p.id, "name": p.name, "maker": p.maker, "category": p.category,
                     "price": p.price, "rating": p.rating} for p in Product.query.order_by(Product.id)])


@bp.get("/events")
def events():
    return jsonify([{"id": e.id, "title": e.title, "location": e.location,
                     "start_date": e.start_date.isoformat()}
                    for e in Event.query.order_by(Event.start_date)])
