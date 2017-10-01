import yaml
from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# This config file contains the database connection information.
# (also some extra, yet unused stuff)
app.config.from_pyfile('../main.ini')
db = SQLAlchemy(app)

template = {
  "swagger": "2.0",
  "info": {
    "title": "Recipe API",
    "description": "API for accessing Cooking from the Margins",
    # "contact": {
    #   "responsibleOrganization": "ME",
    #   "responsibleDeveloper": "Me",
    #   "email": "me@me.com",
    #   "url": "www.me.com",
    # },
    "termsOfService": "http://me.com/terms",
    "version": "0.0.1"
  },
  # "host": "mysite.com",  # overrides localhost:500
  "basePath": "/",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
  "operationId": "getmyData"
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "definitions": yaml.load(open('cookbook_ws/static/definitions.yaml', 'r'))
}

# print(yaml.load(open('cookbook_ws/static/definitions.yaml', 'r')))

swagger = Swagger(app, template=template, config=swagger_config)

# print(swagger.config['definitions'])

from cookbook_ws.api import api_page

app.register_blueprint(api_page)

import cookbook_ws.main

