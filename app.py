from flask import Flask, render_template, session, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from database.db import init_db, seed_db, get_user_by_email, get_user_by_id, get_user_expenses, get_user_stats, get_category_breakdown
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

    # Summary statistics
    raw_stats = get_user_stats(user_id)
    stats = {
        "total_spent": f"₹{raw_stats['total_spent']:,.2f}",
        "transaction_count": raw_stats['transaction_count'],
        "top_category": raw_stats['top_category']
    }

    raw_expenses = get_user_expenses(user_id)
    transactions = [
        {
            "date": tx["date"],
            "desc": tx["description"],
            "category": tx["category"],
            "amount": f"₹{tx['amount']:,.2f}"
        }
        for tx in raw_expenses
    ]

    raw_cats = get_category_breakdown(user_id)
    color_map = {
        "Food": "bar-orange",
        "Transport": "bar-blue",
        "Shopping": "bar-purple",
        "Bills": "bar-green"
    }
    categories = [
        {
            "name": cat["name"],
            "total": f"₹{cat['total']:,.0f}",
            "percentage": cat["percentage"],
            "color": color_map.get(cat["name"], "bar-gray")
        }
        for cat in raw_cats
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
