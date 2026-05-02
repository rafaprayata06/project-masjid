from flask import render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from database.db import db
from datetime import datetime
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

    if not nim or not name or not raw_password:
        return "Data tidak boleh kosong!"

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

    db.session.add(user)
    db.session.commit()

    return redirect("/login")


# ================= LOGIN PAGE =================
def show_login():
    return render_template("auth/login.html")

def login_system():
    if request.method == 'POST':
        nim = str(request.form.get('nim')).strip()
        password = request.form.get('password')

        user = User.query.filter_by(nim=nim).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            role = user.role.strip() if user.role else None

            if user.active == 2:
                flash("Akun kamu sedang tidak aktif!", "error")
                return redirect('/login')

            if role == 'AS':
                flash("Selamat datang, Admin Super!", "success")
                return redirect('/admin-super/users')
            elif role == 'AK':
                flash("Selamat datang, Admin Keuangan!", "success")
                return redirect('/admin-keuangan')
            elif role == 'AH':
                flash("Selamat datang, Admin Humas!", "success")
                return redirect('/admin-humas/news')
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