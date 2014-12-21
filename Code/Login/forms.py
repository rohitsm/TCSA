from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Required, Email

class LoginForm(Form):
	email = TextField('Email Address', [Email(), Required(message='Forgot your email address?')])
	password = PasswordField('Password', [Required(message='Must provide a password')])
	remember_me = BooleanField('Remember Me', default=False)