from flask import Flask

app = Flask(__name__)

# There's currently nothing necessary in this config file, but I expect we'll need it in the future.
app.config.from_pyfile('../main.ini')

import cookbook_ws.main

