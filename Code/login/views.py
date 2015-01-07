# Python
import cgi
import os

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

# App
from login import app
from login import login_manager 
from forms import SignupForm, LoginForm_1, LoginForm_2

# DB
from models import User_1, User_2, User_Profile, set_pass
from login import db

# Dropbox Connectors
from dropbox_conn import dropbox_connect


login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(email):
	# Must be contained in the file where routes are defined (views.py)
	# Returns the associated User object form DB
	return User_2.query.get(email)

@app.route('/')
def index():
	if 'user' in session:
		print "user in session"
		return redirect(url_for('profile'))
	
	return render_template('index.html')

# To test DB connection
@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "Works"
	else:
		return "Not Working"

@app.route('/login', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])
def login():
	if 'user' in session:
		print "user in session"
		return redirect(url_for('profile'))

	return render_template('login.html')

# ================ SIGN UP SECTION ====================== #

@app.route('/signup', methods=['GET', "POST"])
def signup():
	form = SignupForm()

	if request.method == 'POST':

		# Get form data
		print "Inside signup()"
		
		email = cgi.escape(request.form['Email'], True).lower()
		print "email = ", str(email)

		pwd_hash = set_pass(request.form['Password1'])
		print "pwd_hash = ", str(pwd_hash)

		passphrase_hash = set_pass(request.form['Passphrase1'])
		print "passphrase_hash = ", str(passphrase_hash)

		fn = request.files['PB_Key']
		print "filename = ", str(fn.filename)

		# Validates extension of file uploaded and renames the file
		# based on email address: 
		# <name before '@' in email>.pub 

		if (fn.filename).endswith('.pub'):
			new_fn = str(email.split('@')[0]).replace('.','') + '.pub'
			print "new_fn = ", str(new_fn)
			print "current WD = ", os.getcwd()
			print "UPLOAD_FOLDER = ", app.config['UPLOAD_FOLDER']
			fn.save(os.path.join(app.config['UPLOAD_FOLDER'] , new_fn))

		print "Uploaded pub key "

		if form.verify(email):	#Email exists in records
			flash('That email is already registered!')	
			print "That email is already registered"
			return render_template('signup.html')

		else:
			# Add entry into the DB
			entry_1 = User_1(email, pwd_hash)
			entry_2 = User_2(email, passphrase_hash)
			entry_3 = User_Profile(email)
			print "entry_1", entry_1
			print "entry_2", entry_2
			print "entry_3", entry_3
			
			entry_1.child_1.append(entry_2)
			entry_1.child_2.append(entry_3)
			db.session.add(entry_1)
			
			db.session.commit()

			flash('New account created successfully!')
			return redirect(url_for('login'))

	# GET Requests
	print "GET Signup"
	return render_template('signup.html')

# ============= LOGIN/SIGN IN SECTION =================== #

@app.route('/login1', methods=['GET', 'POST'])
def login1():
	form = LoginForm_1()
	print "inside login1"

	if 'user' in session:
		print "user in session"
		return redirect(url_for('profile'))
	
	if request.method == 'POST':
		
		print "inside post"
		email = cgi.escape(request.form['Email'], True).lower()
		password = request.form['Password']

		# DEBUG
		print "email: ", str(email)
		print "password", str(password)

		# Checks if email/pwd exists in DB records
		user = User_1.query.filter_by(email = email).first()
		if user:
			if not form.verify(email, password):
				print "form verify = false"
				# Invalid login. Return error
				flash('Invalid email or password')
				return redirect(url_for('login'))

			# Success; Pass email to second stage of login as arg
			# Session used to pass email to second stage of login
			else:
				print "to login2 (else)"			
				session['email'] = email
				return render_template('login2.html', email=session['email'])
		else:
			flash("Incorrect email/password")
		
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
		return redirect(url_for('login'))

	if request.method == 'POST':

		email = session['email']
		if (email):
			passphrase = request.form['Passphrase']
			#remember_me = False
			#if 'remember_me' in request.form:
			#	remember_me = True
			
			# DEBUG
			print "email (login2): ", str(email)
			print "passphrase (login2):", str(passphrase)

			# Verify 2nd stage of login using email + passphrase
			user = User_2.query.filter_by(email = session['email']).first()
			print "user.email (login2) : ", user.email
			if user:				
				if not form.verify(email, passphrase):
					print "form verify 2 = false"
					# Invalid login. Return error
					flash('Invalid passphrase')
					return redirect(url_for('login'))

				#Success; Redirect to profile page
				else: 
					session.pop('email', None)
					print "to profile"
					session['user'] = email
					# login_user(user, remember = remember_me)
					flash('You were successfully logged in')
					return redirect(url_for('profile', email = email))

			else:
				# if user doesn't exist in records.
				flash('Email not found (login2)')
				return redirect(url_for('login'))
		else:
			flash("Email not found (login2)")
			return redirect(url_for('login'))
	
	# GET requests
	print "GET login2"
	return redirect(url_for('login'))

@app.route('/user')
@login_required
def profile():
	if 'user' not in session:
		return redirect(url_for('login'))
	else:
		# Dropbox Authentication; returns 'None' if access_token not found in DB
		real_name = dropbox_connect()
		print "real_name", real_name
		
		return render_template('profile.html', user=session['user'], db_conn=real_name)

@app.route('/logout')
@login_required
def logout():

	if 'user' not in session:
		print "user not in session"
		return redirect(url_for('login1'))
	
	session.pop('user', None)
	# logout_user()
	print "session popped"
	return redirect(url_for('index'))

# @app.errorhandler(404)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('500.html'), 500
