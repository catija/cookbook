

from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


# class Person(Base):
#     __tablename__ = 'person'
#     # Here we define columns for the table person
#     # Notice that each column is also a normal Python instance attribute.
#     id = Column(Integer, primary_key=True)
#     name = Column(String(250), nullable=False)
#
#
# class Address(Base):
#     __tablename__ = 'address'
#     # Here we define columns for the table address.
#     # Notice that each column is also a normal Python instance attribute.
#     id = Column(Integer, primary_key=True)
#     street_name = Column(String(250))
#     street_number = Column(String(250))
#     post_code = Column(String(250), nullable=False)
#     person_id = Column(Integer, ForeignKey('person.id'))
#     person = relationship(Person)


class RecipeType(Base):
    __tablename__ = 'recipe_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))


class Recipe(Base):
    __tablename__ = 'recipe'
    # Here we define columns for the table recipe
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    recipe_type_id = Column(Integer, ForeignKey('recipe_type.id'), nullable=True)
    recipe_type = relationship("RecipeType")
    ingredients = relationship("RecipeIngredient")
    steps = relationship("RecipeStep")


class RecipeIngredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipe.id'), nullable=False)
    amount = Column(Float, nullable=False)
    amount_units = Column(String(250), nullable=False)


class RecipeStep(Base):
    __tablename__ = "recipe_step"
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'), nullable=False)
    step_number = Column(Integer, nullable=False)
    description = Column(String(250), nullable=False)


def initialize():
    engine = create_engine('sqlite:///sqlalchemy_example.db')
    Base.metadata.create_all(engine)

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()

    session.add(RecipeType(name="Stove Top"))
    session.add(RecipeType(name="Baking"))
    session.add(RecipeType(name="Broiling"))
    session.commit()

    new_recipe_type = session.query(RecipeType).filter(RecipeType.name=='Stove Top')[0]

    # Insert a Person in the person table
    new_recipe = Recipe(name='Steel Cut Oats', description="Delicious")
    new_recipe.steps = [RecipeStep(step_number=1, description="Do Stuff"),
                        RecipeStep(step_number=1, description="Do More Stuff")]
    new_recipe.ingredients = [RecipeIngredient(name="Oats", amount=1, amount_units="Cups"),
                              RecipeIngredient(name="Salt", amount=1, amount_units="Cups")]
    new_recipe.recipe_type = new_recipe_type

    session.add(new_recipe)
    session.commit()

    # Insert an Address in the address table
    #new_address = Address(post_code='00000', person=new_person)
    #session.add(new_address)
    #session.commit()


def _get_session():

    engine = create_engine('sqlite:///sqlalchemy_example.db')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    return session


def get_recipe_types():
    session = _get_session()

    return session.query(RecipeType)