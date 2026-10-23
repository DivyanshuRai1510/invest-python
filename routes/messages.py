from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, and_

from extensions import db
from models import Message, User

bp = Blueprint("messages", __name__, url_prefix="/messages")


def allowed_pair(a, b):
    """Chat is open only between an investor and a founder."""
    return {a.role, b.role} == {"investor", "founder"}


def thread_query(uid):
    me = current_user.id
    return Message.query.filter(or_(
        and_(Message.sender_id == me, Message.recipient_id == uid),
        and_(Message.sender_id == uid, Message.recipient_id == me)))


@bp.route("/")
@login_required
def inbox():
    me = current_user.id
    msgs = (Message.query.filter(or_(Message.sender_id == me, Message.recipient_id == me))
            .order_by(Message.created_at.desc()).all())
    seen, threads = set(), []
    for m in msgs:
        partner_id = m.recipient_id if m.sender_id == me else m.sender_id
        if partner_id in seen:
            continue
        seen.add(partner_id)
        partner = db.session.get(User, partner_id)
        if partner:
            unread = Message.query.filter_by(sender_id=partner_id, recipient_id=me, read_at=None).count()
            threads.append({"partner": partner, "last": m, "unread": unread})
    return render_template("messages.html", threads=threads)


@bp.route("/<int:uid>", methods=["GET", "POST"])
@login_required
def thread(uid):
    other = db.get_or_404(User, uid)
    if other.id == current_user.id or not allowed_pair(current_user, other):
        flash("You can message founders and investors from each other's profiles.", "error")
        return redirect(url_for("messages.inbox"))
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if body:
            db.session.add(Message(sender_id=current_user.id, recipient_id=other.id, body=body[:4000]))
            db.session.commit()
        return redirect(url_for("messages.thread", uid=uid) + "#latest")
    msgs = thread_query(uid).order_by(Message.created_at).all()
    Message.query.filter_by(sender_id=uid, recipient_id=current_user.id, read_at=None).update(
        {"read_at": db.func.now()})
    db.session.commit()
    return render_template("thread.html", other=other, messages=msgs)


@bp.get("/<int:uid>/poll")
def poll(uid):
    if not current_user.is_authenticated:
        return jsonify(error="login required"), 401
    other = db.session.get(User, uid)
    if not other or not allowed_pair(current_user, other):
        abort(404)
    after = request.args.get("after", 0, type=int)
    new = thread_query(uid).filter(Message.id > after).order_by(Message.id).all()
    Message.query.filter_by(sender_id=uid, recipient_id=current_user.id, read_at=None).update(
        {"read_at": db.func.now()})
    db.session.commit()
    return jsonify([{"id": m.id, "body": m.body, "mine": m.sender_id == current_user.id,
                     "time": m.created_at.strftime("%d %b, %H:%M")} for m in new])
