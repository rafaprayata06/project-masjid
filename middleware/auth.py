from functools import wraps
from flask import session, redirect, flash
from flask_login import current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Kalau belum login
        if  not current_user.is_authenticated:
            flash("Silakan login terlebih dahulu", "error")
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function