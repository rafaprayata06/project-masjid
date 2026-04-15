from flask import render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required
from models.user_model import User
from database.db import db
from werkzeug.security import generate_password_hash, check_password_hash


# ================= REGISTER PAGE =================
def show_register():
    return render_template("auth/register.html")


# ================= REGISTER LOGIC =================
def register_user():
    nim = request.form.get("nim")
    name = request.form.get("name")
    jurusan = request.form.get("jurusan")
    jenis_kelamin = request.form.get("jenis_kelamin")   
    raw_password = request.form.get("password")

    # ⚠️ validasi sederhana
    if not nim or not name or not raw_password:
        return "Data tidak boleh kosong!"

    password = generate_password_hash(raw_password)

    user = User(
        nim=nim,
        name=name,
        jurusan=jurusan,
        jenis_kelamin=jenis_kelamin,
        password=password,
        active='0'
    )

    db.session.add(user)
    db.session.commit()

    return redirect("/login")


# ================= LOGIN PAGE =================
def show_login():
    return render_template("auth/login.html")


# ================= LOGIN LOGIC =================
def login_system():
    if request.method == 'POST':
        nim = request.form.get('nim')
        password = request.form.get('password')

        user = User.query.filter_by(nim=nim).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # 🔥 redirect sesuai role
            if user.role == 'AS':
                return redirect('/admin-super')
            elif user.role == 'AK':
                return redirect('/admin-keuangan')
            elif user.role=='AH':
                return redirect('/admin-humas')
            else:
                 return redirect('/login')
        flash("Login gagal! NIM atau password salah")
       

    # ✅ GET request
    return render_template("auth/login.html")


# ================= LOGOUT =================
@login_required
def logout():
    logout_user()
    return redirect('/login')