from database.db import db

class Ustadz(db.Model):
    __tablename__ = "ustadz"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=True)
    no_hp = db.Column(db.String(20), nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    # Relasi ke jadwal khutbah
    jadwal = db.relationship(
        "JadwalKhutbah",
        back_populates="ustadz",
        cascade="all, delete-orphan"
    )