# Imports

# Python
import cgi
import os
import json
import urllib2

# App
from login import app
from login import login_manager 

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

# Forms
from forms import LoginForm_1, LoginForm_2

# DB
from models import get_user_record, set_user_record

# Aswin's function import
from MongoDBWrapper import *

# To test DB connection
@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "Works"
	else:
		return "Not Working"

@app.route('/gdrive')
def gdrive_test():
	#MongoDBWrapper().addStorage()
	return "GDRIVE SUCCESSFULL!"

@app.route('/testajax', methods=['GET', 'POST'])
def testajax():
	form = LoginForm_1()
	print "inside testajax1"
	
	if request.method == 'POST':
		p_email = cgi.escape(request.form['Email'], True).lower()
		p_password = request.form['Password']

		# DEBUG
		print "AJAX p_email:", p_email
		print "AJAX p_password: ", p_password

		# Checks if p_email/p_pwd exists in DB records
		user = get_user_record(p_email)
		if user:
			if not form.authenticate(p_email, p_password):
				print "form verify = false"
				# Invalid login. Return error
				print "testajax: Invalid email or password"
				return json.dumps({'status':'NotOK', 'Error': 'Invalid email or password'})			

			# Success; Pass email to second stage of login as arg
			# Session used to pass email to second stage of login
			else:
				print "to testajax (else)"			
				# session['p_email'] = p_email
				print "testajax: Logged in!"
				return json.dumps({'status':'OK','email': p_email})
		else: 
			# if user doesn't exist in records
			print "testajax: User record not found in DB"
			return json.dumps({'status':'NotOK', 'Error': 'No record found. Please sign up for a new account!'})

	# GET requests
	print "testajax: GET"
	flash('Please log in to continue')
	return render_template('signup.html')

@app.route('/testajax2', methods=['GET', 'POST'])
def testajax2():
	form = LoginForm_2()
	
	if request.method == 'POST':
		print "inside testajax2"

		# p_email = session['p_email']
		# print "email = ", session['p_email']
		p_email = cgi.escape(request.form['Email'], True).lower()
		# if p_email:
		p_passphrase = request.form['Passphrase']
	
		# DEBUG
		print "AJAX email_2:", p_email
		print "AJAX passphrase_2: ", p_passphrase

		# Verify 2nd stage of login using email + passphrase
		user = get_user_record(p_email)
		print "user.email (login2) : ", user.email
		if user:				
			if not form.authenticate(p_email, p_passphrase):
				print "form verify 2 = false"
				# Invalid login. Return error
				print "testajax2: Invalid email or password"
				return json.dumps({'status':'NotOK', 'Error': 'Invalid email or password'})			

			#Success; Redirect to profile page
			else: 
				#session.pop('p_email', None)
				print "(Inside testajax2) to profile"
				session['user'] = p_email
				print "ADDED SESSION!"
				sess_em = session.get('user')
				print "sess_em = ", sess_em
				# login_user(user, remember = remember_me)
				# flash('You were successfully logged in')
				return json.dumps({'status':'OK','email': p_email})
		else: 
			# if user doesn't exist in records
			print "testajax2: User record not found in DB"
			return json.dumps({'status':'NotOK', 'Error': 'No record found. Please sign up for a new account!'})

	# GET requests
	print "testajax2: GET"
	flash('Please log in to continue')
	return render_template('signup.html')


@app.route('/testupload', methods=['GET', 'POST'])
def testupload():
	
	if request.method == 'POST':
		req = request.json['req']
		user_email = request.json['user_email']
		print "req = ", req
		print "user_email", user_email

		p_email = session.get('user')
		print "\n\nSESSION EMAIL : ". p_email
		
		if req == 'upload':
			# Gets encrypted file contents from plugin and sends to DB for saving
			
			filename =  request.json['filename']
			file_content = request.json['file_content']
			
			# Debug 
			print "\n==============(if req == 'upload')=============="
			print "user_email", user_email
			print "filename: ", filename
			print "file_content", file_content
			print "\n==============END TEST UPLOAD=============="
			if (MongoDBWrapper().upload(email=user_email, fileName=filename, fileContent=file_content)):
				return json.dumps({'status':'OK', 'user_email':user_email})
			else:
				return json.dumps({'status':'NotOK'})

		elif req == 'download':
			# Retrives file from DB and sends it to plugin

			filename =  request.json['filename']

			# Debug 
			print "\n==============(else if req == 'download')=============="
			print "user_email", user_email
			print "filename: ", filename
			print "\n==============END TEST DOWNLOAD=============="
			
			file_content = MongoDBWrapper().download(email=user_email, filename=filename)
			if file_content:
				return json.dumps({'status':'OK', 'file_content':file_content})
			else:
				return json.dumps({'status':'NotOK'})

		elif req == 'upload_metadata':
			# Gets encrypted metadata from plugin and sends to DB for saving

			metadata = request.json['metadata']

			# Debug 
			print "\n==============(else if req == 'upload_metadata')=============="
			print "user_email", user_email
			print "metadata: ", metadata
			print "\n==============END TEST UPLOAD_METADATA=============="

			if (MongoDBWrapper().upload_metadata(email=user_email, metadata=metadata)):
				session.pop('user', None)
				print "SESSION POPPED!"
				return json.dumps({'status':'OK', 'user_email':user_email})
			else:
				return json.dumps({'status':'NotOK'})

		elif req == 'download_metadata':
			# Retrives entire metadata (right from the root directory) from DB and sends it to plugin

			# Debug 
			print "\n==============(else if req == 'download_metadata')=============="
			print "user_email", user_email
			print "\n==============END TEST DOWNLOAD_METADATA=============="
			
			metadata = MongoDBWrapper().download_metadata(email=user_email)
			if metadata:
				return json.dumps({'status':'OK', 'metadata':metadata})
			else:
				return json.dumps({'status':'NotOK'})

		elif req == 'delete':
			filename =  request.json['filename']

			if (MongoDBWrapper().delete(email=user_email, fileName=filename)):
				return json.dumps({'status':'OK', 'user_email':user_email})	
			else:
				return json.dumps({'status':'NotOK'})

		else:
			print "request parameter error"
			return json.dumps({'status': 'NotOK'})

	else:
		print"GET Request"
		return render_template('signup.html')

