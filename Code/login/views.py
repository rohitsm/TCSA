
# Flask
from flask import render_template, flash, redirect, request, url_for
from login import app
from forms import SignupForm, LoginForm_1, LoginForm_2
from models import User_1, User_2
from flask import session

# DB
from login import db
<<<<<<< HEAD

@app.route('/')
def index():
	return "hello"


@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "Works"
	else:
		return "Not Working"


@app.route('/signup', methods=['GET', "POST"])
def signup():
	form = SignupForm()

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signup.html', form=form)

		else:
			new_user1 = User_1(form.email.data, form.password.data)
			new_user2 = User_2(form.email.data, form.passphrase.data)
			
			# Insert into DBs
			db.session.add(new_user1)
			db.session.add(new_user2)
			
			# Update the DB by commiting the transaction
			db.session.commit()

			session['email'] = new_user1.email
			return redirect(url_for('profile'))

	# GET request
	return render_template('signup.html', form=form)


@app.route('/login1', methods=['GET', 'POST'])
def login1():

	form = LoginForm_1()

	if 'email' in session:
		return redirect(url_for('profile'))

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', form=form)
		
		else:
			user = User_1(form.email.data)
			print "inside login1: user_email= ", str(user.email)
			return redirect(url_for('login2', email=user.email))

	# GET request
	return render_template('signin.html', form=form)


@app.route('/login2', methods=['GET', 'POST'])
def login2():

	form = LoginForm_2()

	if 'email' in session:
		return redirect(url_for('profile'))

	if request.method == 'POST':
		if form.validate(email) == False:
			return render_template('signin.html', form=form)
		else:
			session['email'] = form.email.data
			return redirect(url_for('profile'))

	# GET requests
	return redirect(url_for('login1'))


@app.route('/profile')
def profile():

	if 'email' not in session:
		return redirect(url_for('login1'))

	user = User_1.query.filter_by(email = session['email']).first()

	if user is None:
		return redirect(url_for('login1'))
	else:
		return render_template('profile.html')

@app.route('/signout')
def signout():

	if 'email' not in session:
		return redirect(url_for('login1'))

	session.pop('email', None)
	return redirect(url_for('home'))

@app.errorhandler(404)
def internal_error(exception):
	# app.logger.exception(exception)
	return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('500.html'), 500
=======
from models import User, User_Profile, set_pass
from models import get_user_record, set_user_record

# Dropbox Connectors
from dropbox_conn import dropbox_connect

# Google Drive Connectors
from gdrive_conn import gdrive_connect

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
		try:
			if request.method == 'POST':

				# Get form data
				print "Inside signup()"

				# Get form data
				email = cgi.escape(request.form['Email'], True).lower()
				password1 = request.form['Password1']
				password2 = request.form['Password2']
				passphrase1 = request.form['Passphrase1']
				passphrase2 = request.form['Passphrase2']
				fn = request.files['PB_Key']

				# DEBUG
				print "email: ", str(email)
				print "password1: ", str(password1)
				print "password2: ", str(password2)
				print "passphrase1: ", str(passphrase1)
				print "passphrase2: ", str(passphrase2)
				print "filename = ", str(fn.filename)
				# print "filesize = ", os.path.getsize(fn.filename)

				# if form.verify(email):	# Email exists in records
				# 	flash('That email is already registered!')	
				# 	print "That email is already registered"
				# 	return render_template('signup.html')

				if len(password1) < 5: # Password lenght test
					flash('Password must have minimum 5 characters!')	
					print "Password must have minimum 5 characters!"
					return render_template('signup.html')

				if len(passphrase1) < 8: # Passphrase lenght test
					flash('Passphrase must have minimum 5 characters!')	
					print "Passphrase must have minimum 5 characters!"
					return render_template('signup.html')

				if (password1 != password2): # Password match test
					flash('Passwords do not match')	
					print "Passwords do not match"
					return render_template('signup.html')

				if (passphrase1 != passphrase2): # Passphrase match test
					flash('Passwords do not match')	
					print "Passwords do not match"
					return render_template('signup.html')

				# Validates extension of file uploaded; Prompt error if invalid public key
				if not (fn.filename).endswith('.pub'):
					flash("Invalid public key. Please upload proper public key")
					print "Invalid public key. Please upload proper public key"
					return render_template('signup.html')
	
				# Delete if the above works

				# if os.stat(fn.filename).st_size == 0:
				# 	print "empty pub key file"
				# 	flash("Invalid public key. Please upload proper public key")
				# 	return render_template('signup.html')				

				else:
					pwd_hash = set_pass(password1)
					print "pwd_hash = ", str(pwd_hash)
					passphrase_hash = set_pass(passphrase1)
					print "passphrase_hash = ", str(passphrase_hash)

					# Strip leading path from file: attack prevention
					# pb_key = os.path.basename(fn.filename)

					# Read public key file contents
					# with open(fn) as f:
					pub_key = fn.read()
					
					print "Uploaded pub key: ", pub_key
					
					# Add entry into the DB
					set_user_record(email, pwd_hash, passphrase_hash, pub_key)
					flash('New account created successfully!')
					return redirect(url_for('login'))

			# GET Requests
			print "GET Signup"
			return render_template('signup.html')

		except OSError:
		# except Exception, e:
			# May be caused by 'os.stat(fn).st_size'
			print "Woah horsey! You broke something!:  OSError"
			print str(e)
			flash("Signup Error")
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
			if user_info is not None:
				#print "user_info = ", user_info
				#gd_email = user_info["email"]
				#print "gd_email = ", type(gd_email)
				gd_email = "hell0"

			return render_template('profile.html', user=session['user'], db_conn=real_name, gd_conn=gd_email)


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
>>>>>>> ross_v3
