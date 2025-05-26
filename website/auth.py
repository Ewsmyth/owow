from flask import Blueprint, request, flash, redirect, url_for, render_template
from .models import db, User
from sqlalchemy import or_
from datetime import datetime
from flask_login import login_user
from .utils import bcrypt
from website.forms.auth_forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route("/", methods=['GET', 'POST'])
def auth_login():
    form = LoginForm()

    if form.validate_on_submit():
        usrnmEmail = usrnmEmail = form.username.data
        password = form.password.data

        usrDbCheck = User.query.filter(or_(User.email == usrnmEmail, User.username == usrnmEmail)).first()

        if usrDbCheck:
            if not usrDbCheck.is_active:
                flash('Invalid email or password.', 'error')
                usrDbCheck.failed_login_attempts += 1
                db.session.commit()
                return redirect(url_for('auth.auth_login'))
            
            if usrDbCheck.failed_login_attempts >= 3:
                usrDbCheck.is_active = False
                db.session.commit()
                flash('Your account is locked due to failed login attempts.', 'error')
                return redirect(url_for('auth.auth_login'))

            # Validate the password
            if bcrypt.check_password_hash(usrDbCheck.password, password):
                usrDbCheck.failed_login_attempts = 0
                usrDbCheck.last_login = datetime.utcnow()
                db.session.commit()

                login_user(usrDbCheck)

                # Handle first login logic
                if usrDbCheck.first_login:
                    usrDbCheck.first_login = False
                    db.session.commit()

                # Redirect based on role
                if usrDbCheck.role.role_name == 'admin':
                    return redirect(url_for('admin.admin_welcome' if usrDbCheck.first_login else 'admin.admin_home'))
                elif usrDbCheck.role.role_name == 'user':
                    return redirect(url_for('user.user_welcome' if usrDbCheck.first_login else 'user.user_home'))

                flash('You do not have a valid authority.', 'error')
                return redirect(url_for('auth.auth_login'))
            else:
                usrDbCheck.failed_login_attempts += 1
                db.session.commit()
                flash('Invalid email or password.', 'error')
                return redirect(url_for('auth.auth_login'))

        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.auth_login'))

    return render_template('auth-login.html', form=form)

@auth.route("/", methods=['GET', 'POST'])
def auth_register():
    return "Hello World"