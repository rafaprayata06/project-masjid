from flask import render_template, request, redirect, flash, abort, jsonify
from flask_login import current_user, login_required
from database.db import db
from datetime import datetime, time as dtime
from sqlalchemy import func, extract, or_

# Import Semua Model secara Global di Atas
from models.kategori_model import Kategori
from models.transaksi_model import Transaksi
from models.user_model import User
from models.berita_model import Berita
from models.ustadz_model import Ustadz
from models.jadwal_khutbah_model import JadwalKhutbah
from models.activity_log_model import ActivityLog
# Pastikan nama berkas/subfolder model jadwal riil Anda sesuai di bawah ini:


# ====================================================================
# BAGIAN ADMIN SUPER
# ====================================================================

def admin_super():
    if current_user.role != 'AS':
        flash('Akses ditolak! Anda tidak memiliki izin untuk membuka halaman tersebut.', 'error')
        return redirect("/login")

    # --- 1. AMBIL DATA AGREGAT UNTUK STATS CARDS ---
    pemasukan = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == 'PEMASUKAN').scalar() or 0
    pengeluaran = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == 'PENGELUARAN').scalar() or 0
    saldo_masjid = pemasukan - pengeluaran

    # Total User & Berita
    total_admin = User.query.count()
    total_berita_publish = Berita.query.filter_by(status='publish').count()
    total_berita_draft = Berita.query.filter_by(status='draft').count()

    stats = {
        'saldo_masjid': saldo_masjid,
        'total_admin': total_admin,
        'berita_publish': total_berita_publish,
        'berita_draft': total_berita_draft
    }

    # --- 2. AMBIL DATA DINAMIS 6 BULAN TERAKHIR UNTUK CHART ---
    hari_ini = datetime.now().date()
    bulan_sekarang = hari_ini.month
    tahun_sekarang = hari_ini.year

    # Ambil 6 bulan ke belakang
    months_labels = []
    pemasukan_6bulan = []
    pengeluaran_6bulan = []
    
    nama_bulan_singkat = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun',
        7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'
    }

    for i in range(5, -1, -1):
        m = bulan_sekarang - i
        y = tahun_sekarang
        if m <= 0:
            m += 12
            y -= 1
        
        months_labels.append(nama_bulan_singkat[m])
        
        # Ambil total pemasukan bulan spesifik
        tot_in = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori)\
            .filter(Kategori.jenis == 'PEMASUKAN', extract('month', Transaksi.created_at) == m, extract('year', Transaksi.created_at) == y).scalar() or 0
        # Ambil total pengeluaran bulan spesifik
        tot_out = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori)\
            .filter(Kategori.jenis == 'PENGELUARAN', extract('month', Transaksi.created_at) == m, extract('year', Transaksi.created_at) == y).scalar() or 0
            
        pemasukan_6bulan.append(float(tot_in))
        pengeluaran_6bulan.append(float(tot_out))

    chart_payload = {
        'labels': months_labels,
        'pemasukan': pemasukan_6bulan,
        'pengeluaran': pengeluaran_6bulan
    }

    # --- 3. JADWAL KHUTBAH / IMAM BULAN BERJALAN (VERSI HUMAS) ---
    nama_bulan_id = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    label_bulan_aktif = nama_bulan_id.get(bulan_sekarang, "Bulan Ini")

    jadwal_bulan_ini = JadwalKhutbah.query.join(Ustadz)\
        .filter(extract('month', JadwalKhutbah.tanggal) == bulan_sekarang)\
        .filter(extract('year', JadwalKhutbah.tanggal) == tahun_sekarang)\
        .order_by(JadwalKhutbah.tanggal.asc()).all()

    list_jadwal_tabel = []
    for jw in jadwal_bulan_ini:
        tgl = jw.tanggal
        if isinstance(tgl, str):
            tgl = datetime.strptime(tgl.split()[0], "%Y-%m-%d").date()
        
        hari_str = tgl.strftime('%d')
        jumat_ke = ((tgl.day - 1) // 7) + 1
        
        list_jadwal_tabel.append({
            'hari_label': f"Jum, {hari_str} {tgl.strftime('%b')}",
            'sholat': f"Shalat Jumat - Pekan {jumat_ke}",
            'ustadz': jw.ustadz.nama,
            'is_next': (tgl >= hari_ini)
        })

    # --- 4. AKTIVITAS TERBARU ---
    logs_terbaru = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()

    return render_template(
        "admin/AS.html", 
        user=current_user, 
        stats=stats,             
        chart=chart_payload, 
        logs=logs_terbaru, 
        schedules=list_jadwal_tabel,
        label_bulan_aktif=label_bulan_aktif
    )
def update_user_controller(nim):
    user = User.query.get_or_404(nim)

    role = request.form.get("role")
    active = request.form.get("active")

    if active not in ["0", "1", "2"]:
        flash("Status tidak valid", "error")
        return redirect("/admin-super/users")

    if role not in ["AS", "AK", "AH", "", None]:
        flash("Role tidak valid", "error")
        return redirect("/admin-super/users")

    if user.role == "AS":
        flash("Admin Super tidak dapat diubah", "error")
        return redirect("/admin-super/users")

    user.role = role if role != "" else None
    user.active = int(active)

    db.session.commit()

    flash("User berhasil diupdate", "success")
    return redirect("/admin-super/kelola-admin")


# ====================================================================
# BAGIAN ADMIN HUMAS
# ====================================================================

@login_required
def admin_humas():
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")
    berita = Berita.query.order_by(Berita.id.desc()).all()
    return render_template("admin/AH.html", user=current_user, semua_berita=berita)

@login_required
def dashboard_humas():
    if current_user.role not in ["AH", "AS"]:
        return redirect("/login")

    # 1. Perhitungan Statistik Berita
    total_berita = Berita.query.count()
    berita_publish = Berita.query.filter_by(status='publish').count() 
    berita_draft = Berita.query.filter_by(status='draft').count()

    # 2. Perhitungan Jumlah Ustadz Unik
    total_ustadz = Ustadz.query.count()

    # 3. Pengambilan Jadwal Dinamis Berdasarkan Bulan Berjalan Saat Ini
    hari_ini = datetime.now().date()
    bulan_sekarang = hari_ini.month
    tahun_sekarang = hari_ini.year

    nama_bulan_id = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    label_bulan_aktif = nama_bulan_id.get(bulan_sekarang, "Bulan Ini")

    jadwal_bulan_ini = JadwalKhutbah.query.join(Ustadz)\
        .filter(extract('month', JadwalKhutbah.tanggal) == bulan_sekarang)\
        .filter(extract('year', JadwalKhutbah.tanggal) == tahun_sekarang)\
        .order_by(JadwalKhutbah.tanggal.asc()).all()

    list_jadwal_tabel = []
    for idx, jw in enumerate(jadwal_bulan_ini):
        tgl = jw.tanggal
        if isinstance(tgl, str):
            tgl = datetime.strptime(tgl.split()[0], "%Y-%m-%d").date()
        
        hari_str = tgl.strftime('%d')
        jumat_ke = ((tgl.day - 1) // 7) + 1
        
        list_jadwal_tabel.append({
            'hari_label': f"Jum, {hari_str} {tgl.strftime('%b')}",
            'sholat': f"Shalat Jumat - Pekan {jumat_ke}",
            'ustadz': jw.ustadz.nama,
            'is_next': (tgl >= hari_ini) 
        })

    return render_template(
        "admin/components-AH/AH_dashboard.html", 
        view="dashboard", 
        user=current_user,
        total_berita=total_berita,
        berita_publish=berita_publish,
        berita_draft=berita_draft,
        total_ustadz=total_ustadz,
        list_jadwal_tabel=list_jadwal_tabel,
        label_bulan_aktif=label_bulan_aktif
    )


# ====================================================================
# BAGIAN ADMIN KEUANGAN
# ====================================================================

def admin_keuangan():
    if current_user.role not in ["AK", "AS"]:
        abort(403)

    page = request.args.get('page', 1, type=int)
    q = request.args.get("q", "").strip()
    jenis = request.args.get("jenis", "")
    kategori_id = request.args.get("kategori_id", "")
    bulan = request.args.get("bulan", "")
    tanggal_awal = request.args.get("tanggal_awal", "")
    tanggal_akhir = request.args.get("tanggal_akhir", "")

    kategori_list = Kategori.query.order_by(Kategori.nama).all()
    query = Transaksi.query.join(Kategori)

    if q:
        query = query.filter(
            or_(
                Transaksi.keterangan.ilike(f"%{q}%"),
                Kategori.nama.ilike(f"%{q}%")
            )
        )

    if jenis:
        query = query.filter(Kategori.jenis == jenis)

    if kategori_id:
        query = query.filter(Transaksi.kategori_id == int(kategori_id))

    if bulan:
        query = query.filter(extract("month", Transaksi.created_at) == int(bulan))

    if tanggal_awal:
        query = query.filter(Transaksi.created_at >= datetime.strptime(tanggal_awal, "%Y-%m-%d"))

    if tanggal_akhir:
        tgl_akhir_dt = datetime.strptime(tanggal_akhir, "%Y-%m-%d")
        query = query.filter(Transaksi.created_at <= datetime.combine(tgl_akhir_dt, dtime.max))

    pagination = query.order_by(Transaksi.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    transaksi_list = pagination.items

    dashboard_query = Transaksi.query.join(Kategori).all()
    total_pemasukan_card = 0
    total_pengeluaran_card = 0

    for trx in dashboard_query:
        if trx.kategori.jenis == "PEMASUKAN":
            total_pemasukan_card += trx.jumlah
        elif trx.kategori.jenis == "PENGELUARAN":
            total_pengeluaran_card += trx.jumlah

    saldo_aktif = total_pemasukan_card - total_pengeluaran_card
    total_perlu_verifikasi = 0
    jumlah_transaksi_pending = 0

    summary_query = query.order_by(None).all()
    total_pemasukan_filter = 0
    total_pengeluaran_filter = 0

    for trx in summary_query:
        if trx.kategori.jenis == "PEMASUKAN":
            total_pemasukan_filter += trx.jumlah
        elif trx.kategori.jenis == "PENGELUARAN":
            total_pengeluaran_filter += trx.jumlah

    saldo_filter = total_pemasukan_filter - total_pengeluaran_filter
    jumlah_transaksi_filter = len(summary_query)

    return render_template(
        "admin/AK.html",
        transaksi_list=transaksi_list,
        pagination=pagination,
        kategori_list=kategori_list,
        total_pemasukan_card=total_pemasukan_card,
        total_pengeluaran_card=total_pengeluaran_card,
        saldo_aktif=saldo_aktif,
        total_perlu_verifikasi=total_perlu_verifikasi,
        jumlah_transaksi_pending=jumlah_transaksi_pending,
        total_pemasukan_filter=total_pemasukan_filter,
        total_pengeluaran_filter=total_pengeluaran_filter,
        saldo_filter=saldo_filter,
        jumlah_transaksi_filter=jumlah_transaksi_filter
    )

def dashboard_keuangan():
    if current_user.role not in ["AK", "AS"]:
        return redirect("/login")

    tahun_dipilih = request.args.get('tahun', default=datetime.now().year, type=int)

    total_pemasukan = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == "PEMASUKAN").scalar() or 0
    total_pengeluaran = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == "PENGELUARAN").scalar() or 0
    saldo_aktif = total_pemasukan - total_pengeluaran

    pemasukan_bulanan = [0] * 12
    pengeluaran_bulanan = [0] * 12

    data_in = db.session.query(
        extract('month', Transaksi.created_at).label('bulan'),
        func.sum(Transaksi.jumlah).label('total')
    ).join(Kategori).filter(Kategori.jenis == "PEMASUKAN", extract('year', Transaksi.created_at) == tahun_dipilih).group_by('bulan').all()

    data_out = db.session.query(
        extract('month', Transaksi.created_at).label('bulan'),
        func.sum(Transaksi.jumlah).label('total')
    ).join(Kategori).filter(Kategori.jenis == "PENGELUARAN", extract('year', Transaksi.created_at) == tahun_dipilih).group_by('bulan').all()

    for row in data_in:
        pemasukan_bulanan[int(row.bulan) - 1] = float(row.total)

    for row in data_out:
        pengeluaran_bulanan[int(row.bulan) - 1] = float(row.total)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'pemasukan': pemasukan_bulanan,
            'pengeluaran': pengeluaran_bulanan
        })

    transaksi_terbaru = Transaksi.query.join(Kategori).order_by(Transaksi.created_at.desc()).limit(5).all()

    return render_template(
        "admin/components-AK/AK-dashboard.html",
        user=current_user,
        total_pemasukan=total_pemasukan,
        total_pengeluaran=total_pengeluaran,
        saldo_aktif=saldo_aktif,
        chart_pemasukan=pemasukan_bulanan,
        chart_pengeluaran=pengeluaran_bulanan,
        tahun_dipilih=tahun_dipilih,
        transaksi_terbaru=transaksi_terbaru
    )