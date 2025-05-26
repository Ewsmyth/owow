from flask import Blueprint, render_template, redirect, url_for, flash
from .decorators import role_required
from flask_login import current_user, login_required

user = Blueprint('user', __name__)

@user.route('/<username>/user-home/')
@login_required
@role_required('user')
def user_home(username):
    if username != current_user.username:
        flash('Unauthorized access to another user\'s account', 'error')
        return redirect(url_for('auth.auth_login'))
    return render_template('user-home.html', username=username)

@user.route('/testing/')
def user_testing():
    return "Hello World"