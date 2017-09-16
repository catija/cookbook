import datetime
import logging

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
    source = db.Column(db.String(250), nullable=True)
    total_served = db.Column(db.Integer, nullable=True)
    recipe_type_id = db.Column(db.Integer, db.ForeignKey('recipe_type.id'), nullable=True)
    recipe_type = db.relationship("RecipeType")
    ingredients = db.relationship("RecipeIngredient")
    steps = db.relationship("RecipeStep")
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class RecipeIngredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    amount_units = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return "{} {} {}".format(self.amount, self.amount_units, self.name)


class RecipeStep(db.Model):
    __tablename__ = "recipe_step"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)


def initialize():

    logger = logging.getLogger()
    logger.critical("Creating new database!")

    # Create all the tables based on the model defined above.
    db.create_all()

    # Insert a Recipe in the person table
    db.session.add(RecipeType(name="Stove Top"))
    db.session.add(RecipeType(name="Baking"))
    db.session.add(RecipeType(name="Broiling"))
    db.session.commit()

    new_recipe_type = db.session.query(RecipeType).filter(RecipeType.name == 'Stove Top')[0]

    # Insert a Recipe in the person table
    new_recipe = Recipe(name='Overnight Apple-Cinnamon Steel Cut Oats',
                        description=("This recipe shortens the cook time for the steel cut oats by letting them soak"
                                     " overnight."))
    new_recipe.steps = [RecipeStep(step_number=1, description="Bring water to boil."),
                        RecipeStep(step_number=2,
                                   description=("Add steel cut oats and salt.  Stir, cover, and remove from heat."
                                                "Let sit overnight.")),
                        RecipeStep(step_number=3, description="Add apple cider, brown sugar, and cinnamon."),
                        RecipeStep(step_number=4, description="Add high heat and bring to boil."),
                        RecipeStep(step_number=5,
                                   description="Reduce heat to simmer for 3 minutes until oatmeal thickens."),
                        RecipeStep(step_number=6,
                                   description="Serve.")]

    new_recipe.ingredients = [RecipeIngredient(name="Oats", amount=1, amount_units="Cup"),
                              RecipeIngredient(name="Water", amount=2, amount_units="Cup"),
                              RecipeIngredient(name="Apple Cider", amount=1, amount_units="Cup"),
                              RecipeIngredient(name="Brown Sugar", amount=1, amount_units="Tablespoon"),
                              RecipeIngredient(name="Cinnamon", amount=0.125, amount_units="Teaspoon"),
                              RecipeIngredient(name="Salt", amount=0.25, amount_units="Teaspoon")]
    new_recipe.recipe_type = new_recipe_type
    new_recipe.source = "Modified from Cooks Country"
    new_recipe.total_served = 4

    db.session.add(new_recipe)
    db.session.commit()