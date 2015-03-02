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

# To test DB connection
@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "Works"
	else:
		return "Not Working"

@app.route('/testajax', methods=['GET', 'POST'])
def testajax():
	
	if request.method == 'POST':
		email = cgi.escape(request.form['Email'], True).lower()
		password = request.form['Password']

		print "AJAX email:", email
		print "AJAX password: ", password

		return json.dumps({'status':'OK','email':email, 'password':password})
	
	# GET Request
	return render_template('test.html')



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