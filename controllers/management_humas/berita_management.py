from flask import request, redirect, url_for, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
from models.berita_model import Berita
from database.db import db
from datetime import datetime
import os
import re


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_berita_form(judul, kategori, isi):
    errors = {}

    if not judul or not judul.strip():
        errors["judul"] = "Judul wajib diisi"

    if not kategori or not kategori.strip():
        errors["kategori"] = "Kategori wajib dipilih"

    if not isi or not isi.strip():
        errors["isi"] = "Isi berita wajib diisi"

    return errors


def handle_thumbnail_upload(file, old_thumbnail=None):
    if not file or file.filename == "":
        return old_thumbnail

    if not allowed_file(file.filename):
        raise ValueError("Format gambar harus JPG, JPEG, PNG, atau WEBP")

    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)

    if file_length > MAX_FILE_SIZE:
        raise ValueError("Ukuran gambar maksimal 2MB")

    if old_thumbnail:
        old_path = os.path.join("static", old_thumbnail)
        if os.path.exists(old_path):
            os.remove(old_path)

    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"

    upload_folder = os.path.join("static", "uploads", "berita")
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)

    file.save(file_path)

    return f"uploads/berita/{filename}"
def generate_slug(judul):
    # Ubah jadi huruf kecil
    slug = judul.lower()

    # Ganti spasi dengan -
    slug = slug.replace(" ", "-")

    # Hapus karakter aneh
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    return slug

def store_berita():
    try:
        judul = request.form.get("judul")
        kategori = request.form.get("kategori")
        excerpt = request.form.get("excerpt")
        isi = request.form.get("isi")
        lokasi = request.form.get("lokasi")
        tanggal_kegiatan = request.form.get("tanggal_kegiatan")
        status = request.form.get("status", "draft")

        is_featured = True if request.form.get("is_featured") else False

        errors = validate_berita_form(judul, kategori, isi)

        if errors:
            for error in errors.values():
                flash(error, "error")
            return redirect("/admin-humas/news")

        slug = generate_slug(judul)

        file = request.files.get("thumbnail")
        thumbnail = handle_thumbnail_upload(file)

        berita = Berita(
            user_nim=current_user.nim,
            judul=judul,
            slug=slug,
            kategori=kategori,
            thumbnail=thumbnail,
            excerpt=excerpt,
            isi=isi,
            lokasi=lokasi,
            tanggal_kegiatan=datetime.strptime(
                tanggal_kegiatan,
                "%Y-%m-%d"
            ).date() if tanggal_kegiatan else None,
            status=status,
            is_featured=is_featured
        )

        db.session.add(berita)
        db.session.commit()

        flash("Berita berhasil ditambahkan!", "success")

    except ValueError as e:
        flash(str(e), "error")

    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menambahkan berita: {str(e)}", "error")

    return redirect("/admin-humas/news")
# ================= EDIT BERITA =================
def edit_berita(id):
    try:
        berita = Berita.query.get_or_404(id)

        judul = request.form.get("judul")
        kategori = request.form.get("kategori")
        excerpt = request.form.get("excerpt")
        isi = request.form.get("isi")
        lokasi = request.form.get("lokasi")
        tanggal_kegiatan = request.form.get("tanggal_kegiatan")
        status = request.form.get("status", "draft")

        is_featured = True if request.form.get("is_featured") else False

        errors = validate_berita_form(judul, kategori, isi)

        if errors:
            for error in errors.values():
                flash(error, "error")
            return redirect("/admin-humas/news")

        berita.judul = judul
        berita.slug = generate_slug(judul)
        berita.kategori = kategori
        berita.excerpt = excerpt
        berita.isi = isi
        berita.lokasi = lokasi
        berita.status = status
        berita.is_featured = is_featured

        berita.tanggal_kegiatan = (
            datetime.strptime(tanggal_kegiatan, "%Y-%m-%d").date()
            if tanggal_kegiatan else None
        )

        file = request.files.get("thumbnail")
        berita.thumbnail = handle_thumbnail_upload(file, berita.thumbnail)

        db.session.commit()

        flash("Berita berhasil diupdate!", "success")

    except ValueError as e:
        flash(str(e), "error")

    except Exception as e:
        db.session.rollback()
        flash(f"Gagal update berita: {str(e)}", "error")

    return redirect("/admin-humas/news")