
# Flask
from flask.ext.wtf import Form
from flask import session

# Models
from login import db
from models import get_user_record, set_user_record, check_pass

# Stage 0
class SignupForm(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def verify(self, email):	
		user = get_user_record(email)	
		if user:
			#Email already exists in records
			return True
		else:
			return False

# Stage 1
class LoginForm_1(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def authenticate(self, eml, pwd):
		# Checks if email and password match in records
		user = get_user_record(eml)
		if check_pass(user.password, pwd):
			return True
		else:
			return False

# Stage 2
class LoginForm_2(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def authenticate(self, eml, passph):
		# Checks if email and passphrase match in records		
		user = get_user_record(eml)
		if check_pass(user.passphrase, passph):
			return True
		else:
			return False




