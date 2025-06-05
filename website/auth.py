from flask import Blueprint, request, flash, redirect, url_for, render_template
from .models import db, User, Role
from sqlalchemy import or_
from datetime import datetime
from flask_login import login_user
from .utils import bcrypt
from website.forms.auth_forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)

@auth.route("/", methods=['GET', 'POST'])
def auth_login():
    form = LoginForm()

    if form.validate_on_submit():
        usrnmEmail = form.username.data
        password = form.password.data
        rememberMe = form.remember.data
        print(f'Username or Email: {usrnmEmail}')

        usrDbCheck = User.query.filter(or_(User.email == usrnmEmail, User.username == usrnmEmail)).first()

        if usrDbCheck:
            if not usrDbCheck.is_active:
                flash('Invalid email or password.', 'error')
                print('Invalid email or password.')
                usrDbCheck.failed_login_attempts += 1
                db.session.commit()
                return redirect(url_for('auth.auth_login'))
            
            if usrDbCheck.failed_login_attempts >= 3:
                usrDbCheck.is_active = False
                db.session.commit()
                flash('Your account is locked due to failed login attempts.')
                print('Your account is locked due to failed login attempts.')
                return redirect(url_for('auth.auth_login'))

            # Validate the password
            if bcrypt.check_password_hash(usrDbCheck.password, password):
                usrDbCheck.failed_login_attempts = 0
                usrDbCheck.last_login = datetime.utcnow()
                db.session.commit()

                login_user(usrDbCheck, remember=rememberMe)

                # Handle first login logic
                if usrDbCheck.first_login:
                    usrDbCheck.first_login = False
                    db.session.commit()

                # Redirect based on role
                if usrDbCheck.role.role_name == 'admin':
                    return redirect(url_for('admin.admin_welcome' if usrDbCheck.first_login else 'admin.admin_home', username=usrDbCheck.username))
                elif usrDbCheck.role.role_name == 'user':
                    return redirect(url_for('user.user_welcome' if usrDbCheck.first_login else 'user.user_home', username=usrDbCheck.username))

                flash('You do not have a valid authority.', 'error')
                return redirect(url_for('auth.auth_login'))
            else:
                usrDbCheck.failed_login_attempts += 1
                db.session.commit()
                flash('Invalid email or password.', 'error')
                print('Invalid email or password.')
                return redirect(url_for('auth.auth_login'))

        flash('Invalid email or password.', 'error')
        print('Invalid email or password.')
        return redirect(url_for('auth.auth_login'))

    return render_template('auth-login.html', form=form)

@auth.route("/register/", methods=['GET', 'POST'])
def auth_register():
    form = RegisterForm()
    if form.validate_on_submit():
        usrnmFrUsr = form.username.data
        emailFrUsr = form.email.data
        password = form.password.data
        confirmPassword = form.confirmPassword.data
        print(f'Username: {usrnmFrUsr}')
        print(f'Email: {emailFrUsr}')

        if password != confirmPassword:
            flash('Passwords do not match.', 'warning')
            print('Passwords do not match.')
            return redirect(url_for('auth.auth_register'))
        
        if User.query.filter_by(email=emailFrUsr).first():
            flash('Email is already in use', 'warning')
            print('Email is already in use')
            return redirect(url_for('auth.auth_register'))
        
        if User.query.filter_by(username=usrnmFrUsr).first():
            flash('Username is already in use.', 'warning')
            print('Username is already in use.')
            return redirect(url_for('auth.auth_register'))
        
        userRole = Role.query.filter_by(role_name='user').first()
        if not userRole:
            flash('Default user role not found please contant Owow administrator.', 'error')
            print('Default user role not found please contant Owow administrator.')
            return redirect(url_for('auth.auth_register'))
        
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')

        createNewUsr = User(
            email=emailFrUsr,
            password=hashedPassword,
            username=usrnmFrUsr,
            role_id=userRole.role_id,
            is_active=True,
            password_last_changed=datetime.utcnow()
        )

        try:
            db.session.add(createNewUsr)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.auth_login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during the registration. Please try again.', 'error')
            print(f"Error: {e}")
            return redirect(url_for('auth.auth_register'))

    return render_template('auth-register.html', form=form)