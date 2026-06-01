# SupportDesk CRM — Datastraw Assessment Submission

A fully functional **Customer Support Ticketing CRM System** built with Python + Flask + SQLite, featuring a professional dark-themed single-page frontend. Deployed on Railway.

---

## 🚀 Live Demo

**Deployed URL:** `https://your-app.railway.app` *(replace after deployment)*

---

## 📋 Features Implemented

| Feature | Status |
|---|---|
| ✅ Create Tickets | Auto-generated IDs (TKT-0001…), timestamp, customer info |
| ✅ List All Tickets | Clean table view with ID, name, subject, priority, status, date |
| ✅ Search Functionality | Real-time search across name, email, ID, subject, description |
| ✅ Filter by Status | Open / In Progress / Closed chips + sidebar quick-filters |
| ✅ View & Update Tickets | Detail modal with full info, status/priority update, notes |
| ✅ Add Notes/Comments | Per-ticket timestamped notes with author attribution |
| ✅ Delete Tickets | With confirmation dialog |
| ✅ Priority System | High / Medium / Low with colour-coded badges (extra) |
| ✅ Dashboard | Live stats (total, open, in-progress, closed) + recent tickets (extra) |
| ✅ Filter by Priority | Dropdown filter on tickets page (extra) |

---

## 🏗️ Architecture

```
crm-system/
├── backend/
│   ├── __init__.py
│   └── app.py          # Flask API + static file serving
├── frontend/
│   └── index.html      # Single-page app (vanilla JS, no build step)
├── seed.py             # Demo data seeder
├── requirements.txt    # Python dependencies
├── Procfile            # Gunicorn for production
├── .env.example        # Environment variable template
├── .gitignore
└── README.md
```

### Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| **Backend** | Python 3 + Flask | Lightweight, readable, excellent SQLite support |
| **Database** | SQLite (built-in) | Zero-config, perfect for MVP, file-based persistence |
| **Frontend** | Vanilla JS + Custom CSS | No build step, fast load, full control over design |
| **Fonts** | Syne + DM Mono + DM Sans | Professional, distinctive, loaded from Google Fonts |
| **Deploy** | Railway.app | Free tier, auto-deploy from GitHub, simple Procfile |

---

## 🗄️ Database Schema

### `tickets` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| ticket_id | TEXT UNIQUE | e.g. TKT-0001 |
| customer_name | TEXT | Required |
| customer_email | TEXT | Required, stored lowercase |
| subject | TEXT | Issue title |
| description | TEXT | Full issue detail |
| priority | TEXT | High / Medium / Low |
| status | TEXT | Open / In Progress / Closed |
| created_at | TEXT | ISO 8601 UTC |
| updated_at | TEXT | ISO 8601 UTC |

### `notes` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| ticket_id | TEXT FK | References tickets.ticket_id |
| note_text | TEXT | Note content |
| author | TEXT | Who added the note |
| created_at | TEXT | ISO 8601 UTC |

---

## 📡 API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/tickets` | Create a new ticket |
| `GET` | `/api/tickets` | List tickets (optional `?status=&search=&priority=`) |
| `GET` | `/api/tickets/:id` | Get single ticket + notes |
| `PUT` | `/api/tickets/:id` | Update status/priority, add note |
| `DELETE` | `/api/tickets/:id` | Delete ticket and its notes |
| `GET` | `/api/stats` | Dashboard stats (counts + recent 5 tickets) |

### Example Requests

**Create ticket:**
```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Jane Smith",
    "customer_email": "jane@example.com",
    "subject": "Cannot login to dashboard",
    "description": "Getting 403 error on all login attempts since yesterday.",
    "priority": "High"
  }'
```

**Search + filter:**
```bash
curl "http://localhost:5000/api/tickets?status=Open&search=login&priority=High"
```

**Update ticket:**
```bash
curl -X PUT http://localhost:5000/api/tickets/TKT-0001 \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress", "note_text": "Investigating the authentication service."}'
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/crm-system.git
cd crm-system

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env

# 5. (Optional) Seed demo data
python seed.py

# 6. Start the server
python backend/app.py
```

Open `http://localhost:5000` in your browser.

---

## 🚢 Deployment (Railway)

1. Push your code to a GitHub repository
2. Go to [railway.app](https://railway.app) and sign in with GitHub
3. Click **New Project → Deploy from GitHub repo**
4. Select your repository
5. Railway auto-detects the `Procfile` and deploys

**Environment variables to set in Railway dashboard:**
```
PORT=8080       (Railway sets this automatically)
DB_PATH=crm.db
```

The app will be live at `https://your-app-name.railway.app`.

> **Note:** Railway's free tier has a 500MB storage limit. For production use, swap SQLite for PostgreSQL using Railway's built-in PostgreSQL plugin and update the DB connection in `app.py`.

---

## 🎨 Design Decisions

- **Dark theme** with a deep navy/charcoal palette — reduces eye strain for support agents working long hours
- **Syne font** for headings — geometric and distinctive without being trendy
- **DM Mono** for ticket IDs and timestamps — instantly scannable data feels at home in monospace
- **Color-coded badges** — Green (open), Amber (in-progress), Grey (closed) map to a traffic-light mental model
- **No JavaScript framework** — The entire frontend is ~500 lines of vanilla JS. Zero dependencies, instant load, easy to understand and modify

---

## 🧩 If I Had More Time

- **Authentication** — JWT-based login so multiple agents can have accounts
- **Email notifications** — Send confirmation emails on ticket creation/updates (Flask-Mail + SendGrid)
- **Audit log** — Track every status change with who made it and when
- **Pagination** — For large datasets; current implementation returns all matching records
- **File attachments** — Let customers attach screenshots to tickets
- **SLA tracking** — Flag tickets that have been open beyond threshold hours
- **PostgreSQL migration** — For production-grade persistence with proper indexing

---

## 🤔 Challenges & Solutions

**Challenge:** Python's built-in `sqlite3` module uses blocking I/O which doesn't play well with concurrent requests.
**Solution:** Used SQLite's WAL (Write-Ahead Logging) mode (`PRAGMA journal_mode=WAL`) which allows concurrent reads and serialises only writes, giving much better throughput without needing an async framework.

**Challenge:** Keeping the frontend single-file without a build step while still having a clean, maintainable codebase.
**Solution:** Structured the vanilla JS into clear sections (API layer, navigation, data fetching, render functions, helpers) with comments. The result is readable and easy to extend.

---

*Built for Datastraw Technologies Assessment — June 2026*
