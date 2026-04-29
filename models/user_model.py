from database.db import db
from flask_login import UserMixin  # 🔥 biar support Flask-Login
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    nim = db.Column(db.String(20), primary_key=True)  # PK manual
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    jurusan = db.Column(db.String(100), nullable=True)
    jenis_kelamin = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum('AH', 'AK', 'AS', name='role_enum'), nullable=True)
    active = db.Column(db.Integer, nullable=True, default=0)
    created_at = db.Column(
    db.DateTime,
    default=datetime.utcnow
)

    # 🔥 penting karena PK bukan id
    def get_id(self):
        return self.nim