from flask import Blueprint
from controllers.user_controller import show_register
from controllers.user_controller import show_login



auth = Blueprint('auth', __name__)

@auth.route("/register")
def register():
    return show_register()

@auth.route("/login")
def login():
    return show_login()

