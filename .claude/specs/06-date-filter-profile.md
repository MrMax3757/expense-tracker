# Spec: Date Filter for Profile Page

## Overview
This feature adds a date range filter to the user's profile page, allowing them to view their spending statistics and transaction history for a specific period. This enhances the utility of the profile page by providing a way to analyze spending trends over time rather than seeing a lifetime total.

## Depends on
- 05-profile-backend-routes

## Routes
No new routes. The existing `GET /profile` route will be modified to accept optional `start_date` and `end_date` query parameters.

## Database changes
No database changes. Existing queries in `database/db.py` will be updated to filter by date.

## Templates
- **Modify:** `templates/profile.html` - Add a date filter form (start date and end date inputs) at the top of the page.

## Files to change
- `app.py` - Update the `profile()` route to handle query parameters and pass them to the database helpers.
- `database/db.py` - Update `get_user_expenses`, `get_user_stats`, and `get_category_breakdown` to accept optional date filters.

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
- Use ISO 8601 date format (`YYYY-MM-DD`) for filtering.
- If no dates are provided, default to showing all expenses.

## Definition of done
- [ ] Profile page renders a date filter form with "Start Date" and "End Date" inputs.
- [ ] Submitting the form updates the "Total Spent", "Transaction Count", and "Top Category" to reflect only the selected range.
- [ ] The transaction list only shows expenses within the selected date range.
- [ ] The category breakdown chart only includes spending from the selected date range.
- [ ] Removing dates or submitting an empty filter returns the view to "all-time" data.
- [ ] The page handles invalid date ranges (start > end) gracefully.
