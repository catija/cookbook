from flask import render_template

from cookbook_ws import app


@app.route("/")
def welcome():
    """
    Main entry point, this method returns the default page for the whole site.
    """
    return render_template("index.html")


@app.route("/random")
def random_recipe():
    """
    This method returns a sample recipe page.

    TODO: Once we've got the backend implemented, we can change this method to serve a random recipe.
    """
    return render_template("recipe_page.html")