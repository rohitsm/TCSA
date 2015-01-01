from login import db
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, String, ForeignKey


# Sets salted hash of the password
def set_pass(password):
	return generate_password_hash(password)

def check_pass(password):
	return check_password_hash(pass_1, pass_2)

# Table 1
class User_1(db.Model):

	# Setting the table name
	__tablename__ = 'Login_1'

	email 	= 	db.Column('email', db.String(120), primary_key=True, unique=True)
	password = 	db.Column('password', db.String(100))

	# Defining One-One relationship with Login_2
	child = relationship("User_2", uselist=False, backref='Login_1')

	def __init__(self, email, password):
		self.email = email.lower()
		self.password = set_pass(password)

	def __repr__(self):
		return <'User %r>' % self.email


# Table 2
class User_2(db.Model):

	# Setting the table name
	__tablename__ = 'Login_2'

	email 		=	db.Column('email', db.String(120), ForeignKey('User_1.email'), primary_key=True, unique=True)
	passphrase 	= 	db.Column('passphrase', db.String(100))

	def __init__(self, email, passphrase):
		# Create object from Login
		
		self.email = email.lower()
		self.passphrase = set_pass(passphrase)

	def get_id(self):
		# For Flask-Login
		return self.email
		# return unicode(self.email)		--->Check functionality

	def is_authenticated(self):
		# Return True if user is authenticated
		return True

	def is_active(self):
		# True, as all users are active
		return True

	def is_anonymous(self):
		# Anonymous users are not supported
		return False

