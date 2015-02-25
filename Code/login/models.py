from login import db
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, String, ForeignKey, BLOB
from sqlalchemy.orm import relationship, backref


# Sets salted hash of the password
def set_pass(password):
	return generate_password_hash(password)

def check_pass(pass_1, pass_2):
	return check_password_hash(pass_1, pass_2)

# Account settings handlers
def update_password(email, new_pwd):
	user = User.query.filter_by(email = email).first()
	user.password = new_pwd
	db.session.commit()
	return True

def update_pbkey(email, new_pbkey):
	user = User.query.filter_by(email = email).first()
	user.pub_key = new_pbkey
	db.session.commit()
	return True

# User record handlers
def get_user_record(email):
	# Get user object from database
	user = User.query.filter_by(email = email).first()
	print "inside get_user_record: "
	return user

def set_user_record(email, password, passphrase, pub_key):
	# Set user object in database
	user = User(email, password, passphrase, pub_key)
	profile = User_Profile(email)

	# Maintaining foreign key dependency
	user.child.append(profile)

	db.session.add(user)
	db.session.commit()
	print "inside set_user_record: "

def update_password(email, new_pwd):
	user = User.query.filter_by(email = email).first()
	user.password = new_pwd
	db.session.commit()
	return True

# Access token handlers
def get_token(email, service):
	# Get access token for service from db
	access_token = None
	record = User_Profile.query.filter_by(email=email).first()

	if service.lower() == 'dropbox':
		access_token = record.dropbox

	elif service.lower() == 'gdrive':
		access_token = record.gdrive

	print "inside get_token: ", access_token
	return access_token

def set_token(email, service, access_token):
	# Sets the access tokens for the services in the DB
	record = User_Profile.query.filter_by(email=email).first()

	if service.lower() == 'dropbox':
		record.dropbox =  access_token
		db.session.commit()
		print "inside set_token: (DROPBOX)"
		return True
	
	elif service.lower() == 'gdrive':
		record.gdrive = access_token
		db.session.commit()
		print "inside set_token: (GDRIVE)"
		return True
	
	return False

# External Wrappers
def get_dropbox_token(email):
	db_token = get_token(str(email), 'dropbox')
	print "inside get_dropbox_token: ", db_token
	return db_token

def set_dropbox_token(email, access_token):
	if set_token(str(email), 'dropbox', access_token):
		print "inside set_dropbox_token: "
		return True
	return False

def get_gdrive_token(email):
	"""Returns Google OAuth credentials as a JSON element"""
	gd_token = get_token(str(email), 'gdrive')
	print "inside get_gdrive_token: ", type(gd_token)	#type = <str>
	return gd_token

def set_gdrive_token(email, access_token):
	if set_token(str(email), 'gdrive', access_token):
		print "inside set_gdrive_token: ", type(access_token)
		return True
	return False

# Table (Email + password + passphrase)
class User(db.Model):
	# Setting the table name
	__tablename__ = 'Login'

	email = Column('email', String(120), primary_key=True)
	password = Column('password', String(120))
	passphrase = Column('passphrase', String(120))
	pub_key = Column('pub_key', BLOB)

	# Describing One-One relationship with Profile
	child = relationship("User_Profile", backref=backref('Login', uselist=False))

	def __init__(self, email, pwdhash, ppshash, pub_key):
		self.email = email.lower()
		self.password = pwdhash
		self.passphrase = ppshash
		self.pub_key = pub_key

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

	email =	Column('email', String(120), ForeignKey('Login.email'), primary_key=True)
	dropbox = Column(BLOB)
	gdrive = Column(BLOB)

	def __init__(self, email):
		self.email = email.lower()

