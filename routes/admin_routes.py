from flask import Blueprint
from controllers.admin_controller import admin_humas, admin_super, admin_keuangan,update_user_controller
from controllers.management_humas.berita_management import store_berita,edit_berita
from flask_login import current_user



admin = Blueprint('admin', __name__)


@admin.route("/admin-super/users", methods=["GET"])
def admin_super_show():
    return admin_super()

@admin.route("/admin/users/update/<string:nim>", methods=["POST"])
def update_user(nim):
    return update_user_controller(nim)
@admin.route("/admin-humas", methods=["GET"])
def admin_humas_show():
    return admin_humas()
@admin.route("/admin-humas", methods=["POST"])
def admin_humas_berita():
    return store_berita()
@admin.route("/admin-humas/update/<string:id>", methods=["POST"])
def admin_humas_berita_edit(id):
    return edit_berita(id)

@admin.route("/admin-keuangan", methods=["GET"])
def admin_keuangan_show():
    return admin_keuangan()

