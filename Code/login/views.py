# Python
import cgi
import os

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort
from flask.ext.login import login_user, logout_user, login_required, current_user
from forms import SignupForm, LoginForm_1, LoginForm_2

# DB
from login import db
from models import User, User_Profile, set_pass
from models import get_user_record, set_user_record

# Dropbox Connectors
from dropbox_conn import dropbox_connect

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
		
	#	if 'user' in session:
	#		print "login(): user in session"
	#		return redirect(url_for('profile'))

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
				set_user_record(email, pwd_hash, passphrase_hash)
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
			# user = User_1.query.filter_by(email = email).first()
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

		if 'user' in session:
			print "login1(): user in session"
			return redirect(url_for('profile'))

		if request.method == 'POST':

			email = session['email']
			print "email = ", email
			if email:
				passphrase = request.form['Passphrase']
				remember_me = False
				if 'remember_me' in request.form:
					remember_me = True
				
				# DEBUG
				print "email (login2): ", str(email)
				print "passphrase (login2):", str(passphrase)

				# Verify 2nd stage of login using email + passphrase
				user = get_user_record(email)
				print "user.email (login2) : ", user.email
				if user:				
					if not form.authenticate(email, passphrase):
						print "form verify 2 = false"
						# Invalid login. Return error
						flash('Invalid passphrase')
						return redirect(url_for('login'))

					#Success; Redirect to profile page
					else: 
						session.pop('email', None)
						print "to profile"
						session['user'] = email
						login_user(user, remember = remember_me)
						flash('You were successfully logged in')
						return redirect(url_for('profile'))

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

	@app.route('/user', methods=['GET', 'POST'])
	@login_required
	def profile():
		if 'user' not in session:
			return redirect(url_for('login'))
		
		else:
			print ("Profile (Else case)")
			real_name = None
			
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
			return render_template('profile.html', user=session['user'], db_conn=real_name)

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

	# @app.errorhandler(404)
	# def internal_error(exception):
	# 	# app.logger.exception(exception)
	# 	return render_template('404.html'), 404

	# @app.errorhandler(500)
	# def internal_error(exception):
	# 	# app.logger.exception(exception)
	# 	return render_template('500.html'), 500
