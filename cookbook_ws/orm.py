import datetime
import logging

from fractions import Fraction
from cookbook_ws import db


def convert_to_mixed_numeral(num):
    """Format a number as a mixed fraction.

    Examples:
        convert_to_mixed_numeral('-55/10') # '-5 1/2'
        convert_to_mixed_numeral(-55/10) # '-5 1/2'
        convert_to_mixed_numeral(-5.5) # '-5 1/2'

    Args:
        num (int|float|str): The number to format. It is coerced into a string.

    Returns:
        str: ``num`` formatted as a mixed fraction.

    """
    num = Fraction(str(num)) # use str(num) to prevent floating point inaccuracies
    n, d = (num.numerator, num.denominator)
    m, p = divmod(abs(n), d)
    if n < 0:
        m = -m
    return '{} {}/{}'.format(m, p, d) if m != 0 and p > 0 \
        else '{}'.format(m) if m != 0 \
        else '{}/{}'.format(n, d)


def _serialize(model_instance):
    """
    Common serialization method.  Serializes top-level elements into dictionary.
    Args:
        model_instance (db.Model): SQL Alchemy object instance
    """
    d = {}
    for column in model_instance.__table__.columns:
        if getattr(model_instance, column.name) is None:
            continue
        if isinstance(column.type, db.DateTime):
            d[column.name] = datetime.datetime.strftime(getattr(model_instance, column.name), "%b %d, %Y at %-I:%M %p")
        elif isinstance(column.type, db.Float):
            d[column.name] = float(getattr(model_instance, column.name))
        else:
            d[column.name] = getattr(model_instance, column.name)
    return d


def _deserialize(model_class, data_dict):
    """
    Common serialization method.  deserializes top-level elements from dictionary.
    Args:
        model_class (db.Model.cls): SQL Alchemy class constructor
        data_dict (dict): dictionary containing data for class
    """
    deser = model_class()

    for column in deser.__table__.columns:

        if column.name in data_dict:
            if isinstance(column.type, db.DateTime):
                setattr(deser, column.name,
                        datetime.datetime.strptime(data_dict[column.name], "%b %d, %Y at %-I:%M %p"))
            elif isinstance(column.type, db.Float):
                setattr(deser, column.name, float(data_dict[column.name]))
            else:
                setattr(deser, column.name, data_dict[column.name])

    return deser


class RecipeType(db.Model):
    __tablename__ = 'recipe_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))

    @property
    def serialize(self):
        return _serialize(self)

    @classmethod
    def deserialize(cls, recipe_dict):
        return _deserialize(cls, recipe_dict)


class Recipe(db.Model):
    __tablename__ = 'recipe'
    # Here we define db.Columns for the table recipe
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250))
    source = db.Column(db.String(250), nullable=True)
    source_url = db.Column(db.String(250), nullable=True)
    total_served = db.Column(db.Integer, nullable=True)
    recipe_type_id = db.Column(db.Integer, db.ForeignKey('recipe_type.id'), nullable=True)
    recipe_type = db.relationship("RecipeType")
    ingredients = db.relationship("RecipeIngredient", cascade="all, delete-orphan")
    steps = db.relationship("RecipeStep", cascade="all, delete-orphan")
    notes = db.relationship("RecipeNote", cascade="all, delete-orphan")
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        d = _serialize(self)

        d['recipe_type'] = self.recipe_type.serialize
        d['steps'] = [step.serialize for step in self.steps]
        d['ingredients'] = [ingredient.serialize for ingredient in self.ingredients]
        d['notes'] = [note.serialize for note in self.notes]

        return d

    @classmethod
    def deserialize(cls, recipe_dict):
        d_recipe = _deserialize(cls, recipe_dict)

        existing_recipe_type = db.session.query(RecipeType).filter(RecipeType.name == 'Stove Top').first()
        if existing_recipe_type is None:
            d_recipe.recipe_type = RecipeType.deserialize(recipe_dict['recipe_type'])
        else:
            d_recipe.recipe_type = existing_recipe_type

        if 'ingredients' in recipe_dict:
            d_recipe.ingredients = [RecipeIngredient.deserialize(i) for i in recipe_dict['ingredients']]

        if 'steps' in recipe_dict:
            d_recipe.steps = [RecipeStep.deserialize(i) for i in recipe_dict['steps']]

        if 'notes' in recipe_dict:
            d_recipe.notes = [RecipeNote.deserialize(i) for i in recipe_dict['notes']]

        return d_recipe


class RecipeIngredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    pre_measure = db.Column(db.String(250), nullable=True)
    post_measure = db.Column(db.String(250), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    amount_units_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=True)
    amount_units = db.relationship("IngredientUnit")
    divided = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "{} {} {}".format(self.amount, self.amount_units, self.name)

    @property
    def serialize(self):
        return _serialize(self)

    @classmethod
    def deserialize(cls, recipe_dict):
        return _deserialize(cls, recipe_dict)

    @property
    def amount_fract(self):
        """
        Converts float to fraction string
        Returns:
            str: fraction
        """
        return convert_to_mixed_numeral(self.amount)


class IngredientUnit(db.Model):
    __tablename__ = 'unit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    plural = db.Column(db.String(250), nullable=False)
    abbr = db.Column(db.String(10), nullable=True)
    pl_abbr = db.Column(db.String(10), nullable=True)

    @property
    def serialize(self):
        return _serialize(self)

    @classmethod
    def deserialize(cls, recipe_dict):
        return _deserialize(cls, recipe_dict)


class RecipeStep(db.Model):
    __tablename__ = "recipe_step"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)

    @property
    def serialize(self):
        return _serialize(self)

    @classmethod
    def deserialize(cls, recipe_dict):
        return _deserialize(cls, recipe_dict)


class RecipeNote(db.Model):
    __tablename__ = "recipe_note"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    note_text = db.Column(db.String(250), nullable=False)

    @property
    def serialize(self):
        return _serialize(self)

    @classmethod
    def deserialize(cls, recipe_dict):
        return _deserialize(cls, recipe_dict)


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

    cup_unit = IngredientUnit(name="cup", plural="cups", abbr="c")
    tsp_unit = IngredientUnit(name="teaspoon", plural="teaspoons", abbr="tsp")
    tbsp_unit = IngredientUnit(name="tablespoon", plural="tablespoons", abbr="tbsp")
    ounce_unit = IngredientUnit(name="ounce", plural="ounces", abbr="oz")
    pound_unit = IngredientUnit(name="pound", plural="pounds", abbr="lb")

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

    new_recipe.ingredients = [
        RecipeIngredient(name="oats", amount=1, amount_units=cup_unit),
        RecipeIngredient(name="water", amount=2, amount_units=cup_unit),
        RecipeIngredient(name="apple cider", amount=1, amount_units=cup_unit),
        RecipeIngredient(name="brown sugar", amount=1, amount_units=tbsp_unit),
        RecipeIngredient(name="cinnamon", amount=0.125, amount_units=tsp_unit),
        RecipeIngredient(name="salt", amount=0.25, amount_units=tsp_unit)
    ]

    new_recipe.recipe_type = new_recipe_type
    new_recipe.source = "Modified from America's Test Kitchen"
    new_recipe.source_url = "https://www.americastestkitchen.com/recipes/7021-apple-cinnamon-steel-cut-oatmeal"
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

    new_recipe.ingredients = [
        RecipeIngredient(name="unsalted butter", amount=4, amount_units=tbsp_unit,
                         post_measure="cut into 4 pieces"),
        RecipeIngredient(name="heavy cream", amount=3, amount_units=tbsp_unit, divided=True),
        RecipeIngredient(name="sugar", amount=1, amount_units=tsp_unit),
        RecipeIngredient(name="sweet potatoes (2 large or 3 medium)",
                         amount=2, amount_units=pound_unit,
                         post_measure="peeled, quartered lengthwise and cut into 1/4 inch slices"),
        RecipeIngredient(name="salt and pepper")
    ]

    new_recipe.notes = [
        RecipeNote(note_text=("It is imperative to cut the sweet potato into thin, "
                              "even slices to ensure perfect cooking."
                              "<ul><li>Quarter each peeled sweet potato lengthwise.</li>"
                              "<li>Cut each quarter into 1/2-inch slices crosswise.</li></ul>")),
        RecipeNote(note_text="This recipe is awesome!")
    ]

    new_recipe.recipe_type = new_recipe_type
    new_recipe.total_served = 4
    db.session.add(new_recipe)

    db.session.commit()

    new_recipe = Recipe(name='Cream Biscuits',
                        description=("Short of a box mix, the cream biscuit is by far the simplest biscuit formula"
                            " out there. Dry ingredients are whisked together and heavy cream is gently"
                            " stirred in. That's it. In fact, the biscuit dough will probably be ready"
                            " before your oven has fully preheated. But don't be fooled by the simplicity"
                            " of this recipe—it might not contain any butter, but heavy cream is full of"
                            " butterfat that makes the biscuits light and tender with a rich, milky flavor."))
    new_recipe.steps = [
                    RecipeStep(step_number=1,
                                   description="In a large bowl, whisk together flour, baking powder, salt, and sugar."),
                    RecipeStep(step_number=2,
                                   description=("Add heavy cream and stir gently with a wooden spoon until dry"
                            "ingredients are just moistened")),
                    RecipeStep(step_number=3,
                                    description=("Turn out dough onto a lighted floured work surface."
                            " Using your hands, fold it one or two times so it becomes a cohesive mass and press it"
                            " down to an even ½-inch thickness. Using a 2-inch round cookie-cutter, cut out biscuits"
                            " as closely together as possible. Gather together scraps, pat down, and cut out more"
                            " biscuits. Discard any remaining scraps.")),
                    RecipeStep(step_number=4,
                                    description=("Bake the biscuits in a 400°F oven until risen and"
                            " golden, about 12-15 minutes. Let cool slightly and serve warm. "))]

    new_recipe.ingredients = [RecipeIngredient(name="all purpose flour", amount=11, amount_units=ounce_unit),
                              RecipeIngredient(name="baking powder", amount=1.5, amount_units=tbsp_unit),
                              RecipeIngredient(name="kosher salt", amount=1, amount_units=tsp_unit),
                              RecipeIngredient(name="sugar", amount=1, amount_units=tbsp_unit),
                              RecipeIngredient(name="heavy whipping cream", amount=1.5, amount_units=cup_unit)]
    new_recipe.recipe_type = new_recipe_type
    new_recipe.source = "from Serious Eats"
    new_recipe.source_url = "http://www.seriouseats.com/recipes/2014/06/light-tender-cream-biscuits-recipe.html"
    new_recipe.total_served = 4

    db.session.add(new_recipe)

    db.session.commit()

