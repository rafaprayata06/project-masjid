from database.db import db
from datetime import datetime
class Berita(db.Model):
    __tablename__ = 'berita'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key ke users.nim
    user_nim = db.Column(
        db.String(20),
        db.ForeignKey('users.nim', ondelete='CASCADE'),
        nullable=False
    )

    # Judul berita
    judul = db.Column(
        db.String(255),
        nullable=False
    )

    # Slug untuk URL
    slug = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    # Kategori berita
    kategori = db.Column(
        db.String(100),
        nullable=False,
        default='kegiatan'
    )

    # Thumbnail / cover berita
    thumbnail = db.Column(
        db.String(255),
        nullable=True
    )

    # Ringkasan berita
    excerpt = db.Column(
        db.Text,
        nullable=True
    )

    # Isi lengkap berita
    isi = db.Column(
        db.Text,
        nullable=False
    )

    # Lokasi kegiatan
    lokasi = db.Column(
        db.String(255),
        nullable=True
    )

    # Tanggal kegiatan
    tanggal_kegiatan = db.Column(
        db.Date,
        nullable=True
    )

    # Status berita: draft / publish
    status = db.Column(
        db.String(20),
        nullable=False,
        default='draft'
    )

    # Jumlah views
    views = db.Column(
        db.Integer,
        default=0
    )

    # Berita unggulan
    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    # Timestamp
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )