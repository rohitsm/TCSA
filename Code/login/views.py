# Python
import cgi

# Flask
from flask import render_template, flash, redirect, request, url_for
from forms import SignupForm 
#from forms import LoginForm_1, LoginForm_2
from flask import session
from werkzeug.security import generate_password_hash #, check_password_hash

# App
from login import app

# DB
from models import User_1, User_2
from login import db

@app.route('/')
def index():
	return "hello"

@app.route('/home')
def home():
	return render_template('layout.html')


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
			#print "Dies here"
			#return redirect(url_for('index'))

		else:
			print "form valid"
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
	print "form type = ", type(form)
	return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def login1():

	if 'email' in session:
		print "breaks here 1"
		return redirect(url_for('profile'))
	
	if request.method == 'POST':
		email = cgi.escape(request.form['Email'], True).lower()
		pwdhash = generate_password_hash(request.form['Password'])
		

		# Verify 1st stage of login using email + pwdhash
		if form.validate(email, pwdhash) == False:
			return render_template('signin.html')

		else:
			# Pass email to second stage of login
			session['email'] = email
			return redirect(url_for('login2'))

	# GET request:
	return render_template('signin.html')


# @app.route('/login2', methods=['GET', 'POST'])
# def login2():

# 	form = LoginForm_2()

# 	if 'email' in session:
# 		return redirect(url_for('profile'))

# 	if request.method == 'POST':
# 		if form.validate(email) == False:
# 			return render_template('signin.html', form=form)
# 		else:
# 			session['email'] = form.email.data
# 			return redirect(url_for('profile'))

# 	# GET requests
# 	return render_template('signin.html', form=form)


# @app.route('/profile')
# def profile():

# 	if 'email' not in session:
# 		return redirect(url_for('login1'))

# 	user = User_1.query.filter_by(email = session['email']).first()

# 	if user is None:
# 		return redirect(url_for('login1'))
# 	else:
# 		return render_template('profile.html')

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
