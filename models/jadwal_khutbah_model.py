from database.db import db

class JadwalKhutbah(db.Model):
    __tablename__ = "jadwal_khutbah"

    id = db.Column(db.Integer, primary_key=True)

    ustadz_id = db.Column(
        db.Integer,
        db.ForeignKey("ustadz.id", ondelete="CASCADE"),
        nullable=False
    )

    tanggal = db.Column(
        db.Date,
        nullable=False,
        unique=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    ustadz = db.relationship(
        "Ustadz",
        back_populates="jadwal"
    )