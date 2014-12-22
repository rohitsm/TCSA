
# Flask
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Required, Email

# Models
from login import db
from models import Login_1, Login_2


# Stage 1
class LoginForm_1(Form):

	email = TextField('Email Address', [Email("Please enter your email address"), Required(message='Forgot your email address?')])
	password = PasswordField('Password', [Required(message='Must provide a password!')])
	submit = SubmitField("Proceed")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False

		email = Login_1.query.filter_by(email = self.email.data.lower()).first()
		if email:
			# check password
			if password:
				return True

		return self.email.errors.append("Incorrect email or password")


# Stage 2
class LoginForm_2(Form):

	passphrase = PasswordField('Passphrase', [Required(message='Must provide a passphrase!')])
	submit = SubmitField("Sign In")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self, email):
		if not Form.validate(self):
			return False

		email = Login_1.query.filter_by(email = self.email.data.lower()).first()
		# validate passphrase here! 
		if passphrase:
			# check password
			if password:
				return True

		return self.email.errors.append("Incorrect passphrase")
