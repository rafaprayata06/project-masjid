from database.db import db

class User(db.Model):
    __tablename__ = 'users'

    nim = db.Column(db.String(20), primary_key=True)  # PK manual
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)