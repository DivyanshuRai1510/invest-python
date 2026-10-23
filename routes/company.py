from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import SECTION_TYPES, SECTOR_OPTIONS, Company, CompanyDocument, Connection, Product, Section, default_sections, slugify
from utils import DOC_EXT, IMAGE_EXT, save_upload

bp = Blueprint("company", __name__)
STAGES = ["Bootstrapped", "Seed", "Series A", "Series B", "Series B+"]
CR = 10_000_000
TABS = ("overview", "products", "documents", "team", "investors")


def num(value, cast=float, default=0):
    try:
        return cast(value)
    except (TypeError, ValueError):
        return default


def owned_company(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    if not current_user.is_authenticated or company.owner_id != current_user.id:
        abort(403)
    return company


def fill_company(company, form):
    company.name = form.get("name", "").strip()
    company.tagline = form.get("tagline", "").strip()
    company.description = form.get("description", "").strip()
    company.category = form.get("category", "").strip()
    company.location = form.get("location", "").strip()
    company.website = form.get("website", "").strip()
    company.funding_stage = form.get("funding_stage") if form.get("funding_stage") in STAGES else "Seed"
    company.founded = num(form.get("founded"), int, 2024)
    company.employees = num(form.get("employees"), int, 0)
    company.growth_percent = num(form.get("growth_percent"), float, 0)
    company.annual_profit = int(num(form.get("annual_profit")) * CR)
    company.market_value = int(num(form.get("market_value")) * CR)
    company.revenue = int(num(form.get("revenue")) * CR)


def add_documents(company, files):
    for f in files:
        path = save_upload(f, "docs", DOC_EXT)
        if path:
            db.session.add(CompanyDocument(company_id=company.id, name=f.filename.rsplit(".", 1)[0][:200],
                                           file_path=path))


@bp.route("/company/<slug>")
def detail(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    tab = request.args.get("tab", "overview")
    if tab not in TABS:
        tab = "overview"
    marks = set()
    if current_user.is_authenticated:
        marks = {c.kind for c in Connection.query.filter_by(user_id=current_user.id, company_id=company.id)}
    is_owner = current_user.is_authenticated and company.owner_id == current_user.id
    visible = [s for s in company.sections if s.visible]
    return render_template(
        "company.html", company=company, tab=tab, marks=marks, is_owner=is_owner,
        overview_sections=[s for s in visible if s.type not in ("team", "documents", "products")],
        team_section=next((s for s in visible if s.type == "team"), None),
        documents_section=next((s for s in visible if s.type == "documents"), None),
        investor_count=Connection.query.filter_by(company_id=company.id, kind="interested").count(),
    )


@bp.post("/company/<slug>/connect")
@login_required
def connect(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    kind = request.form.get("kind")
    if kind not in ("saved", "interested"):
        abort(400)
    if current_user.role != "investor":
        flash("Only investor accounts can save startups or show interest.", "error")
        return redirect(url_for("company.detail", slug=slug))
    existing = Connection.query.filter_by(user_id=current_user.id, company_id=company.id, kind=kind).first()
    Connection.query.filter_by(user_id=current_user.id, company_id=company.id).delete()
    if existing:
        flash("Removed from your list.", "success")
    else:
        db.session.add(Connection(user_id=current_user.id, company_id=company.id, kind=kind))
        flash("Saved to your dashboard." if kind == "saved" else "Your interest was sent to the founder.", "success")
    db.session.commit()
    return redirect(url_for("company.detail", slug=slug))


@bp.route("/company/new", methods=["GET", "POST"])
@login_required
def new():
    if current_user.role != "founder":
        flash("Register as a founder to add a startup page.", "error")
        return redirect(url_for("main.home"))
    if current_user.company:
        return redirect(url_for("company.edit", slug=current_user.company.slug))
    if request.method == "POST":
        company = Company(owner_id=current_user.id)
        fill_company(company, request.form)
        if not company.name or not company.category or not company.location:
            flash("Company name, sector and location are required.", "error")
            return render_template("company_form.html", company=None, stages=STAGES, is_new=True)
        base, slug, n = slugify(company.name), slugify(company.name), 2
        while Company.query.filter_by(slug=slug).first():
            slug, n = f"{base}-{n}", n + 1
        company.slug = slug
        company.logo = save_upload(request.files.get("logo"), "logos") or ""
        db.session.add(company)
        db.session.flush()
        for s in default_sections(company):
            db.session.add(s)
        add_documents(company, request.files.getlist("documents"))
        db.session.commit()
        flash("Your startup is registered. Add products and sections to complete the page.", "success")
        return redirect(url_for("company.products_manage", slug=company.slug))
    return render_template("company_form.html", company=None, stages=STAGES, is_new=True)


@bp.route("/company/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug):
    company = owned_company(slug)
    if request.method == "POST":
        fill_company(company, request.form)
        logo = save_upload(request.files.get("logo"), "logos")
        if logo:
            company.logo = logo
        add_documents(company, request.files.getlist("documents"))
        db.session.commit()
        flash("Company details saved.", "success")
        return redirect(url_for("company.detail", slug=company.slug))
    return render_template("company_form.html", company=company, stages=STAGES, is_new=False)


@bp.post("/company/<slug>/documents/<int:doc_id>/delete")
@login_required
def delete_document(slug, doc_id):
    company = owned_company(slug)
    doc = db.get_or_404(CompanyDocument, doc_id)
    if doc.company_id != company.id:
        abort(403)
    db.session.delete(doc)
    db.session.commit()
    flash("Document removed.", "success")
    return redirect(url_for("company.detail", slug=slug, tab="documents"))


# ---------- Products of a registered startup ----------

@bp.route("/company/<slug>/products", methods=["GET", "POST"])
@login_required
def products_manage(slug):
    company = owned_company(slug)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = num(request.form.get("price"), int, -1)
        if not name or price < 0:
            flash("Product name and a valid price are required.", "error")
        else:
            db.session.add(Product(
                company_id=company.id, maker=company.name, name=name,
                category=company.category,
                description=request.form.get("description", "").strip(),
                price=price,
                badge=request.form.get("badge") if request.form.get("badge") in ("", "New Launch", "Bestseller") else "",
                image=save_upload(request.files.get("image"), "products") or "",
            ))
            db.session.commit()
            flash("Product added. It now appears on the marketplace.", "success")
        return redirect(url_for("company.products_manage", slug=slug))
    return render_template("products_manage.html", company=company, product=None)


@bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def product_edit(pid):
    product = db.get_or_404(Product, pid)
    if not product.company or product.company.owner_id != current_user.id:
        abort(403)
    company = product.company
    if request.method == "POST":
        product.name = request.form.get("name", "").strip() or product.name
        product.description = request.form.get("description", "").strip()
        product.price = num(request.form.get("price"), int, product.price)
        product.badge = request.form.get("badge") if request.form.get("badge") in ("", "New Launch", "Bestseller") else ""
        image = save_upload(request.files.get("image"), "products")
        if image:
            product.image = image
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("company.products_manage", slug=company.slug))
    return render_template("products_manage.html", company=company, product=product)


@bp.post("/products/<int:pid>/delete")
@login_required
def product_delete(pid):
    product = db.get_or_404(Product, pid)
    if not product.company or product.company.owner_id != current_user.id:
        abort(403)
    slug = product.company.slug
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("company.products_manage", slug=slug))


# ---------- Page sections ----------

@bp.route("/company/<slug>/sections", methods=["GET", "POST"])
@login_required
def sections(slug):
    company = owned_company(slug)
    if request.method == "POST":
        stype = request.form.get("type")
        if stype not in SECTION_TYPES:
            abort(400)
        nxt = max([s.order_index for s in company.sections], default=-1) + 1
        db.session.add(Section(company=company, type=stype,
                               title=request.form.get("title", "").strip() or SECTION_TYPES[stype],
                               content=request.form.get("content", "").strip(), order_index=nxt))
        db.session.commit()
        flash("Section added.", "success")
        return redirect(url_for("company.sections", slug=slug))
    return render_template("sections.html", company=company, types=SECTION_TYPES)


@bp.post("/sections/<int:section_id>/<action>")
@login_required
def section_action(section_id, action):
    section = db.get_or_404(Section, section_id)
    company = owned_company(section.company.slug)
    if action == "delete":
        db.session.delete(section)
    elif action == "toggle":
        section.visible = not section.visible
    elif action in ("up", "down"):
        secs = list(company.sections)
        for k, s in enumerate(secs):
            s.order_index = k
        i = secs.index(section)
        j = i - 1 if action == "up" else i + 1
        if 0 <= j < len(secs):
            secs[i].order_index, secs[j].order_index = j, i
    else:
        abort(400)
    db.session.commit()
    return redirect(url_for("company.sections", slug=company.slug))
