from flask import request, redirect, url_for, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
from models.berita_model import Berita
from database.db import db
from datetime import datetime
import os
import re


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
        # ================= AMBIL DATA FORM =================
        judul = request.form.get('judul')
        kategori = request.form.get('kategori')
        excerpt = request.form.get('excerpt')
        isi = request.form.get('isi')
        lokasi = request.form.get('lokasi')
        tanggal_kegiatan = request.form.get('tanggal_kegiatan')
        status = request.form.get('status', 'draft')

        # Checkbox featured
        is_featured = True if request.form.get('is_featured') else False

        # ================= SLUG =================
        slug = generate_slug(judul)

        # ================= UPLOAD GAMBAR =================
        thumbnail = None
        file = request.files.get('thumbnail')

        if file and file.filename != '':
            filename = secure_filename(file.filename)

            # Folder simpan
            upload_folder = os.path.join('static', 'uploads', 'berita')

            # Buat folder kalau belum ada
            os.makedirs(upload_folder, exist_ok=True)

            # Path full
            file_path = os.path.join(upload_folder, filename)

            # Simpan file
            file.save(file_path)

            # Simpan path ke DB
            thumbnail = f"uploads/berita/{filename}"

        # ================= SIMPAN KE DATABASE =================
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
                '%Y-%m-%d'
            ).date() if tanggal_kegiatan else None,
            status=status,
            is_featured=is_featured
        )

        db.session.add(berita)
        db.session.commit()

        flash('Berita berhasil ditambahkan!', 'success')

        return redirect("/admin-humas")

    except Exception as e:
        db.session.rollback()

        flash(f'Gagal menambahkan berita: {str(e)}', 'danger')

        return redirect("/admin-humas")


# ================= EDIT BERITA =================
def edit_berita(id):
    try:
        # Ambil berita berdasarkan ID
        berita = Berita.query.get_or_404(id)

        # ================= AMBIL DATA FORM =================
        judul = request.form.get("judul")
        kategori = request.form.get("kategori")
        excerpt = request.form.get("excerpt")
        isi = request.form.get("isi")
        lokasi = request.form.get("lokasi")
        tanggal_kegiatan = request.form.get("tanggal_kegiatan")
        status = request.form.get("status", "draft")

        # Checkbox featured
        is_featured = True if request.form.get("is_featured") else False

        # ================= UPDATE DATA =================
        berita.judul = judul
        berita.slug = generate_slug(judul)
        berita.kategori = kategori
        berita.excerpt = excerpt
        berita.isi = isi
        berita.lokasi = lokasi
        berita.status = status
        berita.is_featured = is_featured

        # Update tanggal
        berita.tanggal_kegiatan = (
            datetime.strptime(tanggal_kegiatan, "%Y-%m-%d").date()
            if tanggal_kegiatan else None
        )

        # ================= HANDLE GAMBAR BARU =================
        file = request.files.get("thumbnail")

        if file and file.filename != "":
            # Hapus gambar lama kalau ada
            if berita.thumbnail:
                old_file_path = os.path.join("static", berita.thumbnail)

                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Simpan gambar baru
            filename = secure_filename(file.filename)

            upload_folder = os.path.join("static", "uploads", "berita")
            os.makedirs(upload_folder, exist_ok=True)

            new_file_path = os.path.join(upload_folder, filename)

            file.save(new_file_path)

            # Simpan path baru ke DB
            berita.thumbnail = f"uploads/berita/{filename}"

        # ================= SAVE =================
        db.session.commit()

        flash("Berita berhasil diupdate!", "success")

        return redirect(url_for("admin.halaman_admin_humas"))

    except Exception as e:
        db.session.rollback()

        flash(f"Gagal update berita: {str(e)}", "danger")

        return redirect("/admin-humas")