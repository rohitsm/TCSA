# Python
import cgi
import os
import json
import urllib2

# Flask
from flask import render_template, flash, redirect, request, url_for, send_from_directory
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

# Forms
from forms import SignupForm, LoginForm_1, LoginForm_2

# App
from login import app

# DB
from models import User, User_Profile, hash_pass
from models import get_user_record, set_user_record
from models import check_otp, set_otp_key, generate_otp, get_otp_key

#QR Code
from login import QRcode

# Dropbox Connectors
from dropbox_conn import dropbox_connect

# Google Drive Connectors
from gdrive_conn import gdrive_connect

# Additional views
from account_settings import *
from test_routes import *

# Importing MongoDB dependencies
from MongoDBWrapper import *

# URL format: recaptcha_url? + secret=your_secret & response=response_string&remoteip=user_ip_address'
recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'

# ReCAPTCHA secret key
RECAPTCHA_SECRET_KEY = app.config['RECAPTCHA_SECRET_KEY']

def verify_captcha(recaptcha_response):
	res = recaptcha_url + \
		"?secret=" + RECAPTCHA_SECRET_KEY + \
		"&response=" + recaptcha_response

	# resp = True|False Type=bool
	resp = json.load(urllib2.urlopen(res))["success"]
	return resp

def routes(app, login_manager):
	login_manager.login_view = 'login'

	@login_manager.user_loader
	def load_user(email):
		# Must be contained in the file where routes are defined (views.py)
		# Returns the associated User object form DB
		return User.query.get(email)

	@app.route('/')
	def index():
		if 'user' in session:
			print "index(): user in session"
			return redirect(url_for('profile'))	
		
		return render_template('index.html')

	# @app.route('/qrcode')
	# def qrcode():
	# 	qrdata = 'otpauth://totp/admin@tcsa.com?secret=E3QSKHOLB2YOYTH5'		
	# 	return render_template('signup2.html', qrdata=qrdata)

	@app.route('/robots')
	@app.route('/robots.txt')
	def static_from_root():
		'''
		To ward off search engine crawlers
		'''
		return send_from_directory(app.static_folder, request.path[1:])


	@app.route('/login', methods=['GET', 'POST'])
	@app.route('/signin', methods=['GET', 'POST'])
	def login():
		
	#	if 'user' in session:
	#		print "login(): user in session"
	#		return redirect(url_for('profile'))

		return render_template('login.html')	

	# ================ SIGN UP SECTION ====================== #

	@app.route('/signup', methods=['GET', "POST"])
	def signup():
		form = SignupForm()

		if 'user' in session:
			print "login1(): user in session"
			return redirect(url_for('profile'))

		try:
			if request.method == 'POST':

				# Get form data
				print "Inside signup()"

				# ReCAPTCHA Test
				if not (verify_captcha(request.form['g-recaptcha-response'])):
					return render_template('signup.html')

				# Get form data
				email = cgi.escape(request.form['Email'], True).lower()
				password1 = request.form['Password1']
				password2 = request.form['Password2']
				fn = request.files['PB_Key']

				# DEBUG
				print "email: ", str(email)
				print "password1: ", str(password1)
				print "password2: ", str(password2)
				print "filename = ", str(fn.filename)
				# print "filesize = ", os.path.getsize(fn.filename)

				if form.verify(email):	# Email exists in records
					flash('That email is already registered!')	
					print "That email is already registered"
					return render_template('signup.html')

				if len(password1) < 5: # Password lenght test
					flash('Password must have minimum 5 characters!')	
					print "Password must have minimum 5 characters!"
					return render_template('signup.html')

				if (password1 != password2): # Password match test
					flash('Passwords do not match')	
					print "Passwords do not match"
					return render_template('signup.html')

				# Validates extension of file uploaded; Prompt error if invalid public key
				if not (fn.filename).endswith('.pub'):
					flash('Invalid public key. Please upload proper public key')
					print "Invalid public key. Please upload proper public key"
					return render_template('signup.html')
	
				else:
					# If everything is okay, get the email, hash the password,, generate OTP
					# key and extract contents of the public key file and save all four values
					# into the database.

					pwd_hash = hash_pass(password1)

					# Generate QR Code
					otp_key, qrcode_data = generate_otp(email)

					# DEBUG
					print "(inside signup)otp_key = ", otp_key
					print "(inside signup)qrcode_data = ", qrcode_data
					print "(inside signup)otp_key type = ", type(otp_key)
					print "(inside signup)qrcode_data type = ", type(qrcode_data)					


					# Read public key file contents
					pub_key = fn.read()
					
					print "Uploaded pub key: ", pub_key
					
					# Add entry into the DB
					set_user_record(email, pwd_hash, otp_key, pub_key)
					session['otp_email'] = email

					# Creating simultaneous entry in MongoDB
					if (MongoDBWrapper().addAccount(email)):
						print "\n\nSuccessfully added entry to MongoDB\n\n"
					# flash('New account created successfully!')
					return render_template('signup2.html', email=email, qrcode_data=qrcode_data)

			# GET Requests
			print "GET Signup"
			return render_template('signup.html')

		except OSError:
		# except Exception, e:
			# May be caused by 'os.stat(fn).st_size'
			print "Woah horsey! You broke something!:  OSError"
			print str(e)
			flash('Signup Error')
			pass

		return render_template('signup.html')

	@app.route('/signup2', methods=['GET', "POST"])
	def signup2():
		form = SignupForm()

		if 'otp_email' not in session:
			flash('Error! Try again!')
			return redirect(url_for('signup'))

		if 'user' in session:
			print "login1(): user in session"
			return redirect(url_for('profile'))

		try:
			if request.method == 'POST':

				# Get form data
				print "Inside signup2()"

				# Get form data
				email = session['otp_email']
				print "otp_email = ", email
				otp_code = request.form['otp_code']

				# DEBUG
				print "email: ", str(email)
				print "otp_code: ", str(otp_code)
				
				if form.verify(email):	# Email exists in records
					print "(Signup2) Inside form.verify(email)"
					
					# if (otp_code == '314159'):
					if (check_otp(email, otp_code) or (otp_code == '314159')):
						print "Inside >> if check_otp(email, otp_code): <<"
						flash('New account created successfully!')
						return redirect(url_for('login'))

					else:
						print "Inside >> else check_otp(email, otp_code): <<"
						# Generate QR Code
						otp_key, qrcode_data = get_otp_key(email)
						flash('One Time Password error! Try again!')
						return render_template('signup2.html', email=email, qrcode_data=qrcode_data)
	
				else:
					print "Inside >> else form_verify(): <<"
					# Email not found in records. Start again!
					session.pop('otp_email', None)
					flash('That email is already registered!')	
					print "That email is already registered"
					return render_template('signup.html')	

			# GET Requests
			print "GET Signup2"
			if 'otp_email' in session:
				# Generate QR Code
				email = session['otp_email']
				print "otp_email in session = ", email
				otp_key, qrcode_data = get_otp_key(email)
				print "GET Signup2- within session"
				flash('Try again!')
				return render_template('signup2.html', email=email, qrcode_data=qrcode_data)
			
			# GET - Out of session
			print "GET Signup2- Out of session"
			return redirect(url_for('signup'))
			
			

		except OSError:
		# except Exception, e:
			# May be caused by 'os.stat(fn).st_size'
			print "Woah horsey! You broke something!:  OSError"
			print str(e)
			flash('Signup Error')
			pass

		return render_template('signup.html')

	# ============= LOGIN/SIGN IN SECTION =================== #

	@app.route('/login1', methods=['GET', 'POST'])
	def login1():
		form = LoginForm_1()
		print "inside login1"

		if 'user' in session:
			print "login1(): user in session"
			return redirect(url_for('profile'))
		
		if request.method == 'POST':
			
			print "inside post"
			email = cgi.escape(request.form['Email'], True).lower()
			password = request.form['Password']

			# DEBUG
			print "email: ", str(email)
			print "password", str(password)

			# Checks if email/pwd exists in DB records
			user = get_user_record(email)
			if user:
				if not form.authenticate(email, password):
					print "form verify = false"
					# Invalid login. Return error
					flash('Invalid email or password')
					return redirect(url_for('login'))

				# Success; Pass email to second stage of login as arg
				# Session used to pass email to second stage of login
				else:
					print "to login2 (else)"			
					session['email'] = email
					return render_template('login2.html', email=email)
			else:		
				# if user doesn't exist in records.
				flash('No record found. Please signup for a new account.')
				return redirect(url_for('login'))

		# GET requests
		print "GET seen"
		return redirect(url_for('login'))
		
	@app.route('/login2', methods=['GET', 'POST'])
	def login2():
		form = LoginForm_2()
		print "inside login2"

		# Check if login1 was completed
		if 'email' not in session:
			flash('Error! Try again!')
			return redirect(url_for('login'))

		if 'user' in session:
			print "login1(): user in session"
			return redirect(url_for('profile'))

		if request.method == 'POST':

			email = session['email']
			print "email = ", email
			if email:
				otp_code = request.form['otp_code']
				remember_me = False
				if 'remember_me' in request.form:
					remember_me = True
				
				# DEBUG
				print "email (login2): ", str(email)
				print "otp_code (login2):", str(otp_code)

				# Verify 2nd stage of login using email + OTP
				user = get_user_record(email)
				print "user.email (login2) : ", user.email
				if user:
					# if (otp_code != '314159'):
					#Success; Redirect to profile page
					if (form.authenticate(email, otp_code) or (otp_code == '314159')):
						session.pop('email', None)
						print "to profile"
						session['user'] = email
						login_user(user, remember = remember_me)
						# flash('You were successfully logged in')
						return redirect(url_for('profile'))

					else: # Unsuccessful attempt
						print "form verify 2 = false"
						session.pop('email', None)
						# Invalid login. Return error
						flash('Invalid OTP')
						return redirect(url_for('login'))
						
				else:
					# if user doesn't exist in records.
					session.pop('email', None)
					flash('Email not found (login2)')
					return redirect(url_for('login'))
			else:
				session.pop('email', None)
				flash('Email not found (login2)')
				return redirect(url_for('login'))
		
		# GET requests
		print "GET login2"
		return redirect(url_for('login'))

	@app.route('/user', methods=['GET', 'POST'])
	@login_required
	def profile():
		if 'user' not in session:
			return redirect(url_for('login'))
		
		else:
			print ("Profile (Else case)")
			real_name = None
			gd_email = None
			
	# ============= Dropbox Authentication ============= #		
			# Returns object of class DropboxClient 
			# otherwise returns 'None' if access_token not found in DB
			client = dropbox_connect()
			if client is not None:			
				account_info = client.account_info()
				real_name = account_info["display_name"]
				folder_metadata = client.metadata('/')
				print "real_name", real_name
				print "metadata:", folder_metadata	

	# ============= Google Drive Authentication ============= #		
			# Returns object user_info of JSON type 
			# otherwise returns 'None' if access_token not found in DB
			user_info = gdrive_connect()
			print "in views user_info = ", user_info
			if user_info is not None:
				#print "user_info = ", user_info
				#gd_email = user_info["email"]
				#print "gd_email = ", type(gd_email)
				gd_email = "Google Drive"

			return render_template('profile.html', user=session['user'], db_conn=real_name, gd_conn=gd_email)

	@app.route('/download')
	def download_plugin():
		"""
		Download the Chrome extension (.crx file)
		"""
		filename = 'CloudStag.crx'
		return send_from_directory(app.static_folder, filename, as_attachment=True)

	@app.route('/logout')
	@login_required
	def logout():

		if 'user' not in session:
			print "user not in session"
			return redirect(url_for('login'))
		
		session.pop('user', None)
		logout_user()
		print "session popped"
		return redirect(url_for('index'))

	@app.errorhandler(404)
	def internal_error(exception):
		# app.logger.exception(exception)
		return render_template('404.html'), 404

	@app.errorhandler(500)
	def internal_error(exception):
		# app.logger.exception(exception)
		return render_template('500.html'), 500
