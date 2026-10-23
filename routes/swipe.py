from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from extensions import db
from models import Company, Connection

bp = Blueprint("swipe", __name__, url_prefix="/swipe")
ACTIONS = ("passed", "saved", "interested")


def _investor_required_json():
    if not current_user.is_authenticated or current_user.role != "investor":
        return jsonify(error="Investor login required"), 401
    return None


@bp.route("/")
def index():
    # Browsing is public; require an investor account only when recording a decision.
    is_investor = current_user.is_authenticated and current_user.role == "investor"
    seen = [c.company_id for c in Connection.query.filter_by(user_id=current_user.id)] if is_investor else []
    query = Company.query
    if seen:
        query = query.filter(~Company.id.in_(seen))
    companies = query.order_by(Company.id).all()
    sectors = current_user.sector_list() if is_investor else []
    companies.sort(key=lambda c: c.category not in sectors)
    interested = Connection.query.filter_by(user_id=current_user.id, kind="interested") if is_investor else Connection.query.filter_by(id=-1)
    return render_template("swipe.html", companies=companies[:40],
        interested_count=interested.count(), recent=interested.order_by(Connection.id.desc()).limit(5).all(),
        is_investor=is_investor)


@bp.post("/act")
def act():
    denied = _investor_required_json()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    if action not in ACTIONS:
        return jsonify(error="Invalid action"), 400
    try:
        company = db.session.get(Company, int(data.get("company_id")))
    except (TypeError, ValueError):
        company = None
    if not company:
        return jsonify(error="Company not found"), 404

    # One decision per investor per company: replace any earlier one
    Connection.query.filter_by(user_id=current_user.id, company_id=company.id).delete()
    db.session.add(Connection(user_id=current_user.id, company_id=company.id, kind=action))
    db.session.commit()
    return jsonify(ok=True, action=action, company_id=company.id)


@bp.post("/undo")
def undo():
    denied = _investor_required_json()
    if denied:
        return denied
    last = (Connection.query.filter_by(user_id=current_user.id)
            .order_by(Connection.id.desc()).first())
    if not last:
        return jsonify(ok=False, error="Nothing to undo"), 404
    company_id = last.company_id
    db.session.delete(last)
    db.session.commit()
    return jsonify(ok=True, company_id=company_id)
