from flask import Flask
from database.db import db
from flask_migrate import Migrate
from routes.auth_routes import auth
from routes.admin_routes import admin
from models.user_model import User
from flask_login import LoginManager

app = Flask(__name__)

# ================= CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'rahasia'  # 🔥 WAJIB buat session/login

# ================= INIT DB =================
db.init_app(app)

# ================= MIGRATE =================
migrate = Migrate(app, db)

# ================= FLASK-LOGIN =================
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'auth.login'
# 🔥 kalau belum login → redirect ke route ini


# ================= LOAD USER =================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    # 🔥 ambil user dari database tiap request


# ================= ROUTES =================
app.register_blueprint(auth)
app.register_blueprint(admin)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)