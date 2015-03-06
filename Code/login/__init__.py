# Python
import os

# Flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

# CORS - Cross-Origin Resource Sharing
from flask.ext.cors import CORS, cross_origin

app = Flask(__name__, static_url_path='/static')

# Load config file
app.config.from_object('config')

# app.config['CORS_HEADERS'] = 'Content-Type'


# Connect to MySQL with the defaults
db = SQLAlchemy(app)

# Flask-CORS
# cors = CORS(app)#, resources={r"/*": {"origins": "*"}})

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Login App
from login import views, models

views.routes(app, login_manager)

# Create directory to store public keys
# if not os.path.exists('pb_keys'):
#	os.makedirs('pb_keys')

# @app.after_request
# def after_request(response):
# 	# response.setHeader("Access-Control-Allow-Headers", req.getHeader("Access-Control-Request-Headers")); 
# 	response.headers.add('Access-Control-Allow-Origin','*')
# 	return response