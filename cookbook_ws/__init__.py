from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('../main.ini')
db = SQLAlchemy(app)

# There's currently nothing necessary in this config file, but I expect we'll need it in the future.

import cookbook_ws.main

