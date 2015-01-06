from login import db
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, String, ForeignKey, BLOB
from sqlalchemy.orm import relationship, backref


# Sets salted hash of the password
def set_pass(password):
	return generate_password_hash(password)

def check_pass(pass_1, pass_2):
	return check_password_hash(pass_1, pass_2)

# # Sets the access tokens for the services in the DB
# def set_token(self, email, service, access_token):


# 	if service.lower() == 'dropbox':
# 		# Add to column dropbox
# 		return True
	
# 	if service.lower() == 'gdrive':
# 		# Add to column gdrive
# 		return True
	
# 	else:
# 		return False

# # Returns the access tokens for the services in the DB
# def get_token(self, email, service):

# 	if service.lower() == 'dropbox':
# 		# return dropbox token	

	
# 	if service.lower() == 'gdrive':
# 		# return gdrive token

# 	return None

# Table 1 (Email + password)
class User_1(db.Model):

	# Setting the table name
	__tablename__ = 'Login_1'

	email 	= 	Column('email', String(120), primary_key=True, unique=True)
	password = 	Column('password', String(100))

	# Defining One-One relationship with Login_2
	child_1 = relationship("User_2", backref=backref('Login_1',  uselist=False))
	child_2 = relationship("User_Profile", backref=backref('Login_1',  uselist=False))

	def __init__(self, email, pwdhash):
		self.email = email.lower()
		self.password = pwdhash

	# def __repr__(self):
	# 	return '<User %r>' % self.email


# Table 2 (Email + passphrase)
class User_2(db.Model):

	# Setting the table name
	__tablename__ = 'Login_2'

	email 		=	Column('email', String(120), ForeignKey('Login_1.email'), primary_key=True, unique=True)
	passphrase 	= 	Column('passphrase', String(100))

	def __init__(self, email, passphrase_hash):
		# Create object from Login
		
		self.email = email.lower()
		self.passphrase = passphrase_hash

	def get_id(self):
		# For Flask-Login
		#return self.email
		return unicode(self.email)		

	def is_authenticated(self):
		# Return True if user is authenticated
		return True

	def is_active(self):
		# True, as all users are active
		return True

	def is_anonymous(self):
		# Anonymous users are not supported
		return False

# Table 3 - Email + various Access Tokens
class User_Profile(db.Model):

	# Setting the table name
	__tablename__ = 'Profile'

	email =	Column('email', String(120), ForeignKey('Login_1.email'), primary_key=True, unique=True)
	dropbox = Column(BLOB)
	gdrive = Column(BLOB)

	def __init__(self, email):
		self.email = email.lower()








