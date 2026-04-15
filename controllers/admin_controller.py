from flask import Blueprint
from flask import render_template, request, redirect, flash
from flask_login import current_user, login_required

@login_required
def admin_super():
    return render_template("admin/AS.html", user=current_user)