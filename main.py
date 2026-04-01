from flask import Flask
from database.db import db
from flask_migrate import Migrate
from routes.auth_routes import auth
from routes.web_routes import web
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
app.register_blueprint(web)

if __name__ == "__main__":
    app.run(debug=True)