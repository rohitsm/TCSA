
# Flask
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Required, Email

# Models
from login import db
from models import User_1, User_2, check_pass

# Stage 0
class SignupForm(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def verify(self, email):
		print "Inside SignupForm.veriyu(), Email = ", email
		user = User_1.query.filter_by(email = email).first()
		if user:
			#Email already exists in records
			return True
		else:
			return False

	def add_entry(self, email, pwdhash, passphrase_hash):
		print "inside add_entry"
		entry_1 = User_1(email, pwdhash)
		entry_2 = User_2(email, passphrase_hash)
		print "entry_1", entry_1
		print "entry_2", entry_2
		
		entry_1.child.append(entry_2)

		db.session.append(entry_1)
		db.session.commit()

# Stage 1
class LoginForm_1(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def verify(self, eml, pwdhash):
		# Checks if email and password match in records
		print "inside LoginForm_1.verify()"
		user = User_1.query.filter_by(email = eml).first()
		if user.check_pass(user.password, pwdhash):
			return True
		else:			
			return False

# Stage 2
class LoginForm_2(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	# Takes email ID as argument
	def verify(self, eml, pp_hash):
		# Checks if email and passphrase match in records		
		user = User_2.query.filter_by(email = eml).first()
		if user.check_pass(user.passphrase, pp_hash):
			return True
		else:
			return False

