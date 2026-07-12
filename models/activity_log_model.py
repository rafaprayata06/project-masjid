from database.db import db
from datetime import datetime
from zoneinfo import ZoneInfo

def get_wib_time():
    # Ambil waktu Jakarta saat ini, lalu lepas info timezone-nya agar menjadi datetime polos (naive)
    return datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_nim = db.Column(db.String(20), db.ForeignKey('users.nim', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    target_table = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.String(50), nullable=True)
    deskripsi = db.Column(db.Text, nullable=False)
    
    # Tetap arahkan ke fungsi get_wib_time yang baru
    created_at = db.Column(db.DateTime, default=get_wib_time)

    user = db.relationship('User', backref=db.backref('activity_logs', lazy=True))