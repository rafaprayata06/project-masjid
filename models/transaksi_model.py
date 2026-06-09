from datetime import datetime

from database.db import db

class Transaksi(db.Model):
    __tablename__ = 'transaksi'

    id = db.Column(db.Integer, primary_key=True)

    user_nim = db.Column(
        db.String(20),
        db.ForeignKey('users.nim'),
        nullable=False
    )

    kategori_id = db.Column(
        db.Integer,
        db.ForeignKey('kategori.id'),
        nullable=False
    )

    jumlah = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    keterangan = db.Column(
        db.Text,
        nullable=True
    )

    bukti_transaksi = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

 