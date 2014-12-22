
# Flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

# Connect to MySQL with the defaults
db = SQLAlchemy(app)

# Login App
from login import views, models

app.run(debug = True)

