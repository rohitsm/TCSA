
# Flask
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Required, Email

# Models
from login import db
<<<<<<< HEAD
from models import User_1, User_2
=======
from models import get_user_record, set_user_record, check_pass
>>>>>>> ross_v3

# Stage 0
class SignupForm(Form):
	email = TextField('Email Address', [Email("Please enter your email address"), Required(message='Forgot your email address?')])
	password = PasswordField('Password', [Required(message='Must provide a password!')])
	passphrase = PasswordField('Passphrase', [Required(message='Must provide a passphrase!')])
	submit = SubmitField('Create account')

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

<<<<<<< HEAD
	def validate(self):
		if not Form.validate(self):
			return False

		user = User_1.query.filter_by(email = self.email.data.lower()).first()
=======
	def verify(self, email):	
		user = get_user_record(email)	
>>>>>>> ross_v3
		if user:
			self.email.errors.append("That email is already taken")
			return False
		
		# if len(password) < 6:
		# 	self.password.errors.append("Password too short! Must length must 6 chars.")
		# 	return False
		
		# if len(passphrase) < 12:
		# 	self.passphrase.errors.append("Passphrases must be atleast 12 characters long!")
		# 	return False

		else:
			return True

# Stage 1
class LoginForm_1(Form):

	email = TextField('Email Address', [Email("Please enter your email address"), Required(message='Forgot your email address?')])
	password = PasswordField('Password', [Required(message='Must provide a password!')])
	submit = SubmitField("Proceed")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

<<<<<<< HEAD
	def validate(self):
		if not Form.validate(self):
			return False

		user = User_1.query.filter_by(email = self.email.data.lower()).first()
		if user and user.check_password(self.password.data):
=======
	def authenticate(self, eml, pwd):
		# Checks if email and password match in records
		user = get_user_record(eml)
		if check_pass(user.password, pwd):
>>>>>>> ross_v3
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

<<<<<<< HEAD
	# Takes email ID as argument
	def validate(self, eml):
		if not Form.validate(self):
			return False

		user = User_2.query.filter_by(email = eml.lower()).first()
		if user and user.check_passphrase(self.passphrase.data):
=======
	def authenticate(self, eml, passph):
		# Checks if email and passphrase match in records		
		user = get_user_record(eml)
		if check_pass(user.passphrase, passph):
>>>>>>> ross_v3
			return True
		else:
			self.email.errors.append("Incorrect passphrase")
			return False




