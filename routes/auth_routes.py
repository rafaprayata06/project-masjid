from flask import Blueprint
from controllers.user_controller import show_register

auth = Blueprint('auth', __name__)

@auth.route("/register")
def register():
    return show_register()