from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from extensions import db
from models import User

bp = Blueprint("auth", __name__)


def safe_next(target):
    return target if target and target.startswith("/") and not target.startswith("//") else None


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "investor")
        if role not in ("founder", "investor"):
            role = "investor"
        if not name or "@" not in email or len(password) < 6:
            flash("Enter your name, a valid email and a password of at least 6 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists. Try logging in.", "error")
        else:
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            if role == "founder":
                flash("Account created. Now register your startup.", "success")
                return redirect(url_for("company.new"))
            flash("Account created. Complete your investor profile to get better matches.", "success")
            return redirect(url_for("account.profile"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").strip().lower()).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user)
            return redirect(safe_next(request.args.get("next")) or url_for("account.dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))
