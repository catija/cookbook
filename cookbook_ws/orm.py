import datetime
import logging

from fractions import Fraction
from cookbook_ws import db


class RecipeType(db.Model):
    __tablename__ = 'recipe_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))

    @property
    def serialize(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


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

    @property
    def serialize(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))

        d['recipe_type'] = self.recipe_type.serialize
        d['steps'] = [step.serialize for step in self.steps]
        d['ingredients'] = [ingredient.serialize for ingredient in self.ingredients]
        return d


class RecipeIngredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    amount = db.Column(db.Float, nullable=True)
    amount_units = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return "{} {} {}".format(self.amount, self.amount_units, self.name)

    @property
    def serialize(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d

    @property
    def amount_fract(self):
        """
        Converts float to fraction string
        Returns:
            str: fraction
        """
        return str(Fraction(self.amount))


class RecipeStep(db.Model):
    __tablename__ = "recipe_step"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)

    @property
    def serialize(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d

def initialize():

    logger = logging.getLogger()
    logger.critical("Creating new database!")

    db.drop_all()

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

    new_recipe.ingredients = [RecipeIngredient(name="oats", amount=1, amount_units="cup"),
                              RecipeIngredient(name="water", amount=2, amount_units="cup"),
                              RecipeIngredient(name="apple cider", amount=1, amount_units="cup"),
                              RecipeIngredient(name="brown sugar", amount=1, amount_units="tablespoon"),
                              RecipeIngredient(name="cinnamon", amount=0.125, amount_units="teaspoon"),
                              RecipeIngredient(name="salt", amount=0.25, amount_units="teaspoon")]
    new_recipe.recipe_type = new_recipe_type
    new_recipe.source = "Modified from Cooks Country"
    new_recipe.total_served = 4

    db.session.add(new_recipe)

    db.session.commit()

    new_recipe = Recipe(name='Creamy Mashed Sweet Potatoes',
                        description="Easy mashed sweet potato recipe.",
                        source="COOK'S COUNTRY DECEMBER/JANUARY 2007")

    new_recipe.steps = [
                    RecipeStep(step_number=1,
                               description=("Combine butter, 2 tablespoons cream, 1/2 teaspoon salt, "
                                            "1/4 teaspoon pepper, sugar, and sweet potatoes in a large saucepan.")),
                    RecipeStep(step_number=2,
                               description=("Cook, covered, over low heat until potatoes are fall-apart tender, " ""
                                            "35 to 40 minutes.")),
                    RecipeStep(step_number=3,
                               description=("Turn off heat, add remaining tablespoon cream and "
                                            "mash sweet potatoes with potato masher.")),
                    RecipeStep(step_number=4,
                               description="Serve.")]

    new_recipe.ingredients = [RecipeIngredient(name="unsalted butter, cut into 4 pieces", amount=12, amount_units="tablespoons"),
                              RecipeIngredient(name="heavy cream", amount=3, amount_units="tablespoons"),
                              RecipeIngredient(name="sugar", amount=1, amount_units="teaspoon"),
                              RecipeIngredient(name=("sweet potatoes (2 large or 3 medium) "
                                                     "peeled, quartered lengthwise and cut into 1/4 inch slices"),
                                               amount=2, amount_units="pounds"),
                              RecipeIngredient(name="salt and pepper")]

    new_recipe.recipe_type = new_recipe_type
    new_recipe.total_served = 4
    db.session.add(new_recipe)

    db.session.commit()
