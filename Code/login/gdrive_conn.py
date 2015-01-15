# Connect Google Drive

# Python
import json

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

# App
from login import app
from login import login_manager 

# DB
from models import get_gdrive_token, set_gdrive_token
from login import db

# Google Drive API

GDRIVE_CLIENT_SECRET = app.config['GDRIVE_CLIENT_SECRET']
GDRIVE_CLIENT_ID = app.config['GDRIVE_CLIENT_ID']

# Create JSON element from dict CLIENT_SECRET
CLIENT_SECRET = json.dumps(app.config['CLIENT_SECRET'])


endpoint_url = 'https://accounts.google.com/o/oauth2/auth'

# Full, permissive scope to access all of a user's files
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'


def get_gdrive_access_token():
	email = session.get('user')
	print "inside get_gdrive_access_token() \nemail = ", email
	if email is None:
		return None

def gdrive_connect():
	access_token = get_gdrive_access_token




@app.route('gdrive-auth-finish')
def gdrive_auth_finish():


@app.route('/gdrive-auth-start')
def gdrive_auth_start():


@app.route('gdrive-disconnect')
def gdrive_disconnect():
