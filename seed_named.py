import random
from datetime import datetime, timedelta

from extensions import db
from models import SECTOR_OPTIONS, Company, Connection, Event, Product, Section, User, slugify

CR = 10_000_000
PASSWORD = "password123"

# name, tagline, category, location, stage, founded, profit_cr, market_value_cr, growth%, employees, revenue_cr
COMPANIES = [
    ("HydroGenix Energy Pvt. Ltd.", "Green hydrogen production using advanced electrolysis technology.", "Hydrogen Production", "Bengaluru, India", "Series A", 2021, 8.75, 125, 32, 85, 21.4),
    ("H2eon Labs", "Innovative solid-state hydrogen storage solutions.", "Hydrogen Storage", "Pune, India", "Seed", 2022, 5.40, 78, 28, 24, 9.1),
    ("H2Fuel Systems", "Fuel cell systems for industrial and mobility applications.", "Fuel Cells", "Hyderabad, India", "Series B", 2020, 12.60, 210, 41, 140, 44.0),
    ("GreenH2 Mobility", "Hydrogen-powered vehicles and refueling solutions.", "Hydrogen Mobility", "Gurugram, India", "Series B", 2019, 15.20, 305, 35, 210, 61.5),
    ("H2Infra Solutions Pvt. Ltd.", "Building hydrogen refueling infrastructure for a clean future.", "Hydrogen Infrastructure", "Mumbai, India", "Series A", 2021, 4.20, 61, 22, 52, 14.8),
    ("AgriSense Tech", "AI-powered crop intelligence for smarter farming.", "AgriTech", "Nagpur, India", "Seed", 2022, 3.10, 42, 18, 31, 7.2),
    ("AgriNext Pvt. Ltd.", "Smart indoor farming systems with IoT controls.", "AgriTech", "Chennai, India", "Series A", 2020, 6.30, 88, 27, 66, 16.0),
    ("CardioCare Labs", "Portable heart monitoring powered by real-time AI analytics.", "HealthTech", "Chennai, India", "Series A", 2020, 6.80, 95, 26, 64, 18.3),
    ("MedTech Solutions", "Affordable diagnostic devices for rural clinics.", "HealthTech", "Jaipur, India", "Seed", 2021, 2.40, 33, 31, 40, 6.0),
    ("PayNest", "Instant, low-cost payments infrastructure for small merchants.", "FinTech", "Mumbai, India", "Series B", 2018, 18.40, 420, 30, 180, 72.0),
    ("LendWise", "Digital credit scoring for first-time borrowers.", "FinTech", "Bengaluru, India", "Series A", 2021, 4.90, 70, 36, 75, 15.2),
    ("RoboAuto Systems", "AI-powered robotic arms for smart warehousing and automation.", "Robotics", "Pune, India", "Series A", 2021, 7.50, 110, 38, 70, 20.5),
    ("SkyTech Innovations", "Long-range AI surveillance drones for infrastructure.", "Robotics", "Hyderabad, India", "Series A", 2020, 9.80, 135, 29, 90, 26.4),
    ("VoltEdge Technologies", "Fast and smart EV charging for homes and commercial spaces.", "Clean Energy", "Ahmedabad, India", "Series A", 2020, 9.10, 150, 33, 95, 29.0),
    ("SolarStack", "Rooftop solar plus storage bundles for SMEs.", "Clean Energy", "Jodhpur, India", "Seed", 2022, 2.90, 36, 24, 44, 8.7),
    ("LearnLoop", "Adaptive learning platform for K-12 students.", "EdTech", "New Delhi, India", "Seed", 2023, 1.20, 25, 45, 18, 3.4),
    ("SkillForge", "Vocational upskilling with industry-linked certifications.", "EdTech", "Bengaluru, India", "Series A", 2021, 3.60, 52, 30, 60, 11.1),
    ("NeuraLens AI", "Computer-vision APIs for retail and manufacturing.", "AI & ML", "Bengaluru, India", "Series A", 2021, 5.90, 130, 40, 58, 16.9),
    ("Lingua Mind", "Conversational AI for Indian languages in customer support.", "AI & ML", "Hyderabad, India", "Seed", 2023, 1.80, 38, 52, 22, 4.6),
    ("SenseGrid IoT", "Industrial IoT sensors with predictive maintenance.", "IoT", "Coimbatore, India", "Series B", 2019, 11.20, 180, 25, 150, 38.0),
    ("HomeNest IoT", "Smart home automation kits for mid-income households.", "IoT", "Noida, India", "Seed", 2022, 1.60, 21, 33, 27, 5.5),
    ("QuantumLeaf Labs", "Materials research for next-generation batteries.", "DeepTech", "Bengaluru, India", "Seed", 2022, 0.40, 48, 60, 20, 1.1),
    ("OrbitEdge Space", "Small-satellite imaging for climate and agriculture.", "DeepTech", "Bengaluru, India", "Series A", 2020, 2.10, 140, 42, 65, 6.8),
    ("EcoCycle Waste", "Waste-to-energy and plastic recycling platform.", "Sustainability", "Indore, India", "Seed", 2021, 1.90, 27, 34, 48, 6.2),
    ("GreenThread Apparel", "Sustainable textiles from recycled fibres.", "Sustainability", "Surat, India", "Bootstrapped", 2019, 2.70, 19, 21, 38, 9.4),
    ("AquaPure Systems", "Low-cost water purification and monitoring.", "Sustainability", "Vadodara, India", "Seed", 2023, 0.90, 14, 58, 16, 2.7),
    ("MediSync", "Digital patient records for small hospitals.", "HealthTech", "Kochi, India", "Series A", 2021, 3.40, 58, 39, 46, 12.3),
    ("BharatPay Lite", "Offline-first wallets for rural retail.", "FinTech", "Lucknow, India", "Seed", 2022, 1.30, 24, 44, 30, 4.0),
    ("TerraFleet Logistics", "EV fleet management for last-mile delivery.", "Clean Energy", "Gurugram, India", "Series B", 2019, 13.70, 240, 31, 160, 47.8),
    ("CropLoop AI", "Yield prediction using satellite and weather data.", "AgriTech", "Pune, India", "Seed", 2023, 0.70, 15, 62, 14, 2.2),
]

# name, maker (must match a company name), category, description, price (rupees), rating, reviews, badge
PRODUCTS = [
    ("SkySurveil Drone", "SkyTech Innovations", "Robotics", "AI-powered surveillance drone with long-range camera and real-time analytics.", 245000, 4.8, 124, "Bestseller"),
    ("CardioCare Monitor", "CardioCare Labs", "HealthTech", "Portable heart monitoring device with real-time data and AI analytics.", 75000, 4.6, 98, ""),
    ("GreenGrow System", "AgriNext Pvt. Ltd.", "AgriTech", "Smart indoor farming system with IoT sensors and automated controls.", 120000, 4.7, 86, ""),
    ("VoltCharge EV Charger", "VoltEdge Technologies", "Clean Energy", "Fast and smart EV charging solution for homes and commercial spaces.", 55000, 4.5, 72, ""),
    ("RoboPick Assistant", "RoboAuto Systems", "Robotics", "AI-powered robotic arm for smart warehousing and automation.", 375000, 4.9, 58, "New Launch"),
    ("HGX Electrolyzer Series", "HydroGenix Energy Pvt. Ltd.", "Hydrogen Production", "High-efficiency electrolyzer producing 500 kg/day of green hydrogen.", 1850000, 4.7, 22, ""),
    ("HydroStorage Max", "H2eon Labs", "Hydrogen Storage", "Solid-state hydrogen storage unit for pressure-free industrial use.", 920000, 4.6, 18, ""),
    ("H2Gen Fuel Cell Stack", "H2Fuel Systems", "Fuel Cells", "Modular fuel cell stack for forklifts, buses and backup power.", 1340000, 4.5, 31, ""),
    ("GreenH2 Van Kit", "GreenH2 Mobility", "Hydrogen Mobility", "Hydrogen drivetrain conversion kit for light commercial vans.", 2600000, 4.4, 12, ""),
    ("H2Refuel Station Mini", "H2Infra Solutions Pvt. Ltd.", "Hydrogen Infrastructure", "Compact refueling station for city fleets and depots.", 4800000, 4.3, 9, "New Launch"),
    ("CropPulse Sensor Kit", "AgriSense Tech", "AgriTech", "Soil and canopy sensors with AI crop-health alerts.", 18500, 4.4, 210, ""),
    ("VertiTower Mini", "AgriNext Pvt. Ltd.", "AgriTech", "Vertical hydroponic tower for apartments and small farms.", 64000, 4.3, 40, ""),
    ("CardioTrack Wearable", "CardioCare Labs", "HealthTech", "Wrist-worn ECG tracker with clinician-shareable reports.", 9800, 4.5, 150, ""),
    ("DiagPod Rural Kit", "MedTech Solutions", "HealthTech", "Low-power diagnostic kit designed for rural clinics.", 22000, 4.2, 61, ""),
    ("PayNest Terminal", "PayNest", "FinTech", "Compact card and UPI terminal with same-day settlement.", 4500, 4.6, 320, "Bestseller"),
    ("LendWise Score API", "LendWise", "FinTech", "Credit scoring API for lenders serving thin-file borrowers.", 15000, 4.4, 55, ""),
    ("SkyLift Cargo Drone", "SkyTech Innovations", "Robotics", "Payload drone for medical and last-mile cargo delivery.", 610000, 4.6, 37, ""),
    ("SolarStack Home Kit", "SolarStack", "Clean Energy", "Rooftop solar plus battery kit for homes and small shops.", 165000, 4.5, 66, ""),
    ("VoltCharge Fleet Hub", "TerraFleet Logistics", "Clean Energy", "Depot charging hub that schedules EV fleets overnight.", 88000, 4.3, 29, ""),
    ("LearnLoop Tablet Pack", "LearnLoop", "EdTech", "Pre-loaded adaptive learning tablets for government schools.", 12000, 4.4, 140, ""),
    ("SkillForge Course Bundle", "SkillForge", "EdTech", "Six industry-certified courses with placement support.", 8500, 4.6, 210, "Bestseller"),
    ("Vision Shelf Analytics", "NeuraLens AI", "AI & ML", "Shelf-monitoring cameras with stock-out detection.", 40000, 4.7, 90, ""),
    ("Lingua Support Bot", "Lingua Mind", "AI & ML", "Multilingual support bot for Hindi, Tamil and Telugu.", 25000, 4.4, 48, ""),
    ("SenseGrid Vibe Sensor", "SenseGrid IoT", "IoT", "Vibration sensor that predicts motor failure weeks ahead.", 14500, 4.5, 115, ""),
    ("HomeNest Hub", "HomeNest IoT", "IoT", "Central hub for lights, fans and appliances with voice control.", 7900, 4.3, 77, ""),
    ("QuantumLeaf Cell Sample Kit", "QuantumLeaf Labs", "DeepTech", "Lab kit for testing next-gen battery electrode materials.", 56000, 4.2, 12, ""),
    ("OrbitEdge Imaging Pack", "OrbitEdge Space", "DeepTech", "Satellite imagery subscription for crop and flood monitoring.", 980000, 4.6, 15, ""),
    ("EcoCycle Compactor", "EcoCycle Waste", "Sustainability", "Compact plastic compactor with on-site recycling output.", 135000, 4.4, 34, ""),
    ("GreenThread Fabric Roll", "GreenThread Apparel", "Sustainability", "Recycled-fibre fabric roll for garment makers.", 3200, 4.5, 180, ""),
    ("AquaPure Purifier", "AquaPure Systems", "Sustainability", "Low-cost purifier with live water-quality monitoring.", 4900, 4.6, 260, "Bestseller"),
]

# title, location, days from now
EVENTS = [
    ("Global Startup Summit 2026", "Bengaluru, India", 30), ("Investor Connect Meet", "Mumbai, India", 45),
    ("AI & DeepTech Showcase", "New Delhi, India", 60), ("Hydrogen India Forum", "Pune, India", 12),
    ("Clean Energy Demo Day", "Ahmedabad, India", 20), ("HealthTech Pitch Night", "Chennai, India", 25),
    ("FinTech Founders Breakfast", "Mumbai, India", 8), ("Robotics & Automation Expo", "Hyderabad, India", 50),
    ("AgriTech Field Day", "Nagpur, India", 35), ("EdTech Innovators Meetup", "Bengaluru, India", 18),
    ("IoT Summit India", "Coimbatore, India", 70), ("Women in Deep Tech", "Bengaluru, India", 55),
    ("Sustainability Week", "Indore, India", 28), ("Seed Stage Roundtable", "Gurugram, India", 15),
    ("Angel Network Mixer", "Hyderabad, India", 42), ("Climate Capital Summit", "New Delhi, India", 65),
    ("Space Tech Meetup", "Bengaluru, India", 22), ("SaaS Growth Workshop", "Pune, India", 33),
    ("Startup Legal Clinic", "Mumbai, India", 10), ("Pitch Practice Night", "Jaipur, India", 38),
    ("Battery Tech Symposium", "Chennai, India", 75), ("Rural Commerce Expo", "Lucknow, India", 48),
    ("Smart Cities Hackathon", "Kochi, India", 58), ("Founder Wellbeing Circle", "Online", 14),
    ("Investor Due-Diligence Bootcamp", "Mumbai, India", 88), ("Food & AgriTech Summit", "Nagpur, India", 90),
    ("Robotics Pitch Day", "Pune, India", 27), ("Open Source AI Meetup", "Hyderabad, India", 11),
    ("Green Mobility Conclave", "Gurugram, India", 63), ("Water Tech Expo", "Vadodara, India", 80),
]

FIRST_NAMES = ["Aarav", "Vihaan", "Aditya", "Arjun", "Ishaan", "Kabir", "Rohan", "Karan", "Ananya", "Diya",
               "Ira", "Meera", "Saanvi", "Kavya", "Nisha", "Priya", "Riya", "Tara", "Neha", "Sneha",
               "Rahul", "Siddharth", "Vikram", "Harsh", "Pooja", "Ritika", "Aman", "Tanvi"]
LAST_NAMES = ["Mehta", "Iyer", "Reddy", "Sharma", "Nair", "Kapoor", "Patel", "Desai", "Menon", "Rao",
              "Verma", "Joshi", "Chandra", "Bose", "Kulkarni", "Gupta", "Agarwal", "Pillai", "Shah", "Malhotra"]
FIRMS = ["Lotus Ventures", "Himalayan Capital", "Deccan Growth Partners", "Saffron Angels", "Ganga Seed Fund",
         "Indigo Capital", "Peepal Tree Ventures", "Konark Capital", "Rann Ventures", "Sahyadri Partners",
         "Malabar Angels", "Vindhya Capital", "Cauvery Growth", "Thar Ventures", "Brahmaputra Labs",
         "Coromandel Impact Fund"]
TITLES = ["Partner", "Managing Director", "Principal", "Angel Investor", "Associate", "Venture Partner"]
CITIES = ["Bengaluru, India", "Mumbai, India", "New Delhi, India", "Hyderabad, India", "Pune, India",
          "Chennai, India", "Ahmedabad, India", "Gurugram, India", "Kolkata, India", "Jaipur, India"]
TICKETS = [500000, 1000000, 2500000, 5000000]
MULTIPLIERS = [4, 10, 20]

HYDROGENIX_SECTIONS = [
    ("about", "About", "HydroGenix Energy is a deep-tech startup focused on producing green hydrogen through high-efficiency electrolyzers. Its solution enables industries to transition to clean energy and achieve carbon neutrality."),
    ("highlights", "Key Highlights", "Proprietary high-efficiency electrolyzer technology\nCapacity: 500 kg/day green hydrogen\nServing 15+ industrial clients\nPatented technology\nStrong R&D and expert team"),
    ("team", "Team", "Aarav Mehta | Founder & CEO\nNeha Iyer | CTO\nRohan Das | Head of Operations"),
    ("documents", "Legal & Compliance Documents", "Certificate of Incorporation | Uploaded 12 Jan 2023\nGST Certificate | Uploaded 18 Jan 2023\nISO 14001 Certificate | Uploaded 22 Feb 2023\nCIN Verification | Uploaded 12 Jan 2023\nMSME Certificate | Uploaded 18 Jan 2023\nEnvironmental Clearance | Uploaded 10 Mar 2023"),
    ("contact", "Contact", "Website: www.hydrogenix.com\nLocation: Bengaluru, India"),
]


def _person(rng):
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def _user(name, email, role):
    u = User(name=name, email=email, role=role)
    u.set_password(PASSWORD)
    return u


def seed_all():
    rng = random.Random(42)  # deterministic: every reseed gives the same demo data

    # 100 investor profiles
    investors = []
    for i in range(1, 101):
        sectors = rng.sample(SECTOR_OPTIONS, rng.choice([2, 3]))
        ticket_min = rng.choice(TICKETS)
        u = _user(_person(rng), f"investor{i}@invest.com", "investor")
        u.title = rng.choice(TITLES)
        u.firm = rng.choice(FIRMS)
        u.sectors = ", ".join(sectors)
        u.ticket_min = ticket_min
        u.ticket_max = ticket_min * rng.choice(MULTIPLIERS)
        u.location = rng.choice(CITIES)
        u.bio = (f"Invests in {sectors[0].lower()} and {sectors[1].lower()} companies at early stage. "
                 "Looks for credible founders, clear unit economics and a realistic go-to-market plan.")
        investors.append(u)
    db.session.add_all(investors)
    db.session.flush()

    # 30 companies, each owned by its own founder account (founder1..founder30@invest.com)
    by_name = {}
    for i, row in enumerate(COMPANIES, start=1):
        name, tagline, cat, loc, stage, founded, profit, mv, growth, emp, rev = row
        founder = _user(_person(rng), f"founder{i}@invest.com", "founder")
        db.session.add(founder)
        db.session.flush()
        c = Company(
            name=name, slug=slugify(name), tagline=tagline, description=tagline, category=cat,
            location=loc, funding_stage=stage, founded=founded, verified=True,
            annual_profit=int(profit * CR), market_value=int(mv * CR), revenue=int(rev * CR),
            employees=emp, growth_percent=growth,
            website=f"www.{slugify(name.split()[0])}.com", owner_id=founder.id,
        )
        db.session.add(c)
        db.session.flush()
        by_name[name] = c

        if i == 1:
            secs = [Section(company_id=c.id, type=t, title=title, content=content, order_index=idx)
                    for idx, (t, title, content) in enumerate(HYDROGENIX_SECTIONS)]
        else:
            secs = [
                Section(company_id=c.id, type="about", title="About", order_index=0,
                        content=f"{name} works in {cat.lower()} from {loc.split(',')[0]}. {tagline} "
                                f"Founded in {founded} and currently at {stage} stage."),
                Section(company_id=c.id, type="highlights", title="Key Highlights", order_index=1,
                        content="\n".join([f"Team of {emp} people", f"Annual revenue ₹{rev} Cr",
                                           f"Growing {growth}% year on year", f"Funding stage: {stage}"])),
                Section(company_id=c.id, type="contact", title="Contact", order_index=2,
                        content=f"Website: www.{slugify(name.split()[0])}.com\nLocation: {loc}"),
            ]
        db.session.add_all(secs)

    # 30 products, each linked to its maker's company page
    for name, maker, cat, desc, price, rating, reviews, badge in PRODUCTS:
        comp = by_name.get(maker)
        db.session.add(Product(name=name, maker=maker, category=cat, description=desc, price=price,
                               rating=rating, review_count=reviews, badge=badge,
                               company_id=comp.id if comp else None))

    # 30 events
    start = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    for title, loc, days in EVENTS:
        db.session.add(Event(title=title, location=loc, start_date=start + timedelta(days=days),
                             description=f"{title}, {loc}."))

    # demo swipes for investor1 so the dashboard isn't empty on first login
    companies = list(by_name.values())
    demo = investors[0]
    for c in companies[:3]:
        db.session.add(Connection(user_id=demo.id, company_id=c.id, kind="saved"))
    db.session.add(Connection(user_id=demo.id, company_id=companies[3].id, kind="interested"))

    db.session.commit()


def seed_if_empty():
    if Company.query.first() is None:
        seed_all()
