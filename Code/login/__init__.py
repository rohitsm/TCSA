# Python
import os

# Flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__, static_url_path='/static')

# Load config file
app.config.from_object('config')

# Connect to MySQL with the defaults
db = SQLAlchemy(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Login App
from login import views, models

views.routes(app, login_manager)