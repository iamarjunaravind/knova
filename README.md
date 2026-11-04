# KNOVA — Gulf International Higher Education Platform & Expo

KNOVA is a comprehensive higher education platform and exhibition management system built with Django, connecting ambitious students, parents, and schools directly with accredited global universities, verified scholarship programs, and international admissions advisors across the GCC.

---

## 🚀 Key Features

- **Public Expo Portal:**
  - Dynamic Hero with video background and interactive statistics
  - Why KNOVA value propositions & 4-step student roadmap
  - GCC Tour Calendar & Multi-city event locations
  - Verified Scholarships & Financial Aid Directory
  - Exhibitors & Global Universities Booths Explorer
  - Interactive 2D/3D Exhibition Floor Map Blueprint
  - Gamified Student KNOVA Challenge Quest & Digital Pass
  - Keynote Speakers & Masterclasses Timetable
  - Fully responsive mobile & desktop UX with dark navy branding

- **Centralized Content Management (CMS):**
  - Section Visibility & Hide/Show master controls
  - Real-time instant AJAX toggles for every page module
  - Dropdown Accordion Section Jump on all edit pages
  - Hero, Why KNOVA, Roadmap, Testimonials, FAQ & Footer text editors
  - Subpage Content Editors (Exhibitors, Scholarships, Speakers, Programme, Sponsors, Map, Challenge, Privacy/Terms)

- **Administrative Dashboard:**
  - Live Registrations & Attendee Roster
  - QR Code Lead Scanner for Exhibitors & Seminars
  - University Booth Management & Course Directory
  - Common Examination Portal & CBT Question Bank
  - Database Backup & One-Click JSON Snapshot Restore
  - Bulk CSV/Excel Data Import & Sync Engine
  - Countries & Destinations Global Registry

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, Django 5.x
- **Frontend:** HTML5, CSS3, Modern JavaScript (Vanilla ES6+), Feather Icons, KaTeX KaTeX, Swiper
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Deployment:** Docker, Gunicorn, Nginx

---

## 📦 Quick Start & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/iamarjunaravind/knova.git
cd knova
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Launch the development server
```bash
python manage.py runserver 127.0.0.1:8000
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔐 Administrative Access

Access the Admin Dashboard at `http://127.0.0.1:8000/dashboard/`:
- **Page Content & Sections:** `/dashboard/cms/`
- **SEO & Search Engines:** `/dashboard/seo/`
- **Backup & Settings:** `/dashboard/settings/`
- **Django Superuser Console:** `/admin/`

---

## 📄 License
All rights reserved © KNOVA 2026–2027.
