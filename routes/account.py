from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import SECTOR_OPTIONS, Connection, Product, ProductEnquiry
from utils import save_upload

bp = Blueprint("account", __name__)
CR = 10_000_000


def _cr_to_rupees(value):
    try:
        return int(float(value) * CR)
    except (TypeError, ValueError):
        return 0


@bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "founder":
        company = current_user.company
        interests, enquiries = [], []
        if company:
            interests = (Connection.query.filter_by(company_id=company.id, kind="interested")
                         .order_by(Connection.created_at.desc()).all())
            enquiries = (ProductEnquiry.query.join(Product)
                         .filter(Product.company_id == company.id)
                         .order_by(ProductEnquiry.created_at.desc()).all())
        return render_template("dashboard.html", company=company, interests=interests, enquiries=enquiries)

    saved = Connection.query.filter_by(user_id=current_user.id, kind="saved").all()
    interested = Connection.query.filter_by(user_id=current_user.id, kind="interested").all()
    return render_template("dashboard.html", saved=saved, interested=interested)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if request.form.get("action") == "password":
            new_pw = request.form.get("new_password", "")
            if not current_user.check_password(request.form.get("current_password", "")):
                flash("Your current password is not correct.", "error")
            elif len(new_pw) < 6:
                flash("The new password must be at least 6 characters.", "error")
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash("Password updated.", "success")
        else:
            u = current_user
            u.name = request.form.get("name", "").strip() or u.name
            u.title = request.form.get("title", "").strip()
            u.firm = request.form.get("firm", "").strip()
            u.location = request.form.get("location", "").strip()
            u.bio = request.form.get("bio", "").strip()
            avatar = save_upload(request.files.get("avatar"), "avatars")
            if avatar:
                u.avatar = avatar
            if u.role == "investor":
                u.sectors = ", ".join(s for s in request.form.getlist("sectors") if s in SECTOR_OPTIONS)
                u.ticket_min = _cr_to_rupees(request.form.get("ticket_min"))
                u.ticket_max = _cr_to_rupees(request.form.get("ticket_max"))
            db.session.commit()
            flash("Profile saved.", "success")
        return redirect(url_for("account.profile"))
    return render_template("profile.html", sectors=SECTOR_OPTIONS)
