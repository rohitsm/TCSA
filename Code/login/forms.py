
# Flask
from flask.ext.wtf import Form
from flask import session

# Models
from login import db
from models import User_1, User_2, check_pass

# Stage 0
class SignupForm(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def verify(self, email):		
		user = User_1.query.filter_by(email = email).first()
		if user:
			#Email already exists in records
			return True
		else:
			return False

# Stage 1
class LoginForm_1(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def verify(self, eml, pwd):
		# Checks if email and password match in records
		user = User_1.query.filter_by(email = eml).first()
		if check_pass(user.password, pwd):
			return True
		else:
			return False

# Stage 2
class LoginForm_2(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	# Takes email ID as argument
	def verify(self, eml, passph):
		# Checks if email and passphrase match in records		
		user = User_2.query.filter_by(email = eml).first()
		if check_pass(user.passphrase, passph):
			return True
		else:
			return False

