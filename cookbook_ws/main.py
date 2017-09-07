from flask import render_template

from cookbook_ws import app


@app.route("/")
def welcome():
    return render_template("index.html")


@app.route("/random")
def random_recipe():
    return render_template("recipe_page.html")