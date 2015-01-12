# Connect dropbox

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

# App
from login import app
from login import login_manager 

# DB
# from models import User_Profile #, set_access_token, get_access_token
from models import get_dropbox_token, set_dropbox_token
from login import db

# Dropbox API
from dropbox.client import DropboxClient, DropboxOAuth2Flow

DROPBOX_APP_KEY = app.config['DROPBOX_APP_KEY']
DROPBOX_APP_SECRET = app.config['DROPBOX_APP_SECRET']

# Get access token from DB
def get_access_token():
    email = session.get('user')
    print "inside get_access_token() \nemail = ", email
    if email is None:
        return None

    # Get access_token from database
    access_token = get_dropbox_token(email)
    print "access_token from db = ", access_token
    if access_token:
        return access_token

    print "Error record not found in DB. Not connected to dropbox"
    return None

#@app.route('/dropbox-connect')
def dropbox_connect():
    print "inside dropbox_connect()"
    access_token = get_access_token()
    client = None
    app.logger.info('access_token = %r', access_token)
    if access_token is not None:
        client = DropboxClient(access_token)
    # Object contains all the information
    return client

@app.route('/dropbox-auth-finish')
def dropbox_auth_finish():
    email = session.get('user')
    print "inside dropbox_auth_finish. \nemail = ", email
    if email is None:
        abort(403)
    try:
        access_token, user_id, url_state = get_auth_flow().finish(request.args)
    except DropboxOAuth2Flow.BadRequestException, e:
        abort(400)
    except DropboxOAuth2Flow.BadStateException, e:
        abort(400)
    except DropboxOAuth2Flow.CsrfException, e:
        abort(403)
    except DropboxOAuth2Flow.NotApprovedException, e:
        flash('Not approved?  Why not')
        return redirect(url_for('profile'))
    except DropboxOAuth2Flow.ProviderException, e:
        app.logger.exception("Auth error" + e)
        abort(403)
    
    print "user adding dropbox token to DB for email ", email
    # user = User_Profile.query.filter_by(email = email).first()
    if set_dropbox_token(email, access_token):
        print "added access_token to DB"
        #flash('Connected')
        return redirect(url_for('profile'))

    flash('Error. Try again!')
    print "Error. Could not add access_token to DB"
    return redirect(url_for('profile'))

@app.route('/dropbox-auth-start')
def dropbox_auth_start():
    if 'user' not in session:
        abort(403)
    email = session.get('user')
    print "Inside dropbox_auth_start(). \nUser in session"
    print "email= ", email
    if email is None:
        abort(403)

    return redirect(get_auth_flow().start())

@app.route('/dropbox-disconnect')
def dropbox_disconnect():
	# Disconnect Dropbox access token from DB records
    print "inside dropbox_logout()"
    email = session.get('user')
    if email is None:
        abort(403)

    print "Disconnecting Dropbox access_token for email: ", email
    # user = User_Profile.query.filter_by(email = email).first()
    if set_dropbox_token(email, None):
        print "Disconnected Dropbox. remomved token from DB"
        return redirect(url_for('profile'))

    flash("Disconnect error, Try again")
    return redirect(url_for('profile'))

def get_auth_flow():
    redirect_uri = url_for('dropbox_auth_finish', _external=True)
    return DropboxOAuth2Flow(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, redirect_uri,
                                       session, 'dropbox-auth-csrf-token')
















