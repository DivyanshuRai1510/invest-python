# INVEST — Startup and Investor Platform (Python / Flask)

A fully-featured startup-investor matchmaking platform with **Tinder-style swiping**, **real images everywhere**, **direct messaging** between investors and founders, and file uploads for company logos, product photos, documents and profile pictures.

## What is included

- **375 companies** (25 in each of 15 sectors) with real images pulled from free image services
- **150 products** from these companies, each with product photos
- **100 investor profiles** with real profile photos
- **30 upcoming events** with registration

### Core features

- **Company pages with tabs** — Overview, Products, Documents, Team, Investors
- **Startup registration** — Founders register via sign-up, fill the company form (upload logo + documents), then manage products and page sections
- **Product management** — Founders add, edit and delete products with photos
- **Tinder-style swipe** — Investors swipe through companies one at a time. Drag cards left (pass), down (save) or right (show interest). Full keyboard support (arrow keys + Backspace for undo).
- **Direct messaging** — Investors message founders from a company page; founders reply from their dashboard. Real-time message updates with read receipts.
- **Pagination** — Every list has page links and filter persistence
- **Dashboards** — Founders see interested investors and product enquiries. Investors see saved/interested startups.
- **Events with RSVP**
- **Investor profiles with matching startups**

## Images

**Every company, product, and investor has a real image** using picsum.photos (free, copyright-free placeholder images). No emoji or icon placeholders — full images everywhere.

## Folder structure

```
invest-python/
├── app.py                 App factory, template helpers, CLI
├── config.py              Settings (reads .env)
├── extensions.py          Database & login
├── models.py              Database tables
├── icons.py               Icon set & sector colours
├── utils.py               File upload helper
├── seed.py                Sample data (375 companies, 150 products, 100 investors)
├── seed_images.py         Image URL generator
├── wsgi.py                gunicorn entry point
├── requirements.txt
├── Dockerfile
├── .env.example
├── routes/
│   ├── main.py            Home, search (with filters & pagination), products, events, investors
│   ├── auth.py            Register, login, logout
│   ├── company.py         Company pages, registration, documents, products, sections
│   ├── swipe.py           Tinder swipe page & API
│   ├── messages.py        Inbox, chat threads, polling
│   ├── account.py         Dashboard, profile, password
│   └── api.py             JSON endpoints
├── templates/             21 pages (Tailwind CSS)
├── static/
│   ├── logo.svg
│   ├── swipe-enhanced.js  Drag, animations, keyboard controls for Tinder cards
│   ├── chat.js            Live chat polling
│   └── uploads/           Auto-created for logos, photos, documents
└── deploy/
    ├── invest.service
    └── nginx-invest.conf
```

---

## PART A — Run on your PC

### Step 1: Install Python
Python 3.10+ from https://www.python.org/downloads/. Tick **Add python.exe to PATH** on Windows.

### Step 2: Open the project folder
```
cd invest-python
```

### Step 3: Create and activate a virtual environment
Windows:
```
python -m venv venv
venv\Scripts\activate
```
Mac or Linux:
```
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install the libraries
```
pip install -r requirements.txt
```

### Step 5: Start the site
```
python app.py
```
The first start creates `invest.db` and loads the sample data (takes 3–5 seconds).

### Step 6: Open the site
Go to **http://127.0.0.1:5000**

### Step 7: Try it out
Password for all sample accounts: **password123**

**Investors:**
- investor1@invest.com … investor100@invest.com
- Go to **Tinder of Startups** and swipe
- Drag, tap buttons or press arrow keys (← pass, → interest, ↓ save, Backspace undo)
- Open any company and choose **Message founder**

**Founders:**
- founder1@invest.com … founder375@invest.com
- founder1 owns HydroGenix Energy (fully set up with products)
- Register as a new founder and complete the company form (logo + docs)
- Add products with photos
- See interested investors on your dashboard

### Reset data (optional)
```
flask --app app reseed
```

---

## PART B — Deploy to Ubuntu server

You need a VPS and a domain name.

### Step 1: Connect
```
ssh root@YOUR_SERVER_IP
```

### Step 2: Install packages
```
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip nginx unzip
```

### Step 3: Upload and extract
From your PC:
```
scp invest-python.zip root@YOUR_SERVER_IP:/root/
```
On the server:
```
unzip /root/invest-python.zip -d /var/www/
mv /var/www/invest-python /var/www/invest
```

### Step 4: Create environment
```
cd /var/www/invest
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Step 5: Configure secrets
```
cp .env.example .env
nano .env
```
Set `SECRET_KEY` to a random value:
```
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 6: Set permissions
```
chown -R www-data:www-data /var/www/invest
```

### Step 7: Run as a service
```
cp deploy/invest.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now invest
systemctl status invest
```

### Step 8: Connect nginx
```
cp deploy/nginx-invest.conf /etc/nginx/sites-available/invest
nano /etc/nginx/sites-available/invest      # replace yourdomain.com
ln -s /etc/nginx/sites-available/invest /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```
Open `http://yourdomain.com`.

### Step 9: HTTPS (free)
```
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Step 10: Firewall
```
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

### Useful commands
```
journalctl -u invest -f                    # View logs
systemctl restart invest                   # Restart
sudo -u www-data flask --app app reseed    # Reset data
```

---

## Before going live

- Forms need CSRF protection (Flask-WTF)
- Add email verification
- Check company documents manually before marking "Verified"
- Replace sample data with real companies and investors
- Set `SEED_DEMO_DATA=0` in `.env` to disable auto-seeding
- Review investment & payment legal requirements

## V7 interface and chat updates
- Refined company profile cover, responsive spacing, category-gradient artwork, and elevated profile cards.
- Chat supports selecting multiple files and images, showing attachment previews before sending, and posting the message plus selected files.
- Uploaded message files are stored in the Flask instance folder and served through a login-protected conversation route (not exposed as public static files).
- Attachment limit: 8 files per message; the app's existing request limit is 8 MB total per request.
- Geolocation share inserts a Google Maps link into the message composer. Contact sharing currently inserts the conversation partner's display name; a full address-book picker is not included.
- Existing SQLite databases gain the new `message_attachments` table automatically through `db.create_all()`; no existing Message columns are changed.
