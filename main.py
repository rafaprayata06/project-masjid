from flask import Flask, render_template
from database.db import db
from flask_migrate import Migrate
from routes.auth_routes import auth
from models.user_model import User

app = Flask(__name__)

# Config database (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
db.init_app(app)

# Init Migration
migrate = Migrate(app, db)

# Routes
app.register_blueprint(auth)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/jadwal")
def jadwal():
    return render_template("jadwal.html")

@app.route("/keuangan")
def keuangan():
    return render_template("keuangan.html")

@app.route("/profil")
def profil():
    return render_template("profil.html")

@app.route("/infaq")
def infaq():
    return render_template("infaq.html")


if __name__ == "__main__":
    app.run(debug=True)