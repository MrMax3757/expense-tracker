# Expense Tracker – Detailed Summary

## 📖 Project Overview
The **Expense Tracker** is a small Flask‑based web application that lets a user register, log in, and view a personal dashboard of expenses. Data is persisted in a local SQLite database (`spendly.db`).  The UI is rendered with Jinja2 templates and styled via static CSS/JS assets.  A test suite (pytest) validates core date‑filtering logic on the profile page.

---

## 🛠️ Technology Stack
- **Python 3.x**
- **Flask** – web framework
- **SQLite** – lightweight relational DB
- **Jinja2** – HTML templating
- **Werkzeug security** – password hashing/checking
- **pytest** – testing framework
- **dateutil** – for relative date calculations

---

## 📂 Directory Structure
```
expense-tracker/
│   .git/               # Git repo metadata
│   .gitignore
│   CLAUDE.md           # Project description / notes
│   app.py              # Flask entry point & route definitions
│   app.log             # Runtime log (currently empty)
│   file.txt            # Placeholder file (currently open)
│   requirements.txt    # Python dependencies
│   spendly.db          # SQLite DB with sample data
│   
├───database/          # DB helper module
│       __init__.py
│       db.py           # Connection + query functions, schema init & seed
│
├───static/            # Front‑end assets
│   ├───css/           # Stylesheets (not listed in detail)
│   ├───js/            # JavaScript helpers (not listed in detail)
│   └───img.jpg        # Example image used by templates
│
├───templates/         # Jinja2 HTML templates
│       base.html
│       landing.html
│       login.html
│       privacy.html
│       profile.html
│       register.html
│       terms.html
│
├───tests/             # pytest suite
│       test_06-date-filter-profile.py
│
└───.pytest_cache/     # Cached test results
```

---

## 🏗️ Core Application (`app.py`)
- **App configuration** – `app = Flask(__name__)` with a secret key.
- **Authentication** – Simple session‑based login using email + password hash.  `login_required` decorator protects the profile page.
- **Routes**
  - `/` – Landing page.
  - `/register` – Registration page (placeholder).
  - `/login` – GET/POST login handling.
  - `/terms`, `/privacy` – Static legal pages.
  - `/logout` – Clears session.
  - `/profile` – Dashboard showing:
    - Member‑since date.
    - Summary stats: total spent, transaction count, top category.
    - Recent transactions (date, description, amount).
    - Category breakdown with color‑coded bars.
    - Date‑filtering via query parameters (`start_date`, `end_date`, `range` like `this_month`, `last_3_months`, `last_6_months`).
  - Stub routes for expense CRUD (`/expenses/add`, `/expenses/<int:id>/edit`, `/expenses/<int:id>/delete`).
- **Database initialization** – On start (`if __name__ == "__main__"`) the app calls `init_db()` and `seed_db()` to ensure tables exist and sample data is present.

---

## 📊 Database Layer (`database/db.py`)
- **Connection helper** – `get_db()` returns a SQLite connection with `row_factory` and `PRAGMA foreign_keys = ON`.
- **User helpers** – `get_user_by_email`, `get_user_by_id`.
- **Expense helpers** –
  - `get_user_expenses` – optional date range, ordered newest first.
  - `get_category_breakdown` – totals & percentages per category, with optional date filter.
  - `get_user_stats` – total amount, transaction count, top category.
- **Schema creation (`init_db`)** – Creates `users` and `expenses` tables if they do not exist.
- **Seeding (`seed_db`)** – Inserts a demo user (`demo@spendly.com`, password `demo123`) and a set of sample expenses spanning various categories and dates (2026‑09‑01 to 2026‑09‑08).

---

## 🎨 Templates (Jinja2)
| Template | Purpose |
|----------|---------|
| `base.html` | Base layout with navigation, includes CSS/JS. |
| `landing.html` | Public landing page. |
| `login.html` / `register.html` | Authentication forms. |
| `profile.html` | Dashboard showing stats, transaction table, and category bar chart. |
| `terms.html` / `privacy.html` | Legal static pages. |

---

## 📁 Static Assets
- **CSS** – Custom styles (not detailed here) for dark‑mode, glass‑morphism, and responsive layout.
- **JS** – Potential client‑side interactivity (e.g., date‑picker scripts).
- **Image** – `img.jpg` used as a placeholder illustration.

---

## ✅ Tests (`tests/test_06-date-filter-profile.py`)
The test suite validates the date‑filtering logic on the profile route, ensuring that the `range` query parameter correctly resolves to appropriate start/end dates and that the rendered statistics reflect the filtered dataset.

---

## 📦 Configuration (`requirements.txt`)
```
flask
werkzeug
python-dateutil
pytest
```
(Actual versions are not pinned; they can be installed via `pip install -r requirements.txt`.)

---

## 🗂️ Miscellaneous
- **Logging** – `app.log` is prepared for runtime logs.
- **Version control** – `.git` directory holds full history.
- **CI/Cache** – `.pytest_cache` stores testing caches.

---

## 🚀 Next Steps / Extension Points
1. **Implement CRUD for expenses** – flesh out the stub routes (`add`, `edit`, `delete`).
2. **Enhance UI** – apply the premium design guidelines (gradient backgrounds, glass‑morphism, micro‑animations).  Use the `generate_image` tool to prototype mockups.
3. **Add API endpoints** – optional JSON API for external integrations.
4. **Improve security** – move secret key to environment variable, enable HTTPS in production.
5. **Write more tests** – cover registration, login flow, and edge‑case date filters.

---

*Generated on 2026‑10‑19*
