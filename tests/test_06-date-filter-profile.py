import pytest
from app import app as flask_app
from database.db import init_db
import sqlite3
from datetime import date, timedelta

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': 'test_spendly.db',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

    # Cleanup test database after tests run
    import os
    try:
        if os.path.exists('test_spendly.db'):
            os.remove('test_spendly.db')
    except PermissionError:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    # Manually seed the user because /register is currently template-only
    with flask_app.app_context():
        from database.db import get_db
        with get_db() as conn:
            password_hash = "pbkdf2:sha256:260000$dummyhash" # Simplified for test
            conn.execute(
                "INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ('Test User', 'test@example.com', password_hash)
            )
            conn.commit()

    # Login (The /login route uses check_password_hash, so we must use a real hash)
    # Since we can't easily mock check_password_hash without patching,
    # we'll just manually set the session for the test client.
    with client.session_transaction() as sess:
        with flask_app.app_context():
            from database.db import get_db
            with get_db() as conn:
                user = conn.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',)).fetchone()
                sess['user_id'] = user['id']

    return client

@pytest.fixture
def seed_expenses(app, auth_client):
    """Seeds a set of expenses for the logged-in user across various dates."""
    with app.app_context():
        from database.db import get_db
        with get_db() as conn:
            user = conn.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',)).fetchone()
            uid = user['id']

            today = date.today()
            last_month = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            today_str = today.strftime("%Y-%m-%d")
            next_month = (today + timedelta(days=30)).strftime("%Y-%m-%d")

            expenses = [
                (uid, 100.0, "Food", "2020-01-01", "Ancient Meal"),
                (uid, 200.0, "Transport", last_month, "Recent Ride"),
                (uid, 300.0, "Shopping", today_str, "Today's Buy"),
                (uid, 400.0, "Bills", next_month, "Future Bill"),
            ]

            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()

class TestDateFilterProfile:

    def test_profile_auth_guard(self, client):
        """Verify that /profile is protected."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert 'login' in response.location

    def test_profile_all_time_no_filter(self, auth_client, seed_expenses):
        """Verify all expenses are shown when no filters are applied."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert b"\xe2\x82\xb91,000.00" in response.data
        assert b"Ancient Meal" in response.data
        assert b"Future Bill" in response.data

    def test_profile_filter_start_date(self, auth_client, seed_expenses):
        """Verify filtering by start_date only."""
        today = date.today().strftime("%Y-%m-%d")
        response = auth_client.get(f'/profile?start_date={today}')

        assert b"\xe2\x82\xb9700" in response.data
        assert b"Today's Buy" in response.data
        assert b"Future Bill" in response.data
        assert b"Recent Ride" not in response.data
        assert b"Ancient Meal" not in response.data

    def test_profile_filter_end_date(self, auth_client, seed_expenses):
        """Verify filtering by end_date only."""
        today = date.today().strftime("%Y-%m-%d")
        response = auth_client.get(f'/profile?end_date={today}')

        assert b"\xe2\x82\xb9600.00" in response.data
        assert b"Ancient Meal" in response.data
        assert b"Recent Ride" in response.data
        assert b"Today's Buy" in response.data
        assert b"Future Bill" not in response.data

    def test_profile_filter_date_range(self, auth_client, seed_expenses):
        """Verify filtering by both start and end dates."""
        start = (date.today() - timedelta(days=35)).strftime("%Y-%m-%d")
        end = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")

        response = auth_client.get(f'/profile?start_date={start}&end_date={end}')

        assert b"\xe2\x82\xb9200.00" in response.data
        assert b"Recent Ride" in response.data
        assert b"Today's Buy" not in response.data
        assert b"Ancient Meal" not in response.data

    def test_profile_range_no_results(self, auth_client, seed_expenses):
        """Verify behavior when no expenses match the filter."""
        start = "2099-01-01"
        end = "2099-01-31"
        response = auth_client.get(f'/profile?start_date={start}&end_date={end}')

        assert b"\xe2\x82\xb90.00" in response.data
        assert b"Ancient Meal" not in response.data

    def test_profile_invalid_range_error(self, auth_client, seed_expenses):
        """Verify that start_date > end_date triggers a flash message."""
        start = "2024-12-31"
        end = "2024-01-01"
        response = auth_client.get(f'/profile?start_date={start}&end_date={end}')

        assert b"Start date cannot be after end date" in response.data
        assert b"\xe2\x82\xb91,000.00" in response.data

    def test_profile_quick_filters(self, auth_client, seed_expenses):
        """Verify quick filter parameters don't crash and return 200."""
        for range_val in ["this_month", "last_3_months", "last_6_months"]:
            response = auth_client.get(f'/profile?range={range_val}')
            assert response.status_code == 200
            assert b"Total Spent" in response.data

    def test_profile_clear_filters(self, auth_client, seed_expenses):
        """Verify that removing dates returns view to all-time data."""
        auth_client.get('/profile?start_date=2099-01-01')
        response = auth_client.get('/profile')
        assert b"\xe2\x82\xb91,000.00" in response.data
