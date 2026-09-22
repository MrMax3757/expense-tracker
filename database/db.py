import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "spendly.db"

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
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


def get_category_breakdown(user_id):
    """Calculates total spend and percentage for each category."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category",
            (user_id,)
        ).fetchall()

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


def get_user_expenses(user_id):
    """Retrieves all expenses for a specific user, ordered by date descending."""
    with get_db() as conn:
        return conn.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ).fetchall()

def get_user_stats(user_id):
    """Returns summary statistics for a user's expenses."""
    with get_db() as conn:
        # Query 1: Total spent and transaction count
        stats_row = conn.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        # Query 2: Top category by amount
        category_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
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
