from flask import Blueprint
from controllers.admin_controller import admin_humas, admin_super, admin_keuangan




admin = Blueprint('admin', __name__)


@admin.route("/admin-super", methods=["GET"])
def admin_super_show():
    return admin_super()

@admin.route("/admin-humas", methods=["GET"])
def admin_humas_show():
    return admin_humas()

@admin.route("/admin-keuangan", methods=["GET"])
def admin_keuangan_show():
    return admin_keuangan()

