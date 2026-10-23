from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for, send_from_directory
from flask_login import current_user, login_required
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
from models import MessageAttachment

from extensions import db
from models import Message, User

bp = Blueprint("messages", __name__, url_prefix="/messages")

@bp.app_template_global("rich_message_lines")
def rich_message_lines(body):
    """Convert legacy location/contact text into safe typed data for server rendering.
    Duplicate lines are collapsed so old messages don't repeat the same share.
    """
    import re
    result = []
    seen = set()
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line or line in seen:
            continue
        seen.add(line)
        match = re.fullmatch(r"My location:\\s*(https?://maps\\.google\\.com/\\?q=[^\\s]+)", line, re.I)
        if match:
            result.append({"kind": "location", "url": match.group(1)})
        elif line.startswith("Contact card:"):
            result.append({"kind": "contact", "text": line[len("Contact card:"):].strip()})
        else:
            result.append({"kind": "text", "text": line})
    return result



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
        files = [f for f in request.files.getlist("files") if f and f.filename]
        if len(files) > 8:
            flash("You can attach up to 8 files per message.", "error")
            return redirect(url_for("messages.thread", uid=uid))
        total_bytes = 0
        for upload in files:
            try:
                upload.stream.seek(0, 2)
                total_bytes += upload.stream.tell()
                upload.stream.seek(0)
            except (OSError, AttributeError):
                pass
        if total_bytes > 8 * 1024 * 1024:
            flash("The combined attachments must be 8 MB or smaller.", "error")
            return redirect(url_for("messages.thread", uid=uid))
        if body or files:
            upload_dir = Path(current_app.instance_path) / "message_uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            msg = Message(sender_id=current_user.id, recipient_id=other.id, body=(body or f"Shared {len(files)} attachment(s).")[:4000])
            db.session.add(msg)
            db.session.flush()
            for file in files:
                safe_name = secure_filename(file.filename) or "attachment"
                stored = f"{uuid.uuid4().hex}_{safe_name}"
                file.save(upload_dir / stored)
                db.session.add(MessageAttachment(message_id=msg.id, original_name=safe_name[:255], stored_name=stored, mime_type=file.mimetype or "application/octet-stream", size_bytes=(upload_dir / stored).stat().st_size))
            db.session.commit()
        return redirect(url_for("messages.thread", uid=uid) + "#latest")
    msgs = thread_query(uid).order_by(Message.created_at).all()
    Message.query.filter_by(sender_id=uid, recipient_id=current_user.id, read_at=None).update(
        {"read_at": db.func.now()})
    db.session.commit()
    return render_template("thread.html", other=other, messages=msgs)


@bp.get("/<int:uid>/attachment/<int:attachment_id>")
@login_required
def download_attachment(uid, attachment_id):
    other = db.session.get(User, uid)
    if not other or other.id == current_user.id or not allowed_pair(current_user, other):
        abort(404)
    attachment = db.session.get(MessageAttachment, attachment_id)
    if not attachment:
        abort(404)
    msg = attachment.message
    # The attachment must belong to this exact conversation, not merely another conversation involving either user.
    if {msg.sender_id, msg.recipient_id} != {current_user.id, other.id}:
        abort(404)
    folder = Path(current_app.instance_path) / "message_uploads"
    inline = request.args.get("inline") == "1" and (attachment.mime_type or "").startswith("image/")
    return send_from_directory(folder, attachment.stored_name, as_attachment=not inline,
                              download_name=attachment.original_name, mimetype=attachment.mime_type)


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
    result = []
    for m in new:
        attachments = []
        for a in m.attachments:
            base = url_for("messages.download_attachment", uid=uid, attachment_id=a.id)
            attachments.append({
                "name": a.original_name,
                "mime_type": a.mime_type or "application/octet-stream",
                "size_bytes": a.size_bytes or 0,
                "url": base,
                "inline_url": base + "?inline=1",
            })
        result.append({"id": m.id, "body": m.body, "mine": m.sender_id == current_user.id,
                       "time": m.created_at.strftime("%d %b, %H:%M"), "attachments": attachments})
    return jsonify(result)
