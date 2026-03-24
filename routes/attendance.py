from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database import get_db
from datetime import date

attendance = Blueprint("attendance", __name__)

@attendance.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    # Get total visits
    total = db.execute(
        "SELECT COUNT(*) as count FROM attendance WHERE user_id = ?",
        (current_user.id,)
    ).fetchone()["count"]

    # Get visits this month
    month = date.today().strftime("%Y-%m")
    monthly = db.execute(
        "SELECT COUNT(*) as count FROM attendance WHERE user_id = ? AND date_visited LIKE ?",
        (current_user.id, f"{month}%")
    ).fetchone()["count"]

    # Get all visit dates for calendar
    visits = db.execute(
        "SELECT date_visited FROM attendance WHERE user_id = ?",
        (current_user.id,)
    ).fetchall()
    visit_dates = [row["date_visited"] for row in visits]

    # Check if already marked today
    today = str(date.today())
    already_marked = db.execute(
        "SELECT id FROM attendance WHERE user_id = ? AND date_visited = ?",
        (current_user.id, today)
    ).fetchone()

    db.close()
    return render_template("dashboard.html",
        total=total,
        monthly=monthly,
        visit_dates=visit_dates,
        already_marked=already_marked
    )

@attendance.route("/mark")
@login_required
def mark():
    today = str(date.today())
    db = get_db()

    already = db.execute(
        "SELECT id FROM attendance WHERE user_id = ? AND date_visited = ?",
        (current_user.id, today)
    ).fetchone()

    if not already:
        db.execute(
            "INSERT INTO attendance (user_id, date_visited) VALUES (?, ?)",
            (current_user.id, today)
        )
        db.commit()
        flash("Attendance marked for today!", "success")
    else:
        flash("Already marked today.", "info")

    db.close()
    return redirect(url_for("attendance.dashboard"))