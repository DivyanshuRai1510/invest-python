"""Sample data. Every company, product and person here is fictional."""
import random
from datetime import datetime, timedelta

from extensions import db
from models import SECTOR_OPTIONS, Company, Connection, Event, Product, Section, User, slugify
from seed_images import company_image_url, product_image_url, investor_avatar_url, user_avatar_url
import seed_named as named

CR = 10_000_000
PASSWORD = "password123"
CITIES = named.CITIES
PREFIXES = ["Aero", "Nova", "Terra", "Vanta", "Kairo", "Zenith", "Aqua", "Lumen", "Verde", "Orbit", "Helix",
            "Quanta", "Sirius", "Nexo", "Pravah", "Surya", "Vayu", "Neer", "Agni", "Udaan", "Sanket", "Tarang",
            "Kosh", "Mitra", "Setu", "Ujala", "Prakriti", "Gyan", "Samarth", "Anvesh", "Dhaara", "Pulse",
            "Atlas", "Coral", "Drishti", "Ember", "Forge", "Grove", "Harbor", "Indigo", "Jade", "Kinetic"]
SUFFIXES = ["Labs", "Systems", "Technologies", "Works", "Dynamics", "Networks", "Solutions", "Tech",
            "Ventures", "Innovations", "Energy", "Robotics", "Biotech", "Logic"]
SERIES = ["Aster", "Kiran", "Vela", "Mira", "Torus", "Rhea", "Ojas", "Sol", "Nimbus", "Parab"]
STAGES = ["Bootstrapped", "Seed", "Seed", "Series A", "Series A", "Series B"]

CATEGORY_DATA = {
    "AI & ML": {
        "taglines": ["Computer vision for quality checks on factory lines.",
                     "Language tools tuned for regional-language support.",
                     "Forecasting for retail inventory teams.",
                     "Document reading for insurance claim desks.",
                     "Speech analytics for call-centre quality teams.",
                     "Recommendation tools for small online stores."],
        "items": ["Vision Module", "Inference Server", "Analytics Dashboard", "Speech API",
                  "Forecast Engine", "Document Parser", "Chat Assistant", "Data Labelling Kit"],
        "uses": ["factory lines", "retail chains", "call centres", "insurance desks", "clinics"]},
    "HealthTech": {
        "taglines": ["Remote patient monitoring for rural clinics.",
                     "Digital records that keep working offline.",
                     "Diagnostic devices for primary health centres.",
                     "Scheduling for multi-speciality hospitals.",
                     "Wearables that flag irregular readings to doctors.",
                     "Medicine stock tracking for pharmacies."],
        "items": ["Vital Monitor", "ECG Patch", "Diagnostic Kit", "Records Tablet", "Telehealth Cart",
                  "Sample Analyser", "Wearable Band", "Pharmacy Tracker"],
        "uses": ["rural clinics", "diagnostic labs", "home care", "pharmacies", "hospital wards"]},
    "AgriTech": {
        "taglines": ["Soil sensing for smallholder farms.",
                     "Greenhouse climate control with low power use.",
                     "Crop disease alerts sent by SMS.",
                     "Irrigation scheduling for drip systems.",
                     "Post-harvest storage monitoring.",
                     "Yield estimates from satellite images."],
        "items": ["Soil Sensor", "Irrigation Controller", "Greenhouse Panel", "Drone Scout",
                  "Storage Logger", "Seed Tracker", "Weather Station", "Crop Dashboard"],
        "uses": ["smallholder farms", "greenhouses", "cold stores", "orchards", "cooperatives"]},
    "FinTech": {
        "taglines": ["Payments for shops that run on weak networks.",
                     "Lending checks for borrowers with thin credit files.",
                     "Expense tools for field sales teams.",
                     "Invoice financing for MSME suppliers.",
                     "Fraud checks for digital wallets.",
                     "Small insurance policies sold over mobile."],
        "items": ["POS Terminal", "Credit API", "Wallet SDK", "Invoice Module", "Fraud Shield",
                  "Expense Card", "Micro-Policy Kit", "Settlement Engine"],
        "uses": ["small merchants", "MSME suppliers", "field sales teams", "kirana stores", "neobanks"]},
    "Hydrogen Production": {
        "taglines": ["Electrolyser units for green hydrogen at industrial sites.",
                     "Compact hydrogen generators for fertiliser plants.",
                     "Power-to-gas modules for renewable parks.",
                     "Water treatment skids that feed electrolysers.",
                     "Monitoring software for hydrogen plants.",
                     "Stack refurbishment for older electrolysers."],
        "items": ["Electrolyser Stack", "Gas Purifier", "Power Converter", "Compressor Skid",
                  "Water Treatment Unit", "Plant Controller", "Safety Monitor", "Stack Refurb Kit"],
        "uses": ["fertiliser plants", "steel units", "solar parks", "refineries", "chemical plants"]},
    "Hydrogen Storage": {
        "taglines": ["Metal hydride tanks for compact storage.",
                     "Pressure vessels for depot-scale hydrogen.",
                     "Storage control software for industrial sites.",
                     "Low-pressure buffer tanks for fuel cells.",
                     "Leak sensors for hydrogen storage bays.",
                     "Modular storage racks for backup power."],
        "items": ["Hydride Tank", "Pressure Vessel", "Buffer Tank", "Leak Sensor", "Storage Controller",
                  "Valve Block", "Rack Module", "Cryo Dewar"],
        "uses": ["backup power sites", "depots", "fuel cell buses", "labs", "data centres"]},
    "Fuel Cells": {
        "taglines": ["PEM fuel cell stacks for forklifts.",
                     "Backup power units for telecom towers.",
                     "Fuel cell modules for city buses.",
                     "Membrane assemblies for research labs.",
                     "Fuel cell controllers with remote diagnostics.",
                     "Hybrid power packs for remote sites."],
        "items": ["PEM Stack", "Power Module", "Membrane Set", "Controller Board", "Hybrid Pack",
                  "Air Blower", "Cooling Plate", "Diagnostics Kit"],
        "uses": ["forklifts", "telecom towers", "buses", "research labs", "remote sites"]},
    "Hydrogen Mobility": {
        "taglines": ["Hydrogen drivetrain kits for delivery vans.",
                     "Fleet telematics for fuel cell vehicles.",
                     "Range extenders for commercial trucks.",
                     "Driver training for hydrogen fleets.",
                     "Maintenance plans for fuel cell buses.",
                     "Tank mounts for light commercial vehicles."],
        "items": ["Drivetrain Kit", "Telematics Box", "Range Extender", "Fleet Dashboard", "Tank Mount",
                  "Battery Buffer", "Service Plan", "Fuel Adapter"],
        "uses": ["delivery vans", "city buses", "logistics fleets", "taxi operators", "campus shuttles"]},
    "Hydrogen Infrastructure": {
        "taglines": ["Refuelling stations for city fleets.",
                     "Mobile refuelling trucks for remote depots.",
                     "Dispensers for light-duty vehicles.",
                     "Station design and permit support.",
                     "Monitoring for hydrogen fuelling sites.",
                     "Inspection robots for gas pipelines."],
        "items": ["Dispenser", "Mini Station", "Mobile Refueller", "Site Controller", "Pipeline Sensor",
                  "Safety Barrier Kit", "Permit Toolkit", "Compressor Unit"],
        "uses": ["city fleets", "depots", "highway corridors", "industrial parks", "ports"]},
    "Robotics": {
        "taglines": ["Picking arms for mid-size warehouses.",
                     "Autonomous carts for hospital logistics.",
                     "Inspection drones for power lines.",
                     "Cobot arms for small assembly lines.",
                     "Delivery robots for campuses.",
                     "Welding cells for fabrication shops."],
        "items": ["Picking Arm", "Autonomous Cart", "Inspection Drone", "Cobot Arm", "Delivery Bot",
                  "Welding Cell", "Gripper Set", "Fleet Software"],
        "uses": ["warehouses", "hospitals", "power utilities", "assembly lines", "campuses"]},
    "Clean Energy": {
        "taglines": ["Rooftop solar and battery bundles for homes.",
                     "Smart chargers for apartment complexes.",
                     "Grid-tied inverters for small businesses.",
                     "Battery storage for solar mini-grids.",
                     "Energy audits for small factories.",
                     "Depot charging for electric buses."],
        "items": ["Solar Kit", "Battery Pack", "Smart Charger", "Inverter", "Energy Meter",
                  "Mini-Grid Controller", "Depot Charger", "Audit Toolkit"],
        "uses": ["homes", "apartment complexes", "small factories", "mini-grids", "bus depots"]},
    "EdTech": {
        "taglines": ["Adaptive practice for school maths.",
                     "Vocational courses with employer tie-ups.",
                     "Language learning for working adults.",
                     "Lab simulations for engineering colleges.",
                     "Teacher dashboards for government schools.",
                     "Mock tests for competitive exam prep."],
        "items": ["Practice Module", "Course Bundle", "Lab Simulator", "Teacher Dashboard", "Mock Test Pack",
                  "Language Track", "Certificate Programme", "Tablet Pack"],
        "uses": ["school maths", "engineering colleges", "working adults", "government schools", "coaching centres"]},
    "IoT": {
        "taglines": ["Vibration sensors for motor health.",
                     "Smart meters for housing societies.",
                     "Asset trackers for cold chain logistics.",
                     "Gateways for factory floors.",
                     "Home automation hubs with local control.",
                     "Water level sensors for municipal tanks."],
        "items": ["Vibration Sensor", "Smart Meter", "Asset Tracker", "Gateway", "Automation Hub",
                  "Level Sensor", "Temperature Logger", "Edge Node"],
        "uses": ["factory floors", "housing societies", "cold chains", "municipal tanks", "homes"]},
    "DeepTech": {
        "taglines": ["Materials research for next-generation batteries.",
                     "Small-satellite imaging for crop monitoring.",
                     "Quantum sensors for navigation.",
                     "Ceramics for high-heat industrial parts.",
                     "Photonic chips for data links.",
                     "Lab instruments for materials testing."],
        "items": ["Sample Kit", "Imaging Pack", "Quantum Sensor", "Ceramic Module", "Photonic Chip",
                  "Test Rig", "Data Subscription", "Spectrometer"],
        "uses": ["battery labs", "farm monitoring", "navigation systems", "foundries", "data centres"]},
    "Sustainability": {
        "taglines": ["Recycled-fibre fabrics for garment makers.",
                     "Plastic recycling units for municipalities.",
                     "Water purifiers with live quality readings.",
                     "Compost systems for housing societies.",
                     "Waste tracking software for cities.",
                     "Plant-based packaging for food brands."],
        "items": ["Fabric Roll", "Recycling Unit", "Purifier", "Compost Bin", "Waste Tracker",
                  "Packaging Sheet", "Filter Cartridge", "Collection App"],
        "uses": ["garment makers", "municipalities", "housing societies", "food brands", "schools"]},
}


def _person(rng):
    return f"{rng.choice(named.FIRST_NAMES)} {rng.choice(named.LAST_NAMES)}"


def _user(name, email, role, password_hash):
    u = User(name=name, email=email, role=role, password_hash=password_hash)
    return u


def seed_all():
    from werkzeug.security import generate_password_hash
    rng = random.Random(42)
    pw_hash = generate_password_hash(PASSWORD)

    # ---- 100 investors ----
    investors = []
    for i in range(1, 101):
        sectors = rng.sample(SECTOR_OPTIONS, rng.choice([2, 3]))
        ticket_min = rng.choice(named.TICKETS)
        name = _person(rng)
        u = _user(name, f"investor{i}@invest.com", "investor", pw_hash)
        u.title = rng.choice(named.TITLES)
        u.firm = rng.choice(named.FIRMS)
        u.sectors = ", ".join(sectors)
        u.ticket_min = ticket_min
        u.ticket_max = ticket_min * rng.choice(named.MULTIPLIERS)
        u.location = rng.choice(CITIES)
        u.bio = (f"Invests in {sectors[0].lower()} and {sectors[1].lower()} companies at early stage. "
                 "Looks for credible founders, clear unit economics and a realistic go-to-market plan.")
        u.avatar = investor_avatar_url(name)
        investors.append(u)
    db.session.add_all(investors)
    db.session.flush()

    # ---- companies: named ones first, then generated to 25 per sector ----
    by_name, by_cat = {}, {c: [] for c in SECTOR_OPTIONS}
    used_names = {row[0] for row in named.COMPANIES}
    founder_no = 0
    all_rows = []

    for row in named.COMPANIES:
        name, tagline, cat, loc, stage, founded, profit, mv, growth, emp, rev = row
        all_rows.append(dict(name=name, tagline=tagline, cat=cat, loc=loc, stage=stage, founded=founded,
                             profit=profit, mv=mv, growth=growth, emp=emp, rev=rev, named=True))

    for cat in SECTOR_OPTIONS:
        have = sum(1 for r in all_rows if r["cat"] == cat)
        for _ in range(max(0, 25 - have)):
            while True:
                name = f"{rng.choice(PREFIXES)} {rng.choice(SUFFIXES)}"
                if name not in used_names:
                    used_names.add(name)
                    break
            profit = round(rng.uniform(0.3, 20), 2)
            all_rows.append(dict(
                name=name, tagline=rng.choice(CATEGORY_DATA[cat]["taglines"]), cat=cat,
                loc=rng.choice(CITIES), stage=rng.choice(STAGES), founded=rng.randint(2016, 2024),
                profit=profit, mv=round(profit * rng.uniform(8, 30), 1), growth=rng.randint(8, 60),
                emp=rng.randint(6, 220), rev=round(profit * rng.uniform(2.2, 4.5), 1), named=False))

    for r in all_rows:
        founder_no += 1
        fname = _person(rng)
        founder = _user(fname, f"founder{founder_no}@invest.com", "founder", pw_hash)
        founder.avatar = user_avatar_url(fname)
        db.session.add(founder)
        db.session.flush()
        slug = slugify(r["name"])
        if Company.query.filter_by(slug=slug).first():
            slug = f"{slug}-{founder_no}"
        c = Company(
            name=r["name"], slug=slug, tagline=r["tagline"], category=r["cat"], location=r["loc"],
            description=r["tagline"], funding_stage=r["stage"], founded=r["founded"], verified=True,
            annual_profit=int(r["profit"] * CR), market_value=int(r["mv"] * CR), revenue=int(r["rev"] * CR),
            employees=r["emp"], growth_percent=r["growth"], is_sample=True,
            website=f"www.{slugify(r['name'].split()[0])}.com", owner_id=founder.id,
            logo=company_image_url(r["name"], r["cat"]),
        )
        db.session.add(c)
        db.session.flush()
        by_name[r["name"]] = c
        by_cat[r["cat"]].append(c)

        if r.get("named") and r["name"] == "HydroGenix Energy Pvt. Ltd.":
            secs = [Section(company_id=c.id, type=t, title=title, content=content, order_index=idx)
                    for idx, (t, title, content) in enumerate(named.HYDROGENIX_SECTIONS)]
        else:
            t_name, t_role = _person(rng), rng.choice(["Founder & CEO", "CTO", "Head of Operations"])
            secs = [
                Section(company_id=c.id, type="about", title="About", order_index=0,
                        content=f"{r['name']} works in {r['cat'].lower()} from {r['loc'].split(',')[0]}. "
                                f"{r['tagline']} Founded in {r['founded']}, currently at {r['stage']} stage."),
                Section(company_id=c.id, type="highlights", title="Key Highlights", order_index=1,
                        content="\n".join([f"Team of {r['emp']} people", f"Annual revenue ₹{r['rev']} Cr",
                                           f"Growth of {r['growth']}% year on year",
                                           f"Funding stage: {r['stage']}"])),
                Section(company_id=c.id, type="team", title="Team", order_index=2,
                        content=f"{t_name} | {t_role}"),
                Section(company_id=c.id, type="contact", title="Contact", order_index=3,
                        content=f"Website: {c.website}\nLocation: {r['loc']}"),
            ]
        db.session.add_all(secs)

    # ---- products: 30 named + 8 generated per sector (120) = 150 ----
    for name, maker, cat, desc, price, rating, reviews, badge in named.PRODUCTS:
        comp = by_name.get(maker)
        db.session.add(Product(name=name, maker=maker, category=cat, description=desc, price=price,
                               rating=rating, review_count=reviews, badge=badge, is_sample=True,
                               company_id=comp.id if comp else None,
                               image=product_image_url(name, cat)))

    price_range = {"Robotics": (150000, 900000), "Hydrogen Infrastructure": (2000000, 6000000),
                   "Hydrogen Production": (800000, 2500000), "Hydrogen Storage": (300000, 1500000),
                   "Fuel Cells": (500000, 1800000), "Hydrogen Mobility": (1500000, 3500000),
                   "DeepTech": (20000, 1000000), "AI & ML": (8000, 90000), "EdTech": (2000, 30000),
                   "FinTech": (1500, 25000), "IoT": (2000, 40000), "Clean Energy": (30000, 200000),
                   "HealthTech": (3000, 120000), "AgriTech": (5000, 90000), "Sustainability": (1000, 150000)}
    badges = ["", "", "", "", "Bestseller", "New Launch"]
    for cat in SECTOR_OPTIONS:
        data = CATEGORY_DATA[cat]
        makers = by_cat[cat]
        lo, hi = price_range[cat]
        for i, item in enumerate(data["items"]):
            maker = rng.choice(makers)
            product_name = f"{SERIES[(i + len(cat)) % len(SERIES)]} {item}"
            use = data["uses"][i % len(data["uses"])]
            db.session.add(Product(
                name=product_name, maker=maker.name, category=cat, company_id=maker.id, is_sample=True,
                description=f"{item} for {use}, supplied by {maker.name}.",
                price=rng.randrange(lo, hi, 500), rating=round(rng.uniform(4.0, 4.9), 1),
                review_count=rng.randint(5, 300), badge=rng.choice(badges),
                image=product_image_url(product_name, cat)))

    # ---- events ----
    start = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    for title, loc, days in named.EVENTS:
        db.session.add(Event(title=title, location=loc, start_date=start + timedelta(days=days),
                             description=f"{title}, {loc}."))

    # ---- demo swipes for investor1 ----
    demo = investors[0]
    companies = list(by_name.values())
    for c in companies[:3]:
        db.session.add(Connection(user_id=demo.id, company_id=c.id, kind="saved"))
    db.session.add(Connection(user_id=demo.id, company_id=companies[3].id, kind="interested"))

    db.session.commit()


def seed_if_empty():
    if Company.query.first() is None:
        seed_all()
