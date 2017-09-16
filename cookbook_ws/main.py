from flask import render_template, jsonify
from sqlalchemy import inspect

from cookbook_ws import app, orm, db
from cookbook_ws.orm import RecipeType, Recipe


@app.route("/")
def welcome():
    """
    Main entry point, this method returns the default page for the whole site.
    """
    recipe_types = db.session.query(RecipeType)
    recipes = Recipe.query.order_by(Recipe.create_date.desc()).limit(6)
    return render_template("index.html", recipe_types=recipe_types, recipes=recipes)


@app.route("/random")
def random_recipe():
    """
    This method returns a sample recipe page.

    TODO: Once we've got the backend implemented, we can change this method to serve a random recipe.
    """
    recipe_types = db.session.query(RecipeType)
    return render_template("recipe_page.html", recipe_types=recipe_types)


@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    """
    This method returns a recipe page.

    Args:
        recipe_id (int): Integer recipe identifier.
    """
    recipe_types = db.session.query(RecipeType)
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    return render_template("recipe.html", recipe_types=recipe_types, recipe=recipe)


@app.route("/reset")
def reset_db():
    """
    This method initializes the database.

    This is very, VERY, temporary.
    """

    orm.initialize()

    recipe_types = db.session.query(RecipeType)
    return render_template("recipe_page.html", recipe_types=recipe_types)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def todict(row):
    return row.s


@app.route("/export")
def export():
    """
    This method exports the contents of the database as a JSON file.
    """
    recipes = Recipe.query.order_by(Recipe.create_date)

    recipe_dicts = [r.serialize for r in recipes]
    return jsonify(recipe_dicts)


@app.route("/admin")
def admin():
    """
    This method exports the contents of the database as a JSON file.
    """
    recipe_types = db.session.query(RecipeType)
    return render_template("admin.html", recipe_types=recipe_types)