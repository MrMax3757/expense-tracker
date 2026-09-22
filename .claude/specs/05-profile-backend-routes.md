---
# Spec: Backend Routes for Profile Page

## Overview
This feature replaces the hardcoded mock data on the profile page with real data fetched from the SQLite database. It ensures that the spending statistics, transaction history, and category breakdowns are dynamically generated based on the logged-in user's actual expenses.

## Depends on
- 01-database-setup
- 03-login-logout
- 04-profile-page

## Routes
No new routes. This feature updates the existing `GET /profile` route to fetch data from the database instead of using hardcoded dictionaries and lists.

## Database changes
No database changes. The `expenses` table already contains the necessary fields (`user_id`, `amount`, `category`, `date`, `description`).

## Templates
- **Modify:** `templates/profile.html` — Ensure the template correctly handles the data types (e.g., formatting floats as currency) passed from the updated route.

## Files to change
- `app.py` — Update the `profile()` route logic.
- `database/db.py` — Add helper functions to fetch expense statistics and transaction lists for a specific user.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Database logic must reside in `database/db.py`, not in `app.py`

## Definition of done
- [ ] Log in as the demo user and verify the profile page displays the real sample data from `seed_db()` instead of the hardcoded mocks.
- [ ] Total spent correctly sums all expenses for the logged-in user.
- [ ] Transaction list shows all expenses for the user, ordered by date (descending).
- [ ] Category breakdown correctly aggregates totals and calculates percentages for each category used by the user.
- [ ] Verify that a user cannot see another user's expenses by manipulating session or request data.
---
