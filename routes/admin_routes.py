from flask import Blueprint
from controllers.admin_controller import admin_super




admin = Blueprint('admin', __name__)


@admin.route("/admin-super", methods=["GET"])
def admin_super_show():
    return admin_super()
