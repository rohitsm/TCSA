
# Flask
from flask import render_template, flash, redirect, request, url_for
from login import app
from forms import LoginForm_1, LoginForm_2
from models import User_1, User_2
from flask import session

# DB
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


@app.route('/login1', methods=['GET', 'POST'])
def login1():

	form = LoginForm_1()

	if 'email' in session:
		return redirect(url_for('profile'))

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', form=form)
		
		else:
			session['email'] = form.email.data
			
			user = User_1(form.email.data)
			return redirect(url_for('login2'))

	# GET request
	return render_template('signin.html', form=form)


@app.route('/login2', methods=['GET', 'POST'])
def login2():

	form = LoginForm_2()

	if 'email' in session:
		return redirect(url_for('profile'))

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', form=form)
		else:
			return "Success"

	# GET requests
	return render_template('signin.html', form=form)


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



