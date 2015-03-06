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

from models import get_user_record, set_user_record

# CORS - Cross-Origin Resource Sharing
# from flask.ext.cors import CORS, cross_origin

# To test DB connection
@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "Works"
	else:
		return "Not Working"

@app.route('/testajax', methods=['GET', 'POST', 'OPTIONS'])
# @cross_origin()
def testajax():
	
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
				session['p_email'] = p_email
				print "testajax: Logged in!"
				return json.dumps({'status':'OK','email': p_email})
		else: 
			# if user doesn't exist in records
			print "testajax: User record not found in DB"
			return json.dumps({'status':'NotOK', 'Error': 'No record found. Please sign up for a new account!'})

	# GET requests
	print "testajax: GET"
	return render_template('test.html')

@app.route('/testajax2', methods=['GET', 'POST'])
# @cross_origin()
def testajax2():
	
	if request.method == 'POST':

		p_email = session['p_email']
		print "email = ", p_email
		if p_email == cgi.escape(request.form['Email'], True).lower():
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
					session.pop('p_email', None)
					print "to profile"
					session['user'] = p_email
					login_user(user, remember = remember_me)
					# flash('You were successfully logged in')
					return json.dumps({'status':'OK','email': p_email})
			else: 
				# if user doesn't exist in records
				print "testajax2: User record not found in DB"
				return json.dumps({'status':'NotOK', 'Error': 'No record found. Please sign up for a new account!'})

	# GET requests
	print "testajax2: GET"
	return render_template('test2.html')


@app.route('/testupload', methods=['GET', 'POST'])
def testupload():
	
	if request.method == 'POST':
		filename =  request.json['filename']
		file_content = request.json['file_content']
		user_email = request.json['user_email']
		
		# Debug 
		print "\n==============BEGIN TEST UPLOAD=============="
		print "filename: ", filename
		print "file_content", file_content
		print "user_email", user_email
		print "\n==============END TEST UPLOAD=============="
		
		return json.dumps({'status':'OK','filename':filename, 'file_content':file_content, 'user_email':user_email})
	else:
		print"GET Request"
		return render_template('signup.html')

