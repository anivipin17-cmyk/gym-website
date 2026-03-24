from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import get_db
from functools import wraps

admin = Blueprint("admin", __name__)

# Block non-admins
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            flash("Access denied.", "danger")
            return redirect(url_for("attendance.dashboard"))
        return f(*args, **kwargs)
    return decorated

@admin.route("/admin")
@login_required
@admin_required
def dashboard():
    db = get_db()
    users = db.execute("SELECT * FROM users WHERE role = 'member'").fetchall()
    products = db.execute("SELECT * FROM products").fetchall()
    orders = db.execute("""
        SELECT users.name, products.name as product, orders.order_date
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN products ON orders.product_id = products.id
        ORDER BY orders.order_date DESC
    """).fetchall()
    db.close()
    return render_template("admin.html", users=users, products=products, orders=orders)

@admin.route("/admin/add-product", methods=["POST"])
@login_required
@admin_required
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    description = request.form["description"]
    db = get_db()
    db.execute(
        "INSERT INTO products (name, price, description) VALUES (?, ?, ?)",
        (name, price, description)
    )
    db.commit()
    db.close()
    flash("Product added!", "success")
    return redirect(url_for("admin.dashboard"))

@admin.route("/admin/delete-product/<int:product_id>")
@login_required
@admin_required
def delete_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    db.close()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.dashboard"))