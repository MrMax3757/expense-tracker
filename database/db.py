import sqlite3
from werkzeug.security import generate_password_hash
from flask import current_app

def calculate_date_range(range_val):
    """Helper to calculate start and end dates based on a range preset."""
    from datetime import date
    from dateutil.relativedelta import relativedelta

    today = date.today()
    if range_val == "this_month":
        return today.replace(day=1).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    elif range_val == "last_3_months":
        return (today - relativedelta(months=3)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    elif range_val == "last_6_months":
        return (today - relativedelta(months=6)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    return None, None

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    # Use DATABASE from Flask config if available, otherwise fallback to default
    try:
        db_path = current_app.config.get("DATABASE", "spendly.db")
    except RuntimeError:
        db_path = "spendly.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_user_by_email(email):
    """Retrieves a user by their email address."""
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def get_user_by_id(user_id):
    """Retrieves a user by their unique ID."""
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_category_breakdown(user_id, start_date=None, end_date=None):
    """Calculates total spend and percentage for each category, with optional date filtering."""
    with get_db() as conn:
        query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " GROUP BY category"
        rows = conn.execute(query, params).fetchall()

        total_spend = sum(row["total"] for row in rows)

        breakdown = []
        for row in rows:
            percentage = (row["total"] / total_spend * 100) if total_spend > 0 else 0
            breakdown.append({
                "name": row["category"],
                "total": row["total"],
                "percentage": round(percentage)
            })

        return breakdown


def get_user_expenses(user_id, start_date=None, end_date=None):
    """Retrieves expenses for a user, ordered by date descending, with optional date filtering."""
    with get_db() as conn:
        query = "SELECT date, description, category, amount FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"
        return conn.execute(query, params).fetchall()

def get_user_stats(user_id, start_date=None, end_date=None):
    """Returns summary statistics for a user's expenses, with optional date filtering."""
    with get_db() as conn:
        # Base conditions for both queries
        query_base = "FROM expenses WHERE user_id = ?"
        params = [user_id]
        if start_date:
            query_base += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query_base += " AND date <= ?"
            params.append(end_date)

        # Query 1: Total spent and transaction count
        stats_row = conn.execute(
            f"SELECT SUM(amount) as total, COUNT(*) as count {query_base}",
            params
        ).fetchone()

        # Query 2: Top category by amount
        category_row = conn.execute(
            f"SELECT category {query_base} GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            params
        ).fetchone()

        return {
            "total_spent": stats_row["total"] if stats_row["total"] is not None else 0,
            "transaction_count": stats_row["count"],
            "top_category": category_row["category"] if category_row else "N/A"
        }

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    with get_db() as conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """Inserts sample data for development if not already present."""
    with get_db() as conn:
        # Check if demo user exists
        user = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()

        if user is None:
            # Create demo user
            password_hash = generate_password_hash("demo123")
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@spendly.com", password_hash)
            )
            user_id = cursor.lastrowid

            # Sample expenses
            expenses = [
                (user_id, 12.50, "Food", "2026-09-01", "Lunch at cafe"),
                (user_id, 45.00, "Transport", "2026-09-02", "Weekly gas"),
                (user_id, 120.00, "Bills", "2026-09-03", "Internet bill"),
                (user_id, 30.00, "Health", "2026-09-04", "Pharmacy"),
                (user_id, 60.00, "Entertainment", "2026-09-05", "Movie night"),
                (user_id, 25.00, "Shopping", "2026-09-06", "New book"),
                (user_id, 15.00, "Other", "2026-09-07", "Parking fee"),
                (user_id, 10.00, "Other", "2026-09-08", "Small donation"),
            ]

            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()
