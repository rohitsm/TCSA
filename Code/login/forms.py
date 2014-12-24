
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

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self, eml, pwdhash):
		print "inside LoginForm_1.validate()"
		if not Form.validate(self):
			return False

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
	def validate(self, eml, pp_hash):
		if not Form.validate(self):
			return False

		user = User_2.query.filter_by(email = eml).first()
		if user and user.check_pass(user.passphrase, pp_hash):
			return True
		else:
			self.email.errors.append("Incorrect passphrase")
			return False

