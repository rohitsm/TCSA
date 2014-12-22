
# Flask
from flask import render_template, flash, redirect, request, url_for
from login import app
from .forms import LoginForm_1, LoginForm_2
from models import Login_1, Login_2
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

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', form=form)
		
		else:
			user = LoginForm_1(form.email.data)
			return redirect(url_for('login2'))

	# GET request
	return render_template('signin.html', form=form)


@app.route('/login2', methods=['GET', 'POST'])
def login2():
	form = LoginForm_2()

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

	user = LoginForm_1




