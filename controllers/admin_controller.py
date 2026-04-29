from flask import Blueprint
from flask import render_template, request, redirect, flash
from flask_login import current_user, login_required
from models.user_model import User
from models.berita_model import Berita
from flask import request, redirect, flash
from database.db import db




@login_required
def admin_super():
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
    return render_template("admin/AS-users.html", user=current_user,users=users, is_empty=is_empty)

def update_user_controller(nim):
    user = User.query.get_or_404(nim)

    role = request.form.get("role")
    active = request.form.get("active")

    # VALIDASI SEDERHANA
    if active not in ["0", "1", "2"]:
        flash("Status tidak valid", "error")
        return redirect("/admin/super")

    if role not in ["AS", "AK", "AH", "", None]:
        flash("Role tidak valid", "error")
        return redirect("/admin/super")

    # UPDATE
    user.role = role if role != "" else None
    user.active = int(active)

    db.session.commit()

    flash("User berhasil diupdate", "success")
    return redirect("/admin-super/users")
def admin_humas():
    berita =  Berita.query.order_by(Berita.id.desc()).all()
    return render_template("admin/AH.html", user=current_user,semua_berita=berita)

def admin_keuangan():
    return render_template("admin/AK.html", user=current_user)