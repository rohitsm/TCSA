# Connect Google Drive

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

# App
from login import app
from login import login_manager 

# DB
from models import get_dropbox_token, set_dropbox_token
from login import db

# Google Drive API

GDRIVE_CLIENT_SECRET = app.config['GDRIVE_CLIENT_SECRET']
GDRIVE_CLIENT_ID = app.config['GDRIVE_CLIENT_ID']

endpoint_url = 'https://accounts.google.com/o/oauth2/auth'