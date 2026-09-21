from flask import Flask, render_template, session, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from database.db import init_db, seed_db, get_user_by_email, get_user_by_id
from functools import wraps

app = Flask(__name__)
app.secret_key = "spendly-secret-key-change-in-production"


def login_required(f):
    """Decorator to ensure the user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register")
def register():
    if "user_id" in session:
        return redirect(url_for("profile"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))

        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))



@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id)

    if not user:
        flash("User account not found.", "error")
        return redirect(url_for("login"))

    # Hardcoded data for Step 4 (UI validation)
    stats = {
        "total_spent": "₹12,450.00",
        "transaction_count": 42,
        "top_category": "Dining"
    }

    transactions = [
        {"date": "2026-09-20", "desc": "Starbucks Coffee", "category": "Dining", "amount": "₹350.00"},
        {"date": "2026-09-19", "desc": "Uber Ride", "category": "Transport", "amount": "₹120.00"},
        {"date": "2026-09-18", "desc": "Amazon - Books", "category": "Shopping", "amount": "₹1,200.00"},
        {"date": "2026-09-15", "desc": "Local Grocery", "category": "Food", "amount": "₹2,400.00"},
    ]

    categories = [
        {"name": "Dining", "total": "₹4,200", "percentage": 34, "color": "bar-orange"},
        {"name": "Transport", "total": "₹2,100", "percentage": 17, "color": "bar-blue"},
        {"name": "Shopping", "total": "₹6,150", "percentage": 49, "color": "bar-purple"},
    ]

    return render_template("profile.html",
                           user=user,
                           stats=stats,
                           transactions=transactions,
                           categories=categories)




@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
