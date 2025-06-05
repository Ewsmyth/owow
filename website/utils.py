from flask import current_app
from . import config
from flask_bcrypt import Bcrypt
from .models import db, User, Role
import html
import re

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
    existing = User.query.filter_by(username="admin").first()
    if existing:
        print("Admin user already exists.")
        return
    try:
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            current_app.logger.error("Admin role not found when trying to create admin user.")
            print("Admin role not found when trying to create admin user.")
            return

        current_app.logger.info("Creating default admin user...")
        print("Creating default admin user...")

        password_hash = bcrypt.generate_password_hash(
            config.ADMIN_PASSWORD or 'admin'
        ).decode('utf-8')

        create_admin = User(
            username='admin',
            email='admin@localhost',
            role_id=admin_role.role_id,
            password=password_hash,
            is_active=True,
            first_login=True
        )
        db.session.add(create_admin)
        db.session.commit()
        current_app.logger.info("Admin user has been created.")
        print("Admin user has been created.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating admin user: {e}")
        print(f"Error creating admin user: {e}")

def create_pre_built_cuisine():
    cuisine_list = [
        "American", "Chinese", "Mexican", "Italian", "Japanese", "Thai", "Indian", "French",
        "Greek", "Korean", "Spanish", "Vietnamese", "Turkish", "Moroccan", "Ethiopian", "Caribbean",
        "Brazilian", "Lebanese", "German", "Russian", "Persian", "Cuban", "Filipino", "Indonesian"
    ]

    try:
        mongo_db = current_app.mongo_db
        cuisines_col = mongo_db["cuisines"]

        for cuisine in cuisine_list:
            # Check if it already exists (case-insensitive match)
            if not cuisines_col.find_one({"name": {"$regex": f"^{cuisine}$", "$options": "i"}}):
                cuisines_col.insert_one({"name": cuisine})
                current_app.logger.info(f"Inserted cuisine: {cuisine}")
                print(f"Inserted cuisine: {cuisine}")
            else:
                print(f"Cuisine already exists: {cuisine}")

    except Exception as e:
        current_app.logger.error(f"Error inserting pre-built cuisines: {e}")
        print(f"Error inserting pre-built cuisines: {e}")


def create_pre_built_ingredients():

    ingredient_list = [
        "salt", "sugar", "flour", "butter", "milk", "eggs", "olive oil", "garlic", "onion",
        "chicken", "beef", "pork", "tomatoes", "carrots", "potatoes", "pepper", "rice",
        "cheese", "basil", "cilantro", "parsley", "lemon", "lime", "vinegar", "soy sauce",
        "ginger", "chili powder", "cumin", "cinnamon", "nutmeg", "oregano", "thyme", "bay leaf"
    ]

    try:
        mongo_db = current_app.mongo_db
        ingredients_col = mongo_db["ingredients"]

        for item in ingredient_list:
            # Avoid duplicates (case-insensitive match)
            if not ingredients_col.find_one({"name": {"$regex": f"^{item}$", "$options": "i"}}):
                ingredients_col.insert_one({"name": item})
                print(f"Inserted ingredient: {item}")
            else:
                print(f"Ingredient already exists: {item}")
    except Exception as e:
        current_app.logger.error(f"Error inserting pre-built ingredients: {e}")
        print(f"Error inserting pre-built ingredients: {e}")

def sanitize_text(text, max_length=100):
    if not text:
        return ""
    return html.escape(text.strip())[:max_length]

def validate_time_format(time_str):
    return bool(re.match(r"^\d{1,2}:\d{2}$", time_str))

# Convert HH:MM string to total minutes
def convert_to_minutes(time_str):
    try:
        hours, minutes = map(int, time_str.strip().split(":"))
        return hours * 60 + minutes
    except (ValueError, AttributeError):
        return 0