from flask import Blueprint, render_template, redirect, url_for, request, flash
from controllers.admin_controller import admin_humas, admin_super, admin_keuangan, update_user_controller, dashboard_keuangan, dashboard_humas
from controllers.management_humas.berita_management import store_berita, edit_berita
from controllers.management_humas.jadwal_management import admin_imam_store_controller, admin_imam_controller, admin_imam_delete_controller, admin_imam_update_controller
from controllers.management_keuangan.keuangan import admin_keuangan_store, export_keuangan, edit_transaksi, search_transaksi_ajax, search_transaksi_partial
from flask_login import current_user
from middleware.auth import login_required
from models.activity_log_model import ActivityLog
from models.user_model import User

admin = Blueprint('admin', __name__)

def handle_unauthorized():
    """
    Fungsi pembantu untuk melempar pesan SweetAlert (via Flash) 
    dan mengarahkan user kembali ke dashboard yang sesuai dengan role mereka.
    """
    flash('Akses ditolak! Anda tidak memiliki izin untuk membuka halaman tersebut.', 'error')
    if current_user.role == 'AS':
        return redirect(url_for('admin.admin_dashboard_show'))
    elif current_user.role == 'AH':
        return redirect(url_for('admin.admin_humas_dashboard'))
    elif current_user.role == 'AK':
        return redirect(url_for('admin.admin_keuangan_dashboard'))
    return redirect(url_for('admin.admin_dashboard_show'))


# ====================================================================
# BAGIAN ADMIN SUPER (Hanya Role 'AS' yang boleh masuk)
# ====================================================================

@admin.route("/admin-super/kelola-admin", methods=["GET"])
@login_required
def admin_super_kelola_admin():
    if current_user.role != 'AS':
        return handle_unauthorized()
    return admin_super()

@admin.route("/admin-super/dashboard", methods=["GET"])
@login_required
def admin_dashboard_show():
    if current_user.role != 'AS':
        return handle_unauthorized()
    return admin_super()  # <--- MODIFIKASI BARIS INI
@admin.route("/admin-super/finance", methods=["GET"])
@login_required
def admin_super_finance():
    if current_user.role != 'AS':
        return handle_unauthorized()
    return admin_keuangan()

@admin.route("/admin-super/news", methods=["GET"])
@login_required
def admin_super_news():
    if current_user.role != 'AS':
        return handle_unauthorized()
    return admin_humas()

@admin.route("/admin-super/schedules", methods=["GET"])
@login_required
def admin_super_imam():
    if current_user.role != 'AS':
        return handle_unauthorized()
    return admin_imam_controller()

@admin.route("/admin-super/users", methods=["GET"])
@login_required
def admin_super_users_list():
    if current_user.role != 'AS':
        return handle_unauthorized()
    return redirect(url_for('admin.admin_dashboard_show'))

@admin.route("/admin-super/users/update/<string:nim>", methods=["POST"])
@login_required
def update_user(nim):
    if current_user.role != 'AS':
        return handle_unauthorized()
    return update_user_controller(nim)

@admin.route('/admin-super/activity-logs', methods=['GET'])
@login_required
def view_activity_logs():
    if current_user.role != 'AS':
        return handle_unauthorized()

    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '', type=str)
    filter_action = request.args.get('action', '', type=str)
    filter_table = request.args.get('table', '', type=str)

    query = ActivityLog.query.join(User)

    if search_query:
        query = query.filter(
            (ActivityLog.user_nim.like(f"%{search_query}%")) | 
            (User.name.like(f"%{search_query}%")) |
            (ActivityLog.deskripsi.like(f"%{search_query}%"))
        )
    if filter_action:
        query = query.filter(ActivityLog.action == filter_action)
    if filter_table:
        query = query.filter(ActivityLog.target_table == filter_table)

    per_page = 10
    paginated_logs = query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    available_tables = [r[0] for r in ActivityLog.query.with_entities(ActivityLog.target_table).distinct().all()]

    return render_template(
        'admin/components-AS/view_logs.html', 
        logs=paginated_logs.items,
        pagination=paginated_logs,
        search=search_query,
        selected_action=filter_action,
        selected_table=filter_table,
        available_tables=available_tables
    )


# ====================================================================
# ROUTE HUMAS (Hanya Role 'AH' atau 'AS' yang boleh masuk)
# ====================================================================

@admin.route("/admin-humas", methods=["GET"])
@login_required
def admin_humas_show():
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return redirect(url_for('admin.admin_humas_dashboard'))

@admin.route("/admin-humas/dashboard", methods=["GET"])
@login_required
def admin_humas_dashboard():
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return dashboard_humas() 

@admin.route("/admin-humas/news", methods=["GET"])
@login_required
def admin_humas_news():
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return admin_humas()

@admin.route("/admin-humas/schedules", methods=["GET"])
@login_required
def admin_humas_imam():
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return admin_imam_controller()

@admin.route("/admin-humas/schedules/update/<int:id>", methods=["POST"])
@login_required
def admin_humas_imam_update(id):
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return admin_imam_update_controller(id)

@admin.route("/admin-humas/schedules/delete/<int:id>", methods=["POST"])
@login_required
def admin_humas_imam_delete(id):
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return admin_imam_delete_controller(id)

@admin.route("/admin-humas/schedules/store", methods=["POST"])
@login_required
def admin_humas_imam_store():
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return admin_imam_store_controller()

@admin.route("/admin-humas/news/store", methods=["POST"])
@login_required
def admin_humas_create():
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return store_berita()

@admin.route("/admin-humas/news/update/<string:id>", methods=["POST"])
@login_required
def update_berita(id):
    if current_user.role not in ['AH', 'AS']:
        return handle_unauthorized()
    return edit_berita(id)


# ====================================================================
# ROUTE KEUANGAN (Hanya Role 'AK' atau 'AS' yang boleh masuk)
# ====================================================================

@admin.route("/admin-keuangan", methods=["GET"])
@login_required
def admin_keuangan_show():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return redirect(url_for('admin.admin_keuangan_dashboard'))

@admin.route("/admin-keuangan/dashboard", methods=["GET"])
@login_required
def admin_keuangan_dashboard():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return dashboard_keuangan() 

@admin.route("/admin-keuangan/finance", methods=["GET"])
@login_required
def admin_keuangan_finance():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return admin_keuangan()

@admin.route("/admin-keuangan/finance/search", methods=["GET"])
@login_required
def admin_keuangan_search():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return search_transaksi_ajax()

@admin.route("/admin-keuangan/finance/partial", methods=["GET"])
@login_required
def admin_keuangan_partial():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return search_transaksi_partial()

@admin.route("/admin-keuangan/finance/export", methods=["GET"])
@login_required
def export_keuangan_file():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return export_keuangan()

@admin.route("/admin-keuangan/finance/store", methods=["POST"])
@login_required
def admin_keuangan_create():
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return admin_keuangan_store()

@admin.route("/admin-keuangan/finance/update/<int:id>", methods=["POST"])
@login_required
def update_transaksi(id):
    if current_user.role not in ['AK', 'AS']:
        return handle_unauthorized()
    return edit_transaksi(id)