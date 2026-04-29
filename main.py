from flask import Flask
from database.db import db
from flask_migrate import Migrate
from routes.auth_routes import auth
from routes.admin_routes import admin
from models.user_model import User
from flask_login import LoginManager
from models.berita_model import Berita

# TAMBAHAN BARU
import os
from dotenv import load_dotenv

# BACA FILE .env
load_dotenv()

app = Flask(__name__)

# ================= CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# ================= INIT DB =================
db.init_app(app)

# ================= MIGRATE =================
migrate = Migrate(app, db)

# ================= FLASK-LOGIN =================
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'auth.login_form'


# ================= LOAD USER =================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ================= ROUTES =================
app.register_blueprint(auth)
app.register_blueprint(admin)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)