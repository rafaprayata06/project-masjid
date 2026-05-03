from functools import wraps
from flask import redirect, flash
from flask_login import current_user


def guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Kalau user sudah login
        if current_user.is_authenticated:

            role = current_user.role.strip() if current_user.role else None

            # Admin Super
            if role == "AS":
                flash("Anda sudah login sebagai Admin Super", "info")
                return redirect("/admin-super/users")

            # Admin Humas
            elif role == "AH":
                flash("Anda sudah login sebagai Admin Humas", "info")
                return redirect("/admin-humas/news")

            # Admin Keuangan
            elif role == "AK":
                flash("Anda sudah login sebagai Admin Keuangan", "info")
                return redirect("/admin-keuangan")

            # Default fallback
            flash("Anda sudah login", "info")
            return redirect("/")

        return f(*args, **kwargs)

    return decorated_function