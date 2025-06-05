from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, g
from .decorators import role_required
from flask_login import current_user, login_required
from datetime import datetime
from .forms.user_forms import DummyRecipeForm
from bson.objectid import ObjectId
from .utils import sanitize_text, validate_time_format, convert_to_minutes
from re import escape

user = Blueprint('user', __name__)

@user.route('/<username>/user-home/')
@login_required
@role_required('user')
def user_home(username):
    if username != current_user.username:
        flash('Unauthorized access to another user\'s account', 'error')
        return redirect(url_for('auth.auth_login'))
    return render_template('user-home.html', username=username)

@user.route('/<username>/user-home/shopping-list/')
@login_required
@role_required('user')
def user_shopping_list(username):
    return render_template('user-shopping-list.html', username=username)

@user.route('/<username>/user-home/recipes/')
@login_required
@role_required('user')
def user_recipes(username):
    if username != current_user.username:
        flash('Unauthorized access', 'error')
        return redirect(url_for('auth.auth_login'))
    
    user_id = current_user.user_id
    recipes = list(g.mongo_db.recipes.find({"saved_by": user_id}))

    return render_template('user-recipes.html', username=username, recipes=recipes)

@user.route('/<username>/user-home/recipes/add-recipe/')
@login_required
@role_required('user')
def user_add_recipe(username):
    form = DummyRecipeForm()

    cuisines = sorted([c["name"] for c in g.mongo_db.cuisines.find({}, {"name": 1})])

    ingredients = sorted([
        doc["name"] for doc in g.mongo_db.ingredients.find({}, {"name": 1})
    ])

    return render_template('user-add-recipe.html', form=form, username=username, cuisines=cuisines, ingredients=ingredients)

@user.route('/<username>/user-home/profile/')
@login_required
@role_required('user')
def user_profile(username):
    return render_template('user-profile.html', username=username)

@user.route('/<username>/user-home/recipes/add-recipe/create/', methods=['GET', 'POST'])
@login_required  # Ensures user must be logged in to access this route
@role_required('user')  # Ensures only users with the 'user' role can access
def user_create_recipe(username):
    # Prevents a user from creating recipes under another username
    if username != current_user.username:
        flash('Unauthorized access', 'error')
        return redirect(url_for('auth.auth_login'))

    # Dummy form placeholder for CSRF protection and validation scaffold
    form = DummyRecipeForm()

    # Only proceed if the form submission is valid
    if form.validate_on_submit():
        # Get form values
        dish_name = sanitize_text(request.form.get('dish_name'), 100)

        ingredients = []  # Will be populated with structured ingredient data

        # Lists of ingredients and their corresponding amounts and units
        names = request.form.getlist('ingredient[]')
        amounts = request.form.getlist('amount[]')
        units = request.form.getlist('unit[]')

        # Recipe instructions and meal type
        instructions = request.form.get('instructions', '').strip()
        meal = request.form.get('meal-selection')

        # Get prep and cook time in HH:MM format
        prep_time_raw = request.form.get('prep_time')
        cook_time_raw = request.form.get('cook_time')

        if not validate_time_format(prep_time_raw):
            flash("Invalid prep time format. Use HH:MM.", "error")
            return redirect(url_for('user.user_add_recipe', username=username))

        if not validate_time_format(cook_time_raw):
            flash("Invalid cook time format. Use HH:MM.", "error")
            return redirect(url_for('user.user_add_recipe', username=username))


        prep_time_minutes = convert_to_minutes(prep_time_raw)
        cook_time_minutes = convert_to_minutes(cook_time_raw)

        # Handle cuisine logic — either selected or a custom value
        selected_cuisine = request.form.get('cuisine')
        custom_cuisine = sanitize_text(request.form.get('custom_cuisine', ''), 50)
        cuisine = custom_cuisine if selected_cuisine == 'other' and custom_cuisine else selected_cuisine

        # Add new cuisine to DB if it doesn’t already exist
        if selected_cuisine == 'other' and custom_cuisine:
            escaped_cuisine = escape(custom_cuisine)
            existing = g.mongo_db.cuisines.find_one({
                "name": {"$regex": f"^{escaped_cuisine}$", "$options": "i"}
            })
            if not existing:
                try:
                    g.mongo_db.cuisines.insert_one({"name": custom_cuisine.title()})
                    print(f"Added new cuisine to DB: {custom_cuisine.title()}")  # Debug log
                except Exception as e:
                    flash('Faile to save cuisine to the database.', 'error')
                    print(f"Cuisine Insert Error: {e}")

        
        if not (len(names) == len(amounts) == len(units)):
            flash("Ingredient list is incomplete or mismatched.", "error")
            return redirect(url_for('user.user_add_recipe', username=username))

        # Loop over each ingredient and ensure it exists in DB
        for name, amount, unit in zip(names, amounts, units):
            name_clean = sanitize_text(name.lower(), 100)

            escaped_name = escape(name_clean)
            existing = g.mongo_db.ingredients.find_one({
                "name": {"$regex": f"^{escaped_name}$", "$options": "i"}
            })

            if not existing:
                try:
                    g.mongo_db.ingredients.insert_one({"name": name_clean.title()})
                    print(f"Added new ingredient: {name_clean.title()}")
                except Exception as e:
                    flash('Failed to save ingredient to the database.', 'error')
                    print(f"Ingredient Insert Error: {e}")


            ingredients.append({
                "ingredient": name,
                "amount": amount,
                "unit": unit
            })

        # Final recipe document to insert
        recipe = {
            "owner": username,
            "dish_name": dish_name,
            "cuisine": cuisine,
            "meal": meal,
            "prep_time": prep_time_minutes,
            "cook_time": cook_time_minutes,
            "instructions": instructions,
            "ingredients": ingredients,
            "saved_by": [current_user.user_id],
            "created_at": datetime.utcnow()
        }

        # Insert recipe into MongoDB
        try:
            g.mongo_db.recipes.insert_one(recipe)
        except Exception as e:
            flash("An error occurred while saving your recipe.", "error")
            print(f"DB Insert Error: {e}")
            return redirect(url_for('user.user_recipes', username=username))

    # Render the recipe creation form on GET or invalid POST
    return redirect(url_for('user.user_recipes', username=username))

@user.route('/<username>/user-home/recipes/view/<recipe_id>/')
@login_required
@role_required('user')
def user_view_recipe(username, recipe_id):
    if username != current_user.username:
        flash('Unauthorized access', 'error')
        return redirect(url_for('auth.auth_login'))

    try:
        recipe = g.mongo_db.recipes.find_one({"_id": ObjectId(recipe_id), "saved_by": current_user.user_id})
        if not recipe:
            flash("Recipe not found or access denied.", "error")
            return redirect(url_for('user.user_recipes', username=username))
    except Exception as e:
        flash("Invalid recipe ID.", "error")
        return redirect(url_for('user.user_recipes', username=username))

    return render_template(
        'user-view-recipe.html', 
        username=username, 
        recipe=recipe,
        back_url=url_for('user.user_recipes', username=username)
    )