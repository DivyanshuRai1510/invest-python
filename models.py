import re
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager

SECTOR_OPTIONS = [
    "AI & ML", "HealthTech", "AgriTech", "FinTech", "Hydrogen Production", "Hydrogen Storage",
    "Fuel Cells", "Hydrogen Mobility", "Hydrogen Infrastructure", "Robotics", "Clean Energy",
    "EdTech", "IoT", "DeepTech", "Sustainability",
]

SECTION_TYPES = {
    "about": "About",
    "highlights": "Key Highlights",
    "products": "Products",
    "team": "Team",
    "documents": "Documents",
    "contact": "Contact",
}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="investor")  # founder | investor
    avatar = db.Column(db.String(255), default="")        # path under static/, optional
    title = db.Column(db.String(120), default="")
    firm = db.Column(db.String(150), default="")
    sectors = db.Column(db.String(255), default="")       # comma separated
    ticket_min = db.Column(db.BigInteger, default=0)      # rupees
    ticket_max = db.Column(db.BigInteger, default=0)      # rupees
    location = db.Column(db.String(120), default="")
    bio = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", backref="owner", uselist=False)
    connections = db.relationship("Connection", backref="user", cascade="all, delete-orphan")
    rsvps = db.relationship("EventRSVP", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def sector_list(self):
        return [s.strip() for s in (self.sectors or "").split(",") if s.strip()]

    @property
    def initials(self):
        parts = self.name.split()
        return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    logo = db.Column(db.String(255), default="")
    tagline = db.Column(db.String(255), default="")
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200), default="")
    verified = db.Column(db.Boolean, default=False)
    funding_stage = db.Column(db.String(30), default="Seed")
    founded = db.Column(db.Integer, default=2024)
    annual_profit = db.Column(db.BigInteger, default=0)   # rupees
    market_value = db.Column(db.BigInteger, default=0)    # rupees
    revenue = db.Column(db.BigInteger, default=0)         # rupees
    employees = db.Column(db.Integer, default=0)
    growth_percent = db.Column(db.Float, default=0)
    is_sample = db.Column(db.Boolean, default=False)      # True for demo data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sections = db.relationship("Section", backref="company", cascade="all, delete-orphan",
                               order_by="Section.order_index")
    products = db.relationship("Product", backref="company")
    documents = db.relationship("CompanyDocument", backref="company", cascade="all, delete-orphan",
                                order_by="CompanyDocument.id")
    connections = db.relationship("Connection", backref="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "slug": self.slug, "tagline": self.tagline,
            "category": self.category, "location": self.location, "verified": self.verified,
            "funding_stage": self.funding_stage, "founded": self.founded,
            "annual_profit": self.annual_profit, "market_value": self.market_value,
            "growth_percent": self.growth_percent,
        }


class CompanyDocument(db.Model):
    __tablename__ = "company_documents"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Section(db.Model):
    """One block of a company's page. Companies compose their page from these."""
    __tablename__ = "sections"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, default="")
    order_index = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)

    def lines(self):
        return [l.strip() for l in (self.content or "").splitlines() if l.strip()]

    def pairs(self):
        out = []
        for line in self.lines():
            a, _, b = line.partition("|")
            out.append((a.strip(), b.strip()))
        return out


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    maker = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default="")
    image = db.Column(db.String(255), default="")          # path under static/, empty = icon artwork
    price = db.Column(db.BigInteger, nullable=False)
    rating = db.Column(db.Float, default=0)
    review_count = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(30), default="")
    is_sample = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enquiries = db.relationship("ProductEnquiry", backref="product", cascade="all, delete-orphan")


class ProductEnquiry(db.Model):
    __tablename__ = "product_enquiries"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    """Direct message. Allowed only between an investor and a founder."""
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)


class MessageAttachment(db.Model):
    """File shared in a private investor-founder conversation."""
    __tablename__ = "message_attachments"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120), default="application/octet-stream")
    size_bytes = db.Column(db.Integer, default=0)
    message = db.relationship("Message", backref=db.backref("attachments", cascade="all, delete-orphan"))


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, default="")

    rsvps = db.relationship("EventRSVP", backref="event", cascade="all, delete-orphan")


class EventRSVP(db.Model):
    __tablename__ = "event_rsvps"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Connection(db.Model):
    """Investor -> company decision. kind: saved | interested | passed."""
    __tablename__ = "connections"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    kind = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def default_sections(company):
    return [
        Section(company=company, type="about", title="About", content=company.description, order_index=0),
        Section(company=company, type="contact", title="Contact", order_index=1,
                content=f"Website: {company.website or 'not provided'}\nLocation: {company.location}"),
    ]


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(40), default="General")
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("support_tickets", lazy=True))


class Order(db.Model):
    """Order record for founder-side order tracking; no payment is processed by this model."""
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    customer_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_amount = db.Column(db.BigInteger, default=0)
    status = db.Column(db.String(30), default="Pending")
    payment_status = db.Column(db.String(30), default="Unpaid")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship("Product")
    company = db.relationship("Company", backref=db.backref("orders", lazy=True))


class Payment(db.Model):
    """Payment ledger entry; informational only and not connected to a payment gateway."""
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    amount = db.Column(db.BigInteger, default=0)
    method = db.Column(db.String(40), default="Manual")
    status = db.Column(db.String(30), default="Pending")
    reference = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.relationship("Order")
    company = db.relationship("Company", backref=db.backref("payments", lazy=True))
