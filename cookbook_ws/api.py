from flask import Blueprint, Response, jsonify, request, url_for
from werkzeug.utils import redirect

from cookbook_ws import db
from cookbook_ws.orm import Recipe, RecipeNote

api_page = Blueprint('api', __name__, url_prefix="/api")


@api_page.route('/')
@api_page.route('/recipe')
def api_default():
    response = Response(response="This is the REST API for interacting with the cookbook.\nSwagger pages soon.")
    response.mimetype = 'text/text'
    return response


@api_page.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """
    RECIPE API
    This endpoint retrieves JSON representation of a given recipe.
    ---
    tags:
      - API
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
        default: 1
    responses:
      200:
        description: A JSON encoded recipe object.
        schema:
          $ref: '#/definitions/Recipe'
        examples:
          {
              "create_date": "2017-09-24 15:29:42",
              "description": "This recipe shortens the cook time for the steel cut oats by letting them soak overnight.",
              "id": 1,
              "ingredients": [ ]
            }
    """
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    return jsonify(recipe.serialize)


@api_page.route('/recipe/<int:recipe_id>/notes', methods=['GET'])
def get_recipe_notes(recipe_id):
    """
    RECIPE API
    This endpoint retrieves JSON representation of all of the notes for a given recipe.
    ---
    tags:
      - API
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
        default: 1
    definitions:
      RecipeNotes:
        type: array
        items:
          $ref: '#/definitions/RecipeNote'
    responses:
      200:
        description: A JSON encoded recipe object.
        schema:
            $ref: '#/definitions/RecipeNotes'
        examples:
          [  {
                "create_date": "2017-09-24 15:29:42",
                "id": 2,
                "note_text": "This recipe is awesome!",
                "recipe_id": 2
              }
            ]
    """
    recipe_notes = RecipeNote.query.filter_by(recipe_id=recipe_id)
    return jsonify([note.serialize for note in recipe_notes])


@api_page.route('/recipe/<int:recipe_id>/notes', methods=['POST'])
def post_recipe_note(recipe_id):
    """
    RECIPE API
    This endpoint allows adding a note to a recipe.
    ---
    tags:
      - API
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
        default: 1
      - name: note_text
        in: body
        type: string
        required: true
        default: This is my note
    responses:
      200:
        description: A JSON encoded recipe note object.
        schema:
            $ref: '#/definitions/RecipeNote'
        examples:
          [  {
                "create_date": "2017-09-24 15:29:42",
                "id": 2,
                "note_text": "This recipe is awesome!",
                "recipe_id": 2
              }
            ]
    """

    print("Adding note...")

    text = request.get_data().decode('UTF-8')

    print("Adding note:{}".format(text))

    if text is not None:
        recipe = Recipe.query.filter_by(id=recipe_id).first()

        new_note = RecipeNote(note_text=text)
        recipe.notes.append(new_note)

        # db.session.update(recipe)
        db.session.commit()

    return redirect(url_for('api.get_recipe_note', recipe_id=recipe_id, note_id=new_note.id))


@api_page.route('/recipe/<int:recipe_id>/notes/<int:note_id>', methods=['GET'])
def get_recipe_note(recipe_id, note_id):
    """
    RECIPE API
    This endpoint retrieves JSON representation of a single note for a given recipe.
    ---
    tags:
      - API
    parameters:
      - name: recipe_id
        in: path
        type: integer
        required: true
        default: 1
      - name: note_id
        in: path
        type: integer
        required: true
        default: 1
    responses:
      200:
        description: A JSON encoded recipe object.
        schema:
          $ref: '#/definitions/RecipeNote'
        examples:
          {
                "create_date": "2017-09-24 15:29:42",
                "id": 2,
                "note_text": "This recipe is awesome!",
                "recipe_id": 2
          }
    """
    recipe_note = RecipeNote.query.filter_by(recipe_id=recipe_id).filter_by(id=note_id).first()

    if recipe_note is None:
        return Response(status=404)

    return jsonify(recipe_note.serialize)


@api_page.route('/recipe/<int:recipe_id>', methods=['PUT'])
def put_recipe(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    return jsonify(recipe.serialize)


@api_page.route('/recipe', methods=['POST'])
def post_recipe():

    print(request.json)
    text = request.get_data().decode('UTF-8')
    data = request.get_json()

    print("Adding recipe:{}".format(text))
    print(data)

    if text is not None:
        recipe = Recipe.deserialize(data)

        print(recipe.serialize)
        recipe = db.session.merge(recipe)
        db.session.commit()

        print(recipe.serialize)

    return redirect(url_for('api.get_recipe', recipe_id=recipe.id))

