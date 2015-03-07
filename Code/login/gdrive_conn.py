# Connect Google Drive
# Reference: https://developers.google.com/api-client-library/python/auth/web-app

# Python
import json
import httplib2
import urllib2
from urllib import urlencode
import re

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
from oauth2client.client import Credentials

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

def refresh_access_token(cred):
	""" Take credentials (with expired access token) as arg and return
		credentials with renewed access token.

		Get refresh token for this purpose from db. To look in db records,
		use corresponding email (taken from session). After renewing, write
		new credentials back to DB

	Args:
		cred: From DB; contains expired access_token; also contains refresh_token
	Returns:
		cred: Contains renewed access_token
	"""

	try:	
		# Get email from session. Email used for querying DB
		email = session.get('user')
		print "inside gdrive-auth-finish. \nEmail = ", email
		if email is None:
			abort(403)

		# Extract out refresh_token from cred
		refresh_token = cred.refresh_token

		# Build the JSON variable for credentials
		renew = {
			'client_id' : GDRIVE_CLIENT_ID,
			'client_secret' : GDRIVE_CLIENT_SECRET,
			'refresh_token' : refresh_token,
			'grant_type' : "refresh_token"
		}

		# Renew access_token using the above refresh_token
		req = urllib2.Request("https://www.googleapis.com/oauth2/v3/token", urlencode(renew))
		resp = urllib2.urlopen(req)
		content = resp.read()
		cont = json.loads(content)

		# Replace old access_token with renewed one
		cred.access_token = cont["access_token"]	

		# Update DB records with new credentials.
		set_gdrive_token(email, cred.to_json())
	
		return cred
	
	except AttributeError as e:
		print "No refresh_token found in old_credentials. NoneType?", e
		return None

	except Exception as e:
		print "Error: ", e
		return None

def get_user_info(credentials):
	"""Send a request to the UserInfo API to retrieve the user's information.

	Args:
		credentials: oauth2client.client.OAuth2Credentials instance to authorize the
		             request.
	Returns:
		User information as a dict.
	"""	
	try:
		# Returns user information as a JSON object
		user_info_service = build(
			serviceName = 'drive', version = 'v2',
			http = credentials.authorize(httplib2.Http()) )		
		# user_info is of type dict 
		user_info = user_info_service.files().list().execute()
		if user_info:
			return user_info
		else:
			return None
	except Exception as e:
		# logging.error('An error occurred: %s', e)
		print "An error occurred: ", e

def gdrive_connect():
	"""Interfaces with views.py

	Returns:
		User information as a JSON string if it exists otherwise None. 
	"""
	try:		
		cred = get_gdrive_refresh_token()
		print "gdrive_connect() - cred from db = ", cred
		# Convert JSON represenation to an instance of 'OAuth2Credentials'
		credentials = Credentials.new_from_json(cred)
		
		# No record found in DB
		if credentials is None:
			print "No records for credentials found in DB = none"
			return None		

		# Expired access_token
		if credentials.access_token_expired:
			# Get new access_token
			print "credentials.access_token_expired"
			credentials = refresh_access_token(credentials)

		user_info = get_user_info(credentials)
		# print "\n\nuser_info = ", json.dumps(user_info, indent=4, sort_keys=True)
		return json.dumps(user_info)

	except client.AccessTokenRefreshError as e:
		flash('Drive access revoked!')
		print "client.AccessTokenRefreshError", e
		# User revoked access, so remove gdrive token from DB
		set_gdrive_token(email, None)
		return None

	except AttributeError as e:
		print "no record found in DB. \nArributeError", e
		# No record exists in DB for GDrive
		return None

	except TypeError as e:
		print "no record found in DB. \nTypeError", e
		return None


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
		
		# Credentials is of type class 'oauth2client.client.OAuth2Credentials'
		credentials = flow.step2_exchange(auth_code)

		# Convert credentials to a JSON representation before storing
		if set_gdrive_token(email, credentials.to_json()):
			print "credentials added to DB: type", type(credentials)
			return redirect(url_for('profile'))

		flash('Error in adding Gdrive token to DB')
		print "Error, Could not add credentials to DB"
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
