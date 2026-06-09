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