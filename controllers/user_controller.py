import re # Pastikan sudah di-import di bagian paling atas file
from flask import render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from database.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


# ================= REGISTER PAGE =================
def show_register():
    return render_template("auth/register.html")

# ================= REGISTER LOGIC =================
def register_user():
    # Ambil IP Address pendaftar untuk melacak limit
    user_ip = request.remote_addr 
    
    # Hitung batas waktu (24 jam yang lalu)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    
    # Hitung berapa kali pendaftaran dalam 24 jam terakhir
    reg_count = User.query.filter(
        User.created_at >= yesterday
    ).count()

    if reg_count >= 3:
        flash("Maaf, batas pendaftaran maksimal 3 kali dalam 24 jam telah tercapai.", "danger")
        return redirect("/register")

    # Ambil data form
    nim = request.form.get("nim")
    name = request.form.get("name")
    jurusan = request.form.get("jurusan")
    jenis_kelamin = request.form.get("jenis_kelamin")   
    raw_password = request.form.get("password")

    # --- VALIDASI 1: CEK DATA KOSONG ---
    if not nim or not name or not raw_password or not jenis_kelamin or not jurusan:
        flash("Data tidak boleh kosong!", "warning")
        return redirect("/register")

    # --- VALIDASI 2: LIMIT 3 KALI PER 24 JAM (Backend) ---
    # Menghitung pendaftaran dalam 24 jam terakhir
    waktu_batas = datetime.utcnow() - timedelta(hours=24)
    jumlah_daftar = User.query.filter(User.created_at >= waktu_batas).count()

    if jumlah_daftar >= 3:
        flash("Gagal: Batas maksimal pendaftaran adalah 3 kali dalam 24 jam.", "error")
        return redirect("/register")

    # --- VALIDASI 3: SYARAT PASSWORD (Min 5, Huruf & Angka) ---
    if len(raw_password) < 5:
        flash("Password gagal: Minimal harus 5 karakter.", "warning")
        return redirect("/register")
    
    if not (re.search("[A-Za-z]", raw_password) and re.search("[0-9]", raw_password)):
        flash("Password gagal: Harus kombinasi huruf dan angka.", "warning")
        return redirect("/register")

    # -------------------------------------------------------
    # Jika lolos semua validasi di atas, baru jalankan di bawah ini
    # -------------------------------------------------------

    # Hash Password
    password = generate_password_hash(raw_password)

    user = User(
        nim=nim,
        name=name,
        jurusan=jurusan,
        jenis_kelamin=jenis_kelamin,
        password=password,
        active=0,
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(user)
        db.session.commit()
        flash("Registrasi berhasil! Silakan login.", "success")
        return redirect("/login")
    except Exception as e:
        db.session.rollback()
        flash("Terjadi kesalahan atau NIM sudah terdaftar.", "error")
        return redirect("/register")

# ================= LOGIN PAGE =================
def show_login():
    return render_template("auth/login.html")
def login_system():
    if request.method == 'POST':
        nim = str(request.form.get('nim')).strip()
        password = request.form.get('password')

        user = User.query.filter_by(nim=nim).first()

        if user and check_password_hash(user.password, password):

            # CEK STATUS DULU SEBELUM LOGIN
            if int(user.active) == 2:
                flash("Akun kamu sedang tidak aktif!", "error")
                return redirect('/login')

            login_user(user)

            role = user.role.strip() if user.role else None

            if role == 'AS':
                flash("Selamat datang, Admin Super!", "success")
                return redirect('/admin-super/users')

            elif role == 'AK':
                flash("Selamat datang, Admin Keuangan!", "success")
                return redirect('/admin-keuangan/dashboard')

            elif role == 'AH':
                flash("Selamat datang, Admin Humas!", "success")
                return redirect('/admin-humas/dashboard')

            else:
                flash("Role tidak dikenali!", "error")
                return redirect('/login')

        flash("NIM atau password salah!", "error")
        return redirect('/login')

    return render_template("auth/login.html")
# ================= LOGOUT =================
@login_required
def logout_system():
    logout_user()
    return redirect('/login')