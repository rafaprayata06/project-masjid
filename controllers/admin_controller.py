from flask import Blueprint
from flask import render_template, request, redirect, flash
from flask_login import current_user, login_required
from models.kategori_model import Kategori
from models.transaksi_model import Transaksi
from models.user_model import User
from models.berita_model import Berita
from flask import request, redirect, flash
from database.db import db
from datetime import datetime,time
from sqlalchemy import func
from flask import send_file
from openpyxl import Workbook
from io import BytesIO


def admin_super():
    if current_user.role != "AS":
        return redirect("/login")

    keyword = request.args.get("q")

    if keyword:
        users = User.query.filter(
            User.name.ilike(f"%{keyword}%")
        ).order_by(User.created_at.desc()).all()
    else:
        users = User.query.order_by(
            User.created_at.desc()
        ).all()

    is_empty = len(users) == 0
    return render_template("admin/components-KelolaAdmin/AS-users.html", user=current_user,users=users, is_empty=is_empty)

def update_user_controller(nim):
    user = User.query.get_or_404(nim)

    role = request.form.get("role")
    active = request.form.get("active")

    # VALIDASI SEDERHANA
    if active not in ["0", "1", "2"]:
        flash("Status tidak valid", "error")
        return redirect("/admin-super/users")

    if role not in ["AS", "AK", "AH", "", None]:
        flash("Role tidak valid", "error")
        return redirect("/admin-super/users")

    if user.role == "AS":
        flash("Admin Super tidak dapat diubah", "error")
    # UPDATE
    user.role = role if role != "" else None
    user.active = int(active)

    db.session.commit()

    flash("User berhasil diupdate", "success")
    return redirect("/admin-super/kelola-admin")

@login_required
def admin_humas():
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")
    berita =  Berita.query.order_by(Berita.id.desc()).all()
    return render_template("admin/AH.html", user=current_user,semua_berita=berita)

def dashboard_humas():
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")

    # 1. HITUNG METRIK DATA BERITA (Untuk diisi ke card stats nanti)
    total_berita = Berita.query.count()
    
    # 2. AMBIL DATA BERITA TERBARU (Untuk widget log aktivitas/terkini)
    berita_terbaru = Berita.query.order_by(Berita.id.desc()).limit(5).all()

    # 3. RENDER TEMPLATE DENGAN PARAMETER VIEW DASHBOARD
    return render_template(
        "admin/components-AH/AH_dashboard.html", 
        view="dashboard", 
        user=current_user,
        total_berita=total_berita,
        berita_terbaru=berita_terbaru
        
    )

def admin_imam_controller():
    # Array Simulasi Data Mingguan Penuh untuk Loop Slicing di Frontend
    daftar_jadwal_mock = [
        {
            "id": 1, "hari": "Senin", "tanggal": "15 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. H. Ahmad Fauzi", "shubuh_muadzin": "Akhi Rian",
            "dhuhur": "Ust. Rahmat Hidayat", "dhuhur_muadzin": "Akhi Farhan",
            "ashar": "Ust. M. Ridwan", "ashar_muadzin": "Akhi Bilal",
            "maghrib": "Ust. Dr. Syarifuddin", "maghrib_muadzin": "Akhi Rian",
            "isya": "Ust. H. Ahmad Fauzi", "isya_muadzin": "Akhi Ilham"
        },
        {
            "id": 2, "hari": "Selasa", "tanggal": "16 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. M. Ridwan", "shubuh_muadzin": "Akhi Farhan",
            "dhuhur": "Ust. Rahmat Hidayat", "dhuhur_muadzin": "Akhi Bilal",
            "ashar": "Ust. H. Ahmad Fauzi", "ashar_muadzin": "Akhi Ilham",
            "maghrib": "Ust. Dr. Syarifuddin", "maghrib_muadzin": "Akhi Farhan",
            "isya": "Ust. Rahmat Hidayat", "isya_muadzin": "Akhi Rian"
        },
        {
            "id": 3, "hari": "Rabu", "tanggal": "17 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. H. Ahmad Fauzi", "shubuh_muadzin": "Akhi Bilal",
            "dhuhur": "Ust. Dr. Syarifuddin", "dhuhur_muadzin": "Akhi Ilham",
            "ashar": "Ust. M. Ridwan", "ashar_muadzin": "Akhi Rian",
            "maghrib": "Ust. Rahmat Hidayat", "maghrib_muadzin": "Akhi Bilal",
            "isya": "Ust. Dr. Syarifuddin", "isya_muadzin": "Akhi Farhan"
        },
        {
            "id": 4, "hari": "Kamis", "tanggal": "18 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. Dr. Syarifuddin", "shubuh_muadzin": "Akhi Ilham",
            "dhuhur": "Ust. M. Ridwan", "dhuhur_muadzin": "Akhi Rian",
            "ashar": "Ust. Rahmat Hidayat", "ashar_muadzin": "Akhi Farhan",
            "maghrib": "Ust. H. Ahmad Fauzi", "maghrib_muadzin": "Akhi Ilham",
            "isya": "Ust. M. Ridwan", "isya_muadzin": "Akhi Bilal"
        },
        {
            "id": 5, "hari": "Jumat", "tanggal": "19 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. Rahmat Hidayat", "shubuh_muadzin": "Akhi Rian",
            "dhuhur": "Ust. H. Ahmad Fauzi", "dhuhur_muadzin": "Akhi Farhan",
            "ashar": "Ust. Dr. Syarifuddin", "ashar_muadzin": "Akhi Bilal",
            "maghrib": "Ust. M. Ridwan", "maghrib_muadzin": "Akhi Rian",
            "isya": "Ust. H. Ahmad Fauzi", "isya_muadzin": "Akhi Ilham"
        },
        {
            "id": 6, "hari": "Sabtu", "tanggal": "20 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. M. Ridwan", "shubuh_muadzin": "Akhi Farhan",
            "dhuhur": "Ust. Rahmat Hidayat", "dhuhur_muadzin": "Akhi Bilal",
            "ashar": "Ust. H. Ahmad Fauzi", "ashar_muadzin": "Akhi Ilham",
            "maghrib": "Ust. Dr. Syarifuddin", "maghrib_muadzin": "Akhi Farhan",
            "isya": "Ust. Rahmat Hidayat", "isya_muadzin": "Akhi Rian"
        },
        {
            "id": 7, "hari": "Ahad", "tanggal": "21 Juni 2026", "terisi_count": 5,
            "shubuh": "Ust. Dr. Syarifuddin", "shubuh_muadzin": "Akhi Bilal",
            "dhuhur": "Ust. M. Ridwan", "dhuhur_muadzin": "Akhi Ilham",
            "ashar": "Ust. Rahmat Hidayat", "ashar_muadzin": "Akhi Rian",
            "maghrib": "Ust. H. Ahmad Fauzi", "maghrib_muadzin": "Akhi Bilal",
            "isya": "Ust. Dr. Syarifuddin", "isya_muadzin": "Akhi Farhan"
        }
    ]

    return render_template(
        "admin/components-AH/AH_imam.html", 
        user=current_user, 
        daftar_jadwal=daftar_jadwal_mock
    )


def admin_imam_update_row_controller(id):
    shubuh = request.form.get("shubuh")
    maghrib = request.form.get("maghrib")
    
    flash(f"Simulasi Sukses: Jadwal ID {id} diperbarui (Subuh: {shubuh}, Maghrib: {maghrib})", "success")
    return redirect("/admin-humas/schedules")


def admin_imam_store_controller():
    tgl_mulai = request.form.get("tanggal_mulai")
    tgl_selesai = request.form.get("tanggal_selesai")
    
    flash(f"Simulasi Sukses: Inisialisasi pekan baru {tgl_mulai} s/d {tgl_selesai}", "success")
    return redirect("/admin-humas/schedules")



def admin_keuangan():
    if current_user.role not in ["AK", "AS"]:
        return redirect("/login")

    # Ambil parameter dari request URL
    page = request.args.get('page', 1, type=int)
    jenis = request.args.get("jenis")
    kategori_id = request.args.get("kategori_id")
    bulan = request.args.get("bulan")
    tanggal_awal = request.args.get("tanggal_awal")
    tanggal_akhir = request.args.get("tanggal_akhir")

    kategori_list = Kategori.query.order_by(Kategori.nama).all()
    query = Transaksi.query.join(Kategori)

    # FILTER BERDASARKAN INPUT USER
    if kategori_id:
        query = query.filter(Transaksi.kategori_id == int(kategori_id))
    if jenis:
        query = query.filter(Kategori.jenis == jenis)
    if bulan:
        query = query.filter(db.extract("month", Transaksi.created_at) == int(bulan))
    if tanggal_awal:
        query = query.filter(Transaksi.created_at >= datetime.strptime(tanggal_awal, "%Y-%m-%d"))
    if tanggal_akhir:
        tgl_akhir_dt = datetime.strptime(tanggal_akhir, "%Y-%m-%d")
        tgl_akhir_max = datetime.combine(tgl_akhir_dt, time.max)
        query = query.filter(Transaksi.created_at <= tgl_akhir_max)

    # PAGINATION: Dipaksa batasi maksimal 10 data per halaman
    pagination = (
        query
        .order_by(Transaksi.created_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    transaksi_list = pagination.items 

    # HITUNG TOTAL UNTUK CARD INFORMASI
    total_transaksi = Transaksi.query.count()
    total_pemasukan = Transaksi.query.join(Kategori).filter(Kategori.jenis == "PEMASUKAN").count()
    total_pengeluaran = Transaksi.query.join(Kategori).filter(Kategori.jenis == "PENGELUARAN").count()
    
    total_pemasukan_card = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == "PEMASUKAN").scalar() or 0
    total_pengeluaran_card = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == "PENGELUARAN").scalar() or 0
    saldo_aktif = total_pemasukan_card - total_pengeluaran_card

    return render_template(
        "admin/AK.html",
        user=current_user,
        kategori_list=kategori_list,
        transaksi_list=transaksi_list,
        pagination=pagination, 
        total_transaksi=total_transaksi,
        total_pemasukan=total_pemasukan,
        total_pengeluaran=total_pengeluaran,
        total_pemasukan_card=total_pemasukan_card,
        total_pengeluaran_card=total_pengeluaran_card,
        saldo_aktif=saldo_aktif
    )

def dashboard_keuangan():
    if current_user.role not in ["AK", "AS"]:
        return redirect("/login")

    # 1. AMBIL WAKTU SEKARANG (UNTUK FILTER BULANAN)
    bulan_sekarang = datetime.now().month
    tahun_sekarang = datetime.now().year

    # 2. HITUNG METRIK GLOBAL (PEMASUKAN VS PENGELUARAN)
    total_pemasukan = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == "PEMASUKAN").scalar() or 0
    total_pengeluaran = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == "PENGELUARAN").scalar() or 0
    saldo_aktif = total_pemasukan - total_pengeluaran

    # 3. KAS SPESIFIK (MEMISAHKAN ZAKAT & INFAQ/SEDEKAH)
    # Menghitung nominal pemasukan yang nama kategorinya mengandung kata 'Zakat'
    kas_zakat = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(
        Kategori.jenis == "PEMASUKAN", 
        Kategori.nama.ilike('%zakat%')
    ).scalar() or 0
    
    # Sisa pemasukan lainnya otomatis masuk kategori Infaq/Sedekah/Lainnya
    kas_infaq = total_pemasukan - kas_zakat

    # 4. PENGELUARAN BULAN INI (DITAMPILKAN DI CARD KE-4)
    pengeluaran_bulan_ini = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(
        Kategori.jenis == "PENGELUARAN",
        db.extract("month", Transaksi.created_at) == bulan_sekarang,
        db.extract("year", Transaksi.created_at) == tahun_sekarang
    ).scalar() or 0

    # 5. LIMIT DATA: Hanya ambil 5 Transaksi Paling Baru (Tanpa filter/pagination ribet)
    transaksi_terbaru = (
        Transaksi.query.join(Kategori)
        .order_by(Transaksi.created_at.desc())
        .limit(5)
        .all()
    )

    # 6. LEMPAR DATA KE FILE HTML DASHBOARD BARU
    return render_template(
        "admin/components-AK/AK-dashboard.html",
        user=current_user,
        saldo_aktif=saldo_aktif,
        kas_zakat=kas_zakat,
        kas_infaq=kas_infaq,
        pengeluaran_bulan_ini=pengeluaran_bulan_ini,
        transaksi_terbaru=transaksi_terbaru
    )
