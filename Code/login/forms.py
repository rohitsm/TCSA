
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
		user = User_1.query.filter_by(email = eml).first()
		if user:
			self.email.errors.append("That email is already taken")
			return False
		else:
			return True

	def add_entry(self, email, pwdhash, passphrase_hash):
		entry_1 = User_1(email, pwdhash)
		entry_2 = User_2(email, passphrase_hash)
		entry_1.child.append(entry_2)

		db.session.append(entry_1)
		db.session.commit()


# Stage 1
class LoginForm_1(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def verify(self, eml, pwdhash):
		print "inside LoginForm_1.verify()"

		user = User_1.query.filter_by(email = eml).first()
		if user and user.check_pass(user.password, pwdhash):
			return True
		else:
			self.email.errors.append("Invalid email or password")
			return False


# Stage 2
class LoginForm_2(Form):

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	# Takes email ID as argument
	def verify(self, eml, pp_hash):
		
		user = User_2.query.filter_by(email = eml).first()
		if user and user.check_pass(user.passphrase, pp_hash):
			return True
		else:
			self.email.errors.append("Incorrect passphrase")
			return False

