# Spec: Login and Logout

## Overview
This feature implements the authentication loop for Spendly, allowing users to securely access their personal expense data. It converts the existing static login page into a functional authentication system and provides a mechanism for users to end their session.

## Depends on
- 02 Registration (Users must be able to create accounts first)

## Routes
- `GET /login` — Renders the login form — public
- `POST /login` — Authenticates user and creates session — public
- `GET /logout` — Destroys user session and redirects to login — logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `templates/login.html` — Update form to use `POST` method and provide error messaging.
- **Create:** No new templates.

## Files to change
- `app.py` — Implement authentication logic and session management.
- `database/db.py` — Add a helper function to fetch a user by email.

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
- Use Flask `session` for managing logged-in state

## Definition of done
- [ ] User can log in with valid credentials and is redirected to the profile page (or landing).
- [ ] User sees an error message when providing incorrect credentials.
- [ ] Logged-in user can click a logout link/button and is successfully signed out.
- [ ] Unauthenticated users are redirected to the login page when attempting to access protected routes.
