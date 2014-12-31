
# Flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required

app = Flask(__name__)

# Load config file
app.config.from_object('config')

# Connect to MySQL with the defaults
db = SQLAlchemy(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# Login App
from login import views, models

# app.run(debug=True)

# if not app.debug:
#     import logging
#     from logging.handlers import RotatingFileHandler

#     file_handler = RotatingFileHandler('errorlog.log', 'a', 1 * 1024 * 1024, 10)
#     file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    
#     app.logger.setLevel(logging.INFO)
#     file_handler.setLevel(logging.INFO)
    
#     app.logger.addHandler(file_handler)
#     app.logger.info('Error Log')