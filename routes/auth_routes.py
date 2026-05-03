from flask import Blueprint
from controllers.user_controller import show_register, show_login, register_user, login_system,logout_system
from middleware.guest import guest_only





auth = Blueprint('auth', __name__)


@auth.route("/register", methods=["GET"])
@guest_only
def register_form():
    return show_register()

@auth.route("/register", methods=["POST"])
@guest_only
def register_store():
    return register_user()

@auth.route("/login",methods=["GET"])
@guest_only
def login_form():
    return show_login()

@auth.route("/login",methods=["POST"])
@guest_only
def login_sys():
    return login_system()

@auth.route("/logout",methods=["POST"])
def logout_sys():
    return logout_system()

