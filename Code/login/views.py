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
from models import User_1, User_2, set_pass
from login import db

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(email):
	# Must be contained in the file where routes are defined (views.py)
	# Returns the associated User object form DB
	return User_1.query.get(email)

@app.route('/')
def index():
	if 'user' not in session:
		return render_template('index.html')

	# Add Dropbox authentication here

	return render_template('profile.html', user=user)

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
	return render_template('login.html')


# ================ SIGN UP SECTION ====================== #

@app.route('/signup', methods=['GET', "POST"])
def signup():
	form = SignupForm()

	# GET request
	if request.method == 'GET':
		return render_template('signup.html')
		
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
		print os.getcwd()
		fn.save(os.path.join(app.config['UPLOAD_FOLDER'] , new_fn))

	if form.verify(email) != False:		
		flash('That email is already registered')	
		return render_template('signup.html')

	else:
		form.add_entry(email, pwd_hash, passphrase_hash)
		flash('New account created successfully ')
		return redirect(url_for('login'))

# ============= LOGIN/SIGN IN SECTION =================== #

@app.route('/login1', methods=['GET', 'POST'])
def login1():
	form = LoginForm_1()
	error = None
	print "inside login1"

	if 'user' not in session:
		return redirect(url_for('login', email=email))
	
	# GET requests
	if request.method == 'GET':
		print "GET seen"
		return redirect(url_for('login'))
	
	print "inside post"
	email = cgi.escape(request.form['Email'], True).lower()
	pwd_hash = set_pass(request.form['Password'])

	# DEBUG
	print "email: ", str(email)
	print "pwd_hash", str(pwd_hash)

	# Checks if email/pwd exists in DB records
	user = User_1.query.filter_by(email = email).first()
	if user:			
		# Change this to '==''
		if form.verify(email, pwd_hash) != False:
			print "form verify = false"
			# Invalid login. Return error
			error = 'Invalid password'
			return redirect(url_for('login', error=error))

		# Success; Pass email to second stage of login as arg
		# Session used to pass email to second stage of login
		else:
			print "to login2 (else)"			
			session['email'] = email
			return render_template('login2.html')
	else:
		flash("Email not found in records.")
	
	# if user doesn't exist in records.
	error = 'No record found. Create new account?'
	return redirect(url_for('login', error = error))


@app.route('/login2', methods=['GET', 'POST'])
def login2():
	form = LoginForm_2()
	error = None
	print "inside login2"

	# Check if login1 was completed
	if 'email' not in session:
		return redirect(url_for('login'))

	# GET requests
	if request.method == 'GET':
		print "GET login2"
		return redirect(url_for('login'))

	email = session['email']
	if (email):
		passphrase_hash = set_pass(request.form['Passphrase'])
		remember_me = False
		if 'remember_me' in request.form:
			remember_me = True
		
		# DEBUG
		print "email (login2): ", str(email)
		print "passphrase (login2):", str(passphrase_hash)

		# Verify 2nd stage of login using email + passphrase_hash
		user = User_1.query.filter_by(email = session['email']).first()
		if user:				
			# Change this to '==''
			if (form.verify(email, passphrase_hash)) != False:
				print "form verify 2 = false"
				# Invalid login. Return error
				error = 'Invalid passphrase'
				return redirect(url_for('login', error=error))

			#Success; Redirect to profile page
			else: 
				session.pop('email', None)
				print "to profile"
				session['user'] = user.get_id
				login_user(user, remember = remember_me)
				flash('You were successfully logged in')
				return redirect(url_for('profile', email = email))

		else:
			# if user doesn't exist in records.
			error = 'Email not found (login2)'
			return redirect(url_for('login', error = error))
	else:
		flash("Email not found (login2)")
	return redirect(url_for('login', error = error))
	

@app.route('/user')
@login_required
def profile():

	if 'user' not in session:
		return redirect(url_for('home'))
	else:
		return render_template('profile.html', user=user)

	# if 'email' not in session:
	# 	return redirect(url_for('login1'))

	# user = User_1.query.filter_by(email = session['email']).first()

	# if user is None:
	# 	return redirect(url_for('login1'))
	# else:
	# 	return render_template('profile.html')

@app.route('/logout')
# @login_required
def logout():

	if 'email' not in session:
		return redirect(url_for('login1'))
	
	# session.pop('user', None)
	logout_user()
	return redirect(url_for('index'))

# @app.errorhandler(404)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('500.html'), 500
