from flask import render_template
def show_register():
    return render_template("auth/register.html")