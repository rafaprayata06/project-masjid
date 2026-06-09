
from database.db import db

class Kategori(db.Model):
    __tablename__ = 'kategori'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)

    # PEMASUKAN / PENGELUARAN
    jenis = db.Column(db.String(20), nullable=False)

    transaksi = db.relationship(
        'Transaksi',
        backref='kategori',
        lazy=True
    )

