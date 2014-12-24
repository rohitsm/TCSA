
# Flask
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Required, Email

# Models
from login import db
from models import User_1, User_2, check_pass, set_pass

# Stage 0
class SignupForm(Form):
	# email 	= 	TextField(	'Email Address', [Email("Please enter your email address"),
	# 					 	Required(message='Forgot your email address?')])
	# password = 	PasswordField('Password', [Required(message='Must provide a password!')])
	# re_password = PasswordField('Re-enter Password',[Required(message="Must re-enter password!")])

	# passphrase = PasswordField('Passphrase', [Required(message='Must provide a passphrase!')])
	# re_passphrase = PasswordField('Re-enter Passphrase',[Required(message="Must re-enter passphrase!")])

	# submit = 	SubmitField('Create account')

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False

		user = User_1.query.filter_by(email = self.email.data.lower()).first()
		if user:
			self.email.errors.append("That email is already taken")
			return False

		else:
			return True

# Stage 1
class LoginForm_1(Form):

	# email = TextField('Email Address', [Email("Please enter your email address"), Required(message='Forgot your email address?')])
	# password = PasswordField('Password', [Required(message='Must provide a password!')])
	# submit = SubmitField("Proceed")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self, eml, pwdhash):
		if not Form.validate(self):
			return False

		user = User_1.query.filter_by(email = eml.lower()).first()
		pwd = User_1.query.filter_by()
		if user and user.check_password():
			return True
		else:
			self.email.errors.append("Invalid email or password")
			return False


# Stage 2
class LoginForm_2(Form):

	# em = LoginForm_1()
	
	# self.email = em.email #Get email from LoginForm1
	passphrase = PasswordField('Passphrase', [Required(message='Must provide a passphrase!')])
	submit = SubmitField("Sign In")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	# Takes email ID as argument
	def validate(self, eml):
		if not Form.validate(self):
			return False

		user = User_2.query.filter_by(email = eml.lower()).first()
		if user and user.check_passphrase(self.passphrase.data):
			return True
		else:
			self.email.errors.append("Incorrect passphrase")
			return False

