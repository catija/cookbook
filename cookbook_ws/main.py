import datetime
import json

from flask import render_template, jsonify, request, url_for
from werkzeug.utils import redirect

from cookbook_ws import app, orm, db
from cookbook_ws.orm import RecipeType, Recipe, RecipeNote


@app.template_filter('datetime')
def _jinja2_filter_datetime(date):

    date = date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    format = '%b %d, %Y at %-I:%M %p'
    return date.strftime(format)


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


@app.route("/edit_recipe")
@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id=None):
    """
    This method returns a edit-recipe page.

    Args:
        recipe_id (int): Integer recipe identifier.
    """

    recipe_types = db.session.query(RecipeType)

    if recipe_id is not None:
        recipe = Recipe.query.filter_by(id=recipe_id).first()
    else:
        recipe = None

    return render_template("edit_recipe.html", recipe_types=recipe_types, recipe=recipe)


@app.route("/reset")
def reset_db():
    """
    This method initializes the database.

    This is very, VERY, temporary.
    """

    orm.initialize()

    return redirect(url_for('show_recipe', recipe_id=1))


@app.route('/new_note', methods=['GET', 'POST'])
def new_note():

    if request.method == 'POST':
        print(request)
        print(request.form)
        recipe_id = request.form['recipe_id']
        text = request.form['new-note']

        if text is not None:
            recipe = Recipe.query.filter_by(id=recipe_id).first()
            recipe.notes.append(RecipeNote(note_text=text))

            # db.session.update(recipe)
            db.session.commit()

        return redirect(url_for('show_recipe', recipe_id=recipe_id))

    if request.method == 'GET':
        return redirect(url_for('admin'))


@app.route("/export")
def export():
    """
    This method exports the contents of the database as a JSON file.
    """
    recipes = Recipe.query.order_by(Recipe.create_date)

    recipe_dicts = [r.serialize for r in recipes]

    response = jsonify(recipe_dicts)
    response.headers['Content-Disposition'] = 'attachment; filename=margin_recipes.json'
    response.mimetype = 'text/json'

    return response


def _import(recipes):

    db.drop_all()
    db.create_all()

    for recipe_dict in recipes:
        print("Adding Recipe: {}".format(recipe_dict))
        imported_recipe = Recipe.deserialize(recipe_dict)
        print("Adding Recipe: {}".format(imported_recipe))
        db.session.add(imported_recipe)

    print("Committing new recipes")
    db.session.commit()


@app.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        # if 'file' not in request.files:
        #     # flash('No file part')
        #     # return redirect(request.url)
        file = request.files['import_data']
        # # if user does not select file, browser also
        # # submit a empty part without filename
        # if file.filename == '':
        #     flash('No selected file')
        #     return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('uploaded_file',
        #                             filename=filename))

        if file:
            recipe_dicts = json.loads(file.read())
            print(recipe_dicts)
            jsonify(recipe_dicts)
            _import(recipe_dicts)
            # TODO: Add decode logic here and submit to database.

        return redirect(url_for('welcome'))
    if request.method == 'GET':
        return redirect(url_for('admin'))


@app.route("/admin")
def admin():
    """
    This method exports the contents of the database as a JSON file.
    """
    recipe_types = db.session.query(RecipeType)
    return render_template("admin.html", recipe_types=recipe_types)