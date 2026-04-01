from flask import Blueprint, render_template

web = Blueprint('web' , __name__)

@web.route("/")
def home():
    return render_template("index.html")

@web.route("/jadwal")
def jadwal():
    return render_template("jadwal.html")

@web.route("/keuangan")
def keuangan():
    return render_template("keuangan.html")

@web.route("/profil")
def profil():
    return render_template("profil.html")

@web.route("/infaq")
def infaq():
    return render_template("infaq.html")

@web.route("/admin/<role>")
def admin(role):
    return render_template("admin.html", role=role)

@web.route("/berita")
def berita():
    return render_template("berita.html")

@web.route("/galeri")
def galeri():
    return render_template("galeri.html")