from flask import Flask
from flask_login import LoginManager
from database import init_db, get_db
import os

app = Flask(__name__)
app.secret_key = "gymwebsite123"

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# Import and register routes
from routes.auth import auth
from routes.store import store
from routes.attendance import attendance
from routes.admin import admin

app.register_blueprint(auth)
app.register_blueprint(store)
app.register_blueprint(attendance)
app.register_blueprint(admin)

# Load user for flask-login
from models import User

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        return User(user["id"], user["name"], user["email"], user["role"])
    return None

if __name__ == "__main__":
    init_db()
    app.run(debug=True)