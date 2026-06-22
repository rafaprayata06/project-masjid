from flask import Blueprint, render_template, redirect, url_for
from controllers.admin_controller import admin_humas,admin_super, admin_keuangan, update_user_controller, dashboard_keuangan, dashboard_humas, admin_imam_controller, admin_imam_update_row_controller, admin_imam_store_controller
from controllers.management_humas.berita_management import store_berita, edit_berita
from controllers.management_keuangan.keuangan import admin_keuangan_store,export_keuangan,edit_transaksi, search_transaksi_ajax, search_transaksi_partial
from flask_login import current_user
from middleware.auth import login_required
from functools import wraps

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
# ROUTE HUMAS 
# ====================================================================

# 1. Alamat Utama: Otomatis lempar ke Dashboard
@admin.route("/admin-humas", methods=["GET"])
@login_required
def admin_humas_show():
    return redirect(url_for('admin.admin_humas_dashboard'))


# 2. Dashboard Humas (FIX: Sekarang memanggil fungsi utama untuk render AH_dashboard.html)
@admin.route("/admin-humas/dashboard", methods=["GET"])
@login_required
def admin_humas_dashboard():
    return dashboard_humas() 


# 3. Tabel Data Berita Humas (Bisa diakses AH & AS)
@admin.route("/admin-humas/news", methods=["GET"])
@login_required
def admin_humas_news():
    return admin_humas()

# 4. Halaman Utama Kelola Jadwal Imam
@admin.route("/admin-humas/schedules", methods=["GET"])
@login_required
def admin_humas_imam():
    return admin_imam_controller()

# 5. Handler Simpan Perubahan Per Hari (POST Sementara)
@admin.route("/admin-humas/schedules/update-row/<int:id>", methods=["POST"])
@login_required
def admin_humas_imam_update_row(id):
    return admin_imam_update_row_controller(id)

# 6. Handler Tambah Pekan Jadwal Baru (POST Sementara)
@admin.route("/admin-humas/schedules/store", methods=["POST"])
@login_required
def admin_humas_imam_store():
    return admin_imam_store_controller()


# --- PROSES MANIPULASI DATA (MUTASI/CRUD): MUTLAK HANYA ROLE AH ---
# Admin Super (AS) otomatis ditolak 403 jika nekat memanipulasi rute di bawah

# 4. Tambah Berita
@admin.route("/admin-humas/news/store", methods=["POST"])
@login_required
def admin_humas_create():
    return store_berita()


# 5. Update/Edit Berita
@admin.route("/admin-humas/news/update/<string:id>", methods=["POST"])
@login_required
def update_berita(id):
    return edit_berita(id)



# ====================================================================
# ROUTE KEUANGAN 
# ====================================================================


# 1. Alamat Utama: Otomatis lempar ke Dashboard
@admin.route("/admin-keuangan", methods=["GET"])
@login_required
def admin_keuangan_show():
    return redirect(url_for('admin.admin_keuangan_dashboard'))


# 2. Dashboard Keuangan (FIX: Sekarang memanggil fungsi utama untuk render AK.html)
@admin.route("/admin-keuangan/dashboard", methods=["GET"])
@login_required
def admin_keuangan_dashboard():
    return dashboard_keuangan() 


# 3. Tabel Data Transaksi Keuangan (Bisa diakses AK & AS)
@admin.route("/admin-keuangan/finance", methods=["GET"])
@login_required
def admin_keuangan_finance():
    return admin_keuangan()

# 3b. AJAX Search Transaksi (NEW - untuk dynamic search)
@admin.route("/admin-keuangan/finance/search", methods=["GET"])
@login_required
def admin_keuangan_search():
    return search_transaksi_ajax()

@admin.route("/admin-keuangan/finance/partial", methods=["GET"])
@login_required
def admin_keuangan_partial():
    return search_transaksi_partial()

# 4. Export File Excel (FIX: Sekarang sudah aman terkunci)
@admin.route("/admin-keuangan/finance/export", methods=["GET"])
@login_required
def export_keuangan_file():
     return export_keuangan()


# --- PROSES MANIPULASI DATA (MUTASI/CRUD): MUTLAK HANYA ROLE AK ---
# Admin Super (AS) otomatis ditolak 403 jika nekat memanipulasi rute di bawah

# 5. Tambah Transaksi
@admin.route("/admin-keuangan/finance/store", methods=["POST"])
@login_required
def admin_keuangan_create():
    return admin_keuangan_store()


# 6. Update/Edit Transaksi
@admin.route("/admin-keuangan/finance/update/<int:id>", methods=["POST"])
@login_required
def update_transaksi(id):
    return edit_transaksi(id)