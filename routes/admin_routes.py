from flask import Blueprint, render_template, redirect, url_for
from controllers.admin_controller import admin_humas,admin_super, admin_keuangan, update_user_controller
from controllers.management_humas.berita_management import store_berita, edit_berita
from controllers.management_keuangan.keuangan import admin_keuangan_store,export_keuangan,edit_transaksi
from flask_login import current_user
from middleware.auth import login_required

admin = Blueprint('admin', __name__)


# ====================================================================
# BAGIAN ADMIN SUPER (Udah Fix, Gak Bakal Bentrok)
# ====================================================================

@admin.route("/admin-super/kelola-admin", methods=["GET"])
@login_required
def admin_super_kelola_admin():
    return admin_super()
@admin.route("/admin-super/dashboard", methods=["GET"])
@login_required
def admin_dashboard_show():
    return render_template("admin/AS.htmL", user=current_user)

@admin.route("/admin-super/finance", methods=["GET"])
@login_required
def admin_super_finance():
    return admin_keuangan()

@admin.route("/admin-super/news", methods=["GET"])
@login_required
def admin_super_news():
    return admin_humas()

@admin.route("/admin-super/news", methods=["POST"])
@login_required
def admin_super_news_store():
    return store_berita()

@admin.route("/admin-super/news/update/<string:id>", methods=["POST"])
@login_required
def admin_super_news_edit(id):
    return edit_berita(id)

@admin.route("/admin-super/users", methods=["GET"])
@login_required
def admin_super_users_list():
    # Kalau lu mau misahin halaman list user, bisa pake ini
    # Tapi kalau dashboard & list user jadi satu di AS-users.html, ini bisa buat redirect aja
    return redirect(url_for('admin.admin_dashboard_show'))

@admin.route("/admin-super/users/update/<string:nim>", methods=["POST"])
@login_required
def update_user(nim):
    return update_user_controller(nim)


# ====================================================================
# BAGIAN ADMIN HUMAS (Udah dibersihin dari duplikat, tinggal copas)
# ====================================================================
@admin.route("/admin-humas/news", methods=["GET"])
@login_required
def admin_humas_show():
    return admin_humas()

@admin.route("/admin-humas/news", methods=["POST"])
@login_required
def admin_humas_berita():
    return store_berita()

@admin.route("/admin-humas/news/update/<string:id>", methods=["POST"])
@login_required
def admin_humas_berita_edit(id):
    return edit_berita(id)

@admin.route("/admin-humas/dashboard", methods=["GET"])
@login_required
def admin_humas_dashboard():
    return render_template("admin/AS-users.html", user=current_user)


# ====================================================================
# BAGIAN ADMIN KEUANGAN (Udah dibersihin dari duplikat, tinggal copas)
# ====================================================================

# 1. Alamat utama: kalau diketik /admin-keuangan, otomatis DILEMPAR ke /dashboard
@admin.route("/admin-keuangan", methods=["GET"])
@login_required
def admin_keuangan_show():
    return redirect(url_for('admin.admin_keuangan_dashboard'))

# 2. Alamat Dashboard (menangani halaman awal admin keuangan)
@admin.route("/admin-keuangan/dashboard", methods=["GET"])
@login_required
def admin_keuangan_dashboard():
    return render_template("admin/AS-users.html", user=current_user)

# 3. Alamat Kelola Keuangan (menangani halaman tabel transaksi)
@admin.route("/admin-keuangan/finance", methods=["GET"])
@login_required
def admin_keuangan_finance():
    return admin_keuangan()
@admin.route("/admin-keuangan/finance/store", methods=["POST"])
@login_required
def admin_keuangan_create():
    return admin_keuangan_store()

@admin.route("/admin-keuangan/finance/export")
def export_keuangan_file():
     return export_keuangan()

@admin.route( "/admin-keuangan/finance/update/<int:id>",methods=["POST"])
@login_required
def update_transaksi(id):
    return edit_transaksi(id)