from flask import Flask
from . import config
from flask_login import LoginManager
from .models import db, User
from .utils import create_admin_user, create_roles, bcrypt
from sqlalchemy.exc import OperationalError
import time

def create_owow():
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    bcrypt.init_app(app)  # Initialize bcrypt

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.auth_login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    from .auth import auth
    from .user import user
    from .admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    with app.app_context():
        for _ in range(10):
            try:
                app.logger.info("Attempting to initialize the database...")
                db.create_all()
                create_roles()
                create_admin_user()
                app.logger.info("Database initialization complete.")
                break
            except Exception as e:
                app.logger.warning(f"Database not ready. Retrying in 5 seconds... ({e})")
                time.sleep(5)
        else:
            app.logger.error("Failed to initialize the database after 10 attempts.")

    return app