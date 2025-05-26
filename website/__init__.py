from flask import Flask, g
from . import config
from flask_login import LoginManager
from .models import db, User
from .utils import create_admin_user, create_roles, bcrypt
from sqlalchemy.exc import OperationalError
import time
from pymongo import MongoClient

def create_owow():
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    bcrypt.init_app(app)  # Initialize bcrypt

    # Setup MongoDB client
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = mongo_client[app.config["MONGO_DB_NAME"]] # Default database

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.auth_login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Make MongoDB available via `g` object during requests
    @app.before_request
    def before_request():
        if not hasattr(g, 'mongo_db'):
            g.mongo_db = app.mongo_db

    from .auth import auth
    from .user import user
    from .admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    with app.app_context():
        for _ in range(10):
            try:
                print("Attempting to initialize the database...")
                db.create_all()
                create_roles()
                create_admin_user()
                print("Database initialization complete.")
                break
            except Exception as e:
                print(f"Database not ready. Retrying in 5 seconds... ({e})")
                time.sleep(5)
        else:
            print("Failed to initialize the database after 10 attempts.")

    return app