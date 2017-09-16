
from cookbook_ws import db

class RecipeType(db.Model):
    __tablename__ = 'recipe_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))


class Recipe(db.Model):
    __tablename__ = 'recipe'
    # Here we define db.Columns for the table recipe
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250))
    recipe_type_id = db.Column(db.Integer, db.ForeignKey('recipe_type.id'), nullable=True)
    recipe_type = db.relationship("RecipeType")
    ingredients = db.relationship("RecipeIngredient")
    steps = db.relationship("RecipeStep")


class RecipeIngredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    amount_units = db.Column(db.String(250), nullable=False)


class RecipeStep(db.Model):
    __tablename__ = "recipe_step"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)


def initialize():

    # Create all the tables based on the model defined above.
    db.create_all()

    # Insert a Recipe in the person table
    db.session.add(RecipeType(name="Stove Top"))
    db.session.add(RecipeType(name="Baking"))
    db.session.add(RecipeType(name="Broiling"))
    db.session.commit()

    new_recipe_type = db.session.query(RecipeType).filter(RecipeType.name == 'Stove Top')[0]

    # Insert a Recipe in the person table
    new_recipe = Recipe(name='Steel Cut Oats', description="Delicious")
    new_recipe.steps = [RecipeStep(step_number=1, description="Do Stuff"),
                        RecipeStep(step_number=1, description="Do More Stuff")]
    new_recipe.ingredients = [RecipeIngredient(name="Oats", amount=1, amount_units="Cups"),
                              RecipeIngredient(name="Salt", amount=1, amount_units="Cups")]
    new_recipe.recipe_type = new_recipe_type

    db.session.add(new_recipe)
    db.session.commit()