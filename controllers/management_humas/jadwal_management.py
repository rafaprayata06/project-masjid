from flask import render_template, request, redirect, flash
from flask_login import current_user, login_required
from database.db import db
from datetime import datetime
from sqlalchemy import extract, or_
from models.ustadz_model import Ustadz  
from models.jadwal_khutbah_model import JadwalKhutbah

@login_required
def admin_imam_controller():
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")
        
    search_query = request.args.get("q", "").strip()
    bulan_filter = request.args.get("bulan", "").strip()

    query = JadwalKhutbah.query.join(Ustadz)

    if search_query:
        query = query.filter(
            or_(
                Ustadz.nama.ilike(f"%{search_query}%"),
                Ustadz.alamat.ilike(f"%{search_query}%")
            )
        )

    if bulan_filter and bulan_filter.isdigit():
        query = query.filter(extract('month', JadwalKhutbah.tanggal) == int(bulan_filter))

    daftar_jadwal = query.order_by(JadwalKhutbah.tanggal.asc()).all()

    # Inisialisasi struktur matriks tahunan (12 bulan, 5 jumat)
    matriks_jadwal = {bulan: {jumat: None for jumat in range(1, 6)} for bulan in range(1, 13)}

    for jw in daftar_jadwal:
        tgl = jw.tanggal
        
        # Jika tipe data dari DB terbaca sebagai string, konversi ke objek date
        if isinstance(tgl, str):
            tgl = datetime.strptime(tgl.split()[0], "%Y-%m-%d").date()
        
        try:
            bln = tgl.month
            hari = tgl.day
        except AttributeError:
            bln = int(tgl.strftime('%m'))
            hari = int(tgl.strftime('%d'))
        
        # Tentukan posisi kolom Jumat ke berapa (1-5)
        jumat_ke = ((hari - 1) // 7) + 1
        
        if 1 <= jumat_ke <= 5:
            # Menyediakan semua field data yang wajib dibaca oleh view HTML & JavaScript Modal
            matriks_jadwal[bln][jumat_ke] = {
                'id': jw.id,
                'ustadz_id': jw.ustadz_id,
                'tanggal_raw': tgl.strftime('%Y-%m-%d'), # Dibutuhkan untuk value input type="date"
                'tanggal_str': tgl.strftime('%d %b %Y'),  # Ditampilkan di teks card & modal delete
                'nama': jw.ustadz.nama,
                'alamat': jw.ustadz.alamat,
                'no_hp': jw.ustadz.no_hp
            }

    return render_template(
        "admin/components-AH/AH_imam.html", 
        user=current_user, 
        matriks_jadwal=matriks_jadwal,
        search_query=search_query,
        bulan_filter=bulan_filter
    )

@login_required
def admin_imam_store_controller():
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")

    nama = request.form.get("nama", "").strip()
    tanggal_str = request.form.get("tanggal")
    alamat = request.form.get("alamat", "").strip()
    no_hp = request.form.get("no_hp", "").strip()

    if not nama or not tanggal_str:
        flash("Nama Ustadz dan Tanggal wajib diisi!", "error")
        return redirect("/admin-humas/schedules")

    try:
        tanggal_obj = datetime.strptime(tanggal_str, "%Y-%m-%d").date()

        # Cek bentrok jadwal pada tanggal yang sama
        existing_jadwal = JadwalKhutbah.query.filter_by(tanggal=tanggal_obj).first()
        if existing_jadwal:
            flash(f"Gagal menyimpan! Jadwal pada tanggal {tanggal_str} sudah terisi.", "error")
            return redirect("/admin-humas/schedules")

        # Cari ustadz berdasarkan nama (case-insensitive)
        ustadz = Ustadz.query.filter(Ustadz.nama.ilike(nama)).first()
        if not ustadz:
            ustadz = Ustadz(nama=nama, alamat=alamat, no_hp=no_hp)
            db.session.add(ustadz)
            db.session.flush() # Ambil ID ustadz baru sebelum commit utama

        jadwal_baru = JadwalKhutbah(ustadz_id=ustadz.id, tanggal=tanggal_obj)
        db.session.add(jadwal_baru)
        db.session.commit()

        flash("Jadwal penugasan khutbah berhasil disimpan!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menyimpan jadwal: {str(e)}", "error")

    return redirect("/admin-humas/schedules")

@login_required
def admin_imam_update_controller(id):
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")
        
    jadwal = db.session.get(JadwalKhutbah, id)
    if not jadwal:
        flash("Jadwal tidak ditemukan!", "error")
        return redirect("/admin-humas/schedules")
        
    try:
        nama = request.form.get("nama", "").strip()
        tanggal = request.form.get("tanggal")
        alamat = request.form.get("alamat", "").strip()
        no_hp = request.form.get("no_hp", "").strip()
        
        # Sinkronisasi data Ustadz
        ustadz = Ustadz.query.filter(Ustadz.nama.ilike(nama)).first()
        if not ustadz:
            ustadz = Ustadz(nama=nama, alamat=alamat, no_hp=no_hp)
            db.session.add(ustadz)
            db.session.flush()
        else:
            ustadz.alamat = alamat
            ustadz.no_hp = no_hp
            
        tanggal_obj = datetime.strptime(tanggal, "%Y-%m-%d").date()
        
        # Validasi bentrok tanggal jika tanggal diganti
        if jadwal.tanggal != tanggal_obj:
            bentrok = JadwalKhutbah.query.filter_by(tanggal=tanggal_obj).first()
            if bentrok:
                flash("Gagal mengubah! Sudah ada jadwal khutbah lain di tanggal tersebut.", "error")
                return redirect("/admin-humas/schedules")

        jadwal.ustadz_id = ustadz.id
        jadwal.tanggal = tanggal_obj
        
        db.session.commit()
        flash("Jadwal penugasan khutbah berhasil diperbarui!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Terjadi kesalahan saat memperbarui data: {str(e)}", "error")
        
    return redirect("/admin-humas/schedules")

@login_required
def admin_imam_delete_controller(id):
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")
        
    jadwal = db.session.get(JadwalKhutbah, id)
    if not jadwal:
        flash("Jadwal tidak ditemukan!", "error")
        return redirect("/admin-humas/schedules")
        
    try:
        db.session.delete(jadwal)
        db.session.commit()
        flash("Jadwal penugasan khutbah berhasil dihapus!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menghapus jadwal: {str(e)}", "error")
        
    return redirect("/admin-humas/schedules")