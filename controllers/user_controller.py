from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user

user_bp = Blueprint(
    'user',
    __name__,
    url_prefix="/user"
)

@user_bp.route('/')
@login_required
def index():
    return render_template('./user/index.html')