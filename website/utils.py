from flask import current_app
from . import config
from flask_bcrypt import Bcrypt
from .models import db, User, Role

bcrypt = Bcrypt()

def create_roles():
    """Creates default roles in the Role table if they do not exist."""
    try:
        # Check if roles already exist, creating them if necessary
        admin_role = Role.query.filter_by(role_name='admin').first()
        user_role = Role.query.filter_by(role_name='user').first()

        if not admin_role:
            admin_role = Role(role_name='admin', description='System Administrator role with complete system management.')
            db.session.add(admin_role)
            current_app.logger.info("Admin role created.")
            print("Admin role created.")

        if not user_role:
            user_role = Role(role_name='user', description='Standard user role allowing access to system.')
            db.session.add(user_role)
            current_app.logger.info("User role created.")
            print("User role created.")

        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error creating roles: {e}")
        print(f"Error creating roles: {e}")

def create_admin_user():
    """Creates a user with an admin role if one does not exist."""
    try:
        # Fetch the admin role
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            current_app.logger.error("Admin role not found when trying to create admin user.")
            print("Admin role not found when trying to create admin user.")
            return

        # Check if a user with the admin role already exists
        search_for_admin = User.query.filter_by(role_id=admin_role.role_id).first()
        if not search_for_admin:
            current_app.logger.info("No admin user found. Creating default admin user...")
            print("No admin user found. Creating default admin user...")
            password_hash = bcrypt.generate_password_hash(
                config.ADMIN_PASSWORD or 'admin'
            ).decode('utf-8')

            create_admin = User(
                username='admin',
                role_id=admin_role.role_id,  # Assign the fetched admin role ID
                password=password_hash
            )
            db.session.add(create_admin)
            db.session.commit()
            current_app.logger.info("Admin user has been created.")
            print("Admin user has been created.")
    except Exception as e:
        current_app.logger.error(f"Error creating admin user: {e}")
        print(f"Error creating admin user: {e}")