from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from models import User

auth = Blueprint("auth", __name__)

@auth.route("/")
def home():
    return render_template("index.html")

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        membership = request.form["membership"]

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, password, membership_type) VALUES (?, ?, ?, ?)",
                (name, email, password, membership)
            )
            db.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except:
            flash("Email already exists.", "danger")
        finally:
            db.close()

    return render_template("signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            user_obj = User(user["id"], user["name"], user["email"], user["role"])
            login_user(user_obj)
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("attendance.dashboard"))
        else:
            flash("Wrong email or password.", "danger")

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))