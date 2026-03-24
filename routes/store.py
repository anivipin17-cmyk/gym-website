from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database import get_db

store = Blueprint("store", __name__)

@store.route("/store")
@login_required
def shop():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    db.close()
    return render_template("store.html", products=products)

@store.route("/buy/<int:product_id>")
@login_required
def buy(product_id):
    db = get_db()
    db.execute(
        "INSERT INTO orders (user_id, product_id) VALUES (?, ?)",
        (current_user.id, product_id)
    )
    db.commit()
    db.close()
    flash("Order placed successfully!", "success")
    return redirect(url_for("store.shop"))

@store.route("/my-orders")
@login_required
def my_orders():
    db = get_db()
    orders = db.execute("""
        SELECT products.name, products.price, orders.order_date
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE orders.user_id = ?
        ORDER BY orders.order_date DESC
    """, (current_user.id,)).fetchall()
    db.close()
    return render_template("orders.html", orders=orders)