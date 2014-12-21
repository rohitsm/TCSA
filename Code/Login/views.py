
# Flask
from flask import render_template, flash, redirect 
from login import app
from .forms import LoginForm


@app.route('/')
def index():
	return "hello"

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		flash('Login requested for Email="%s", remember_me="%s"' % (form.email.data))
		return redirect('/index')

	return render_template('login.html', 
							# title='Sign In', 
							form=form,
							providers=app.config['OPENID_PROVIDERS'])

