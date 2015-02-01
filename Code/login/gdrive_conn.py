# Connect Google Drive
# Reference: https://developers.google.com/api-client-library/python/auth/web-app

# Python
import json
import httplib2
import urllib2
from urllib import urlencode

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
from oauth2client import client

GDRIVE_CLIENT_SECRET = app.config['GDRIVE_CLIENT_SECRET']
GDRIVE_CLIENT_ID = app.config['GDRIVE_CLIENT_ID']

# Full, permissive scope to access all of a user's files
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Create JSON element from dict CLIENT_SECRET
# CLIENT_SECRET = json.dumps(app.config['CLIENT_SECRET'])

def get_gdrive_refresh_token():
	""" Get user credentials from database
	"""
	email = session.get('user')
	print "inside get_gdrive_access_token() \nemail = ", email
	if email is None:
		return None

	# Get the refresh token from the DB
	refresh_token = get_gdrive_token(email)
	# print "refresh_token form db = ", refresh_token
	if refresh_token:
		return refresh_token

	print "Error no record of refresh_token found in DB. Not connected to Google Drive"
	return None

def gdrive_connect():
	"""Interfaces with views.py

	Returns:
		User information as a dict if it exists otherwise None. 
	"""
	try:		
		credentials_from_db = get_gdrive_refresh_token()
		# print "refresh_token = ", credentials_from_db['refresh_token']
		
		# No record found in DB
		if credentials_from_db is None:
			print "refresh_token = none"
			return None

		########## Testing and debugging. Remove this from here ##########
		refresh_token = credentials_from_db.refresh_token
		print "==================================="
		print "\n\n OLD refresh_token = ", refresh_token
		print "new creds = ", refresh_access_token(credentials_from_db)

		print "===================================\n\n"

		#####################################################################

		credentials = OAuth2Credentials.from_json(credentials_from_db)
		print "credentials = ", credentials
		if credentials.access_token_expired:
			print "credentials.access_token_expired"
			return redirect(url_for('gdrive_auth_finish'))
			# return None
		else:
			# Returns user information as a JSON object
			user_info_service = build(
				serviceName = 'drive', version = 'v2',
				http = credentials.authorize(httplib2.Http()) )
			
			# user_info is of type dict 
			user_info = user_info_service.files().list().execute()
			print "\n\nuser_info type = ", type(user_info)
			print "\n\nuser_info = ", json.dumps(user_info, indent=4, sort_keys=True)
			print "\n\nuser_info type (after) = ", type(user_info)
			return json.dumps(user_info)

	except client.AccessTokenRefreshError as e:
		flash('Drive access revoked!')
		print "client.AccessTokenRefreshError", e
		# User revoked access, so remove gdrive token from DB
		set_gdrive_token(email, None)
		return None


def refresh_access_token(old_credentials):
	""" Take credentials containing expired access token)as arg and return
		credentials with renewed access token.

		Get refresh token for this purpose from db. To look in db records,
		use corresponding email (taken from session)

	Args:
		old_credentials: From DB; contains expired access_token; also contains refresh_token
	Returns:
		new_credentials: Contains renewed access_token
	"""

	try:	
		# Get email from session. Email used for querying DB
		email = session.get('user')
		print "inside gdrive-auth-finish. \nEmail = ", email
		if email is None:
			abort(403)

		# Extract out refresh_token from old_credentials
		refresh_token = old_credentials.refresh_token

		# Build the JSON variable for credentials
		cred = {
			'client_id' : GDRIVE_CLIENT_ID,
			'client_secret' : GDRIVE_CLIENT_SECRET,
			'refresh_token' : refresh_token,
			'grant_type' : "refresh_token"
		}

		# Renew access_token
		req = urllib2.Request("https://www.googleapis.com/oauth2/v3/token", urlencode(cred))
		resp = urllib2.urlopen(req)
		content = resp.read()
		cont = json.loads(content)
		print "inside refresh_access_token. content = ", content
		print "NEW access_token. cont = ", cont["access_token"]
		new_access_token = cont["access_token"]

		# Use regex to replace old access_token with renewed one
		matchObj = re.match(r'.*access_token": "(.*)", "token_uri.*', old_credentials)
		old_access_token = matchObj.group(1)
		new_credentials = old_credentials.replace(old_access_token, new_access_token)

		print "old_access_token: ", old_access_token
		print "new_access_token: ", new_access_token
		print "renewed credentials = ", new_credentials
		return new_credentials
	
	except AttributeError as e:
		print "No refresh_token found in old_credentials. NoneType!"
		return None

	except Exception, e:
		raise e

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
		
		# type(credentials) = class 'oauth2client.client.OAuth2Credentials'
		# credentials 
		
		credentials = flow.step2_exchange(auth_code)
		print "credentials = ", credentials.to_json()
		# session['credentials'] = credentials.to_json()

		# Store credentials as 'oauth2client.client.OAuth2Credentials' object
		if set_gdrive_token(email, credentials):
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
	"""Disconnect Google Drive refresh_token from DB records
	"""
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


