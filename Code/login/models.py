from login import db
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, String, ForeignKey, BLOB
from sqlalchemy.orm import relationship, backref


# Sets salted hash of the password
def set_pass(password):
	return generate_password_hash(password)

def check_pass(pass_1, pass_2):
	return check_password_hash(pass_1, pass_2)

def get_user(email):
	# Get user record from database
	user = User.query.filter_by(email = email).first()
	return user

def set_user(email, pwdhash, ppshash):
	# Insert user record into database
	user = User(email, password, passphrase)
	db.session.add(user)
	db.session.commit()



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

# Table (Email + password + passphrase)
class User(db.Model):
	# Setting the table name
	__tablename__ = 'Login'

	email = Column('email', String(120), primary_key=True)
	password = Column('password', String(120))
	passphrase = Column('password', String(120))

	def __init__(self, email, pwdhash, ppshash):
		self.email = email.lower()
		self.password = pwdhash
		self.passphrase = ppshash

	# Flask-Login function definitions

	def get_id(self):
		# for Flask-Login
		return unicode(self.email)

	def is_authenticated(self):
		# Return true if user is authenticated
		return True

	def is_active(self):
		# True, as all users are active 
		return True

	def is_anonymous(self):
		# Anonymous users are not supported
		return False

# Table 2 - Email + various Access Tokens
class User_Profile(db.Model):

	# Setting the table name
	__tablename__ = 'Profile'

	email =	Column('email', String(120), ForeignKey('Login_1.email'), primary_key=True, unique=True)
	dropbox = Column(BLOB)
	gdrive = Column(BLOB)

	def __init__(self, email):
		self.email = email.lower()








