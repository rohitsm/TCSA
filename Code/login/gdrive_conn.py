# Connect Google Drive
# Reference: https://developers.google.com/api-client-library/python/auth/web-app

# Python
import json
import httplib2

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
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from apiclient.discovery import build

GDRIVE_CLIENT_SECRET = app.config['GDRIVE_CLIENT_SECRET']
GDRIVE_CLIENT_ID = app.config['GDRIVE_CLIENT_ID']

# Full, permissive scope to access all of a user's files
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Create JSON element from dict CLIENT_SECRET
# CLIENT_SECRET = json.dumps(app.config['CLIENT_SECRET'])

def get_gdrive_refresh_token():
	email = session.get('user')
	print "inside get_gdrive_access_token() \nemail = ", email
	if email is None:
		return None

	# Get the refresh token from the DB
	refresh_token = get_gdrive_token(email)
	print "refresh_token form db = ", refresh_token
	if refresh_token:
		return refresh_token

	print "Error no record of refresh_token found in DB. Not connected to Google Drive"
	return None


def gdrive_connect():
	# Make request for new access_token using the refresh token
	refresh_token = get_gdrive_refresh_token()
	print "refresh_token = ", refresh_token
	if refresh_token is None:
		print "refresh_token = none"
		return None
	# Build the JSON variable for credentials
	# cred = {}
	# cred['client_id'] = GDRIVE_CLIENT_ID
	# cred['client_secret'] = GDRIVE_CLIENT_SECRET
	# cred['refresh_token'] = refresh_token
	# cred['grant_type'] = "refresh_token"

	credentials = OAuth2Credentials.from_json(refresh_token)
	if credentials.access_token_expired:
		print "credentials.access_token_expired"
		return None
	else:
		# Returns user information as a JSON object
		user_info_service = build(
			serviceName = 'drive', version = 'v2',
			http = credentials.authorize(httplib2.Http()) )
		print "user_info_service = ", user_info_service
		user_info = user_info_service.files().list().execute()
		print "\n\n\n\nuser_info = ", json.dumps(user_info, indent=4, sort_keys=True)
		return json.dumps(user_info)
		
@app.route('/gdrive-auth-finish')
def gdrive_auth_finish():
	email = session.get('user')
	print "inside gdrive-auth-finish. \nEmail = ", email
	if email is None:
		abort(403)
	flow = get_auth_flow_object()
	if 'code' not in request.args:
		auth_uri = flow.step1_get_authorize_url()
		return redirect(auth_uri)
	else:
		auth_code = request.args.get('code')
		credentials = flow.step2_exchange(auth_code)
		print "credentials = ", credentials.to_json()
		# session['credentials'] = credentials.to_json()
		refresh_token = credentials.refresh_token

		if set_gdrive_token(email, credentials.to_json()):
			print "refresh_token added to DB"
			return redirect(url_for('profile'))

		flash('Error in adding Gdrive token to DB')
		print "Error, Could not add refresh_token to DB"
		return redirect(url_for('profile'))


@app.route('/gdrive-auth-start')
def gdrive_auth_start():
	# Checking for appropriate user session
	if 'user' not in session:
		abort(403)
	email = session.get('user')
	print "inside gdrive_auth_start. \nUser in session"
	print "email = ", email
	if email is None:
		abort(403)

	return redirect(url_for('gdrive_auth_finish'))

def get_auth_flow_object():
	REDIRECT_URI = url_for('gdrive_auth_finish', _external=True)
	flow = OAuth2WebServerFlow(client_id=GDRIVE_CLIENT_ID,
                           client_secret=GDRIVE_CLIENT_SECRET,
                           scope=OAUTH_SCOPE,
                           redirect_uri=REDIRECT_URI)
	flow.params['access_type'] = 'offline'
	flow.params['approval_prompt'] = 'force'
	flow.params['include_granted_scopes'] = 'true'
	return flow

@app.route('/gdrive-disconnect')
def gdrive_disconnect():
	# Disconnect Google Drive refresh_token from DB records
	print "inside gdrive-disconnect"
	email = session.get('user')
	if email is None:
		abort(403)
	print "Disconnecting Google Drive for email: ", email
	if set_gdrive_token(email, None):
		print "Disconnected Google Drive. removed from DB"
		return redirect(url_for('profile'))

	flash("Disconnect error, Try again")
	return redirect(url_for('profile'))


