# Python
import cgi

# Flask
from flask import render_template, flash, redirect, request, url_for
from forms import SignupForm 
from flask import session

# App
from login import app
from forms import LoginForm_1, LoginForm_2

# DB
from models import User_1, User_2, set_pass
from login import db

@app.route('/')
def index():
	return "hello"

@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "Works"
	else:
		return "Not Working"

# ================ SIGN UP SECTION ====================== #

# @app.route('/signup', methods=['GET', "POST"])
# def signup():
# 	form = SignupForm()

# 	if request.method == 'POST':
# 		if form.validate() == False:
# 			return render_template('signup.html', form=form)
# 			#print "Dies here"
# 			#return redirect(url_for('index'))

# 		else:
# 			print "form valid"
# 			new_user1 = User_1(form.email.data, form.password.data)
# 			new_user2 = User_2(form.email.data, form.passphrase.data)
			
# 			# Insert into DBs
# 			db.session.add(new_user1)
# 			db.session.add(new_user2)
			
# 			# Update the DB by commiting the transaction
# 			db.session.commit()

# 			session['email'] = new_user1.email
# 			return redirect(url_for('profile'))

# 	# GET request
# 	print "form type = ", type(form)
# 	return render_template('signup.html', form=form)


# ============= LOGIN/SIGN IN SECTION =================== #

@app.route('/login', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])
def login():
	return render_template('login.html')


@app.route('/login1', methods=['GET', 'POST'])
def login1():
	form = LoginForm_1()
	print "inside login1"

	# if 'email' in session:
	# 	print "email in session"
	# 	return redirect(url_for('profile'))
	
	if request.method == 'POST':
		print "inside post"
		email = cgi.escape(request.form['Email'], True).lower()
		pwd_hash = set_pass(request.form['Password'])

		print "email: ", str(email)
		print "pwd_hash", str(pwd_hash)

		# Verify 1st stage of login using email + pwd_hash
		if form.validate(email, pwd_hash) != False:
			print "form validate = false"
			return redirect(url_for('login'))

		else:
			# Pass email to second stage of login as arg
			print "to login2 (else)"
			session['email'] = email
			return render_template('login2.html', email=email)
			# return redirect(url_for('login2', email=email))

	# GET request:
	print "GET seen"
	return redirect(url_for('login'))


@app.route('/login2', methods=['GET', 'POST'])
def login2():
	form = LoginForm_2()
	print "inside login2"

	# if 'email' in session:
	# 	return redirect(url_for('profile', email=email))

	if request.method == 'POST':
		email = session['email']
		# email = email
		passphrase_hash = set_pass(request.form['Passphrase'])
		print "email (login2): ", str(email)
		print "passphrase (login2):", str(passphrase_hash)

		# Verify 2nd stage of login using email + passphrase_hash
		if (form.validate(email, passphrase_hash)) != False:
			print "form validate 2 = false"
			return redirect(url_for('login'))

		else:
			print "to profile"
			session['status'] = 'validated'
			return redirect(url_for('profile', email = email))

	# GET requests
	print "GET login2"
	return redirect(url_for('login'))


@app.route('/user')
def profile():
	# print "Email = ", str(email)

	if (session['status'] == 'validated'):
		return "Login Successful!"
	else:
		return "Login unsuccessful"

	# if 'email' not in session:
	# 	return redirect(url_for('login1'))

	# user = User_1.query.filter_by(email = session['email']).first()

	# if user is None:
	# 	return redirect(url_for('login1'))
	# else:
	# 	return render_template('profile.html')

# @app.route('/signout')
# def signout():

# 	if 'email' not in session:
# 		return redirect(url_for('login1'))

# 	session.pop('email', None)
# 	return redirect(url_for('index'))

# @app.errorhandler(404)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(exception):
# 	# app.logger.exception(exception)
# 	return render_template('500.html'), 500
