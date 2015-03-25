from login import db
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, String, ForeignKey, BLOB
from sqlalchemy.orm import relationship, backref

# One Time Password and QR code related
import pyotp
import time
import qrcode
from PIL import Image

# Sets salted hash of the password
def hash_pass(password):
	return generate_password_hash(password)

def check_pass(pass_1, pass_2):
	return check_password_hash(pass_1, pass_2)


# One Time Password (OTP) related handlers

def generate_otp(email):
	"""
	Generates a user specific random Base32Key and related QR code data
	for use with Google Authenticator.

	Args: 
		email: New user email to include in TOTP provisioning URI
	Returns:
		otp_key: 	Unique user specific 16 character base32 secret 
						that is compatible with Google Authenticator
		qrcode_data: 	Data for generating user specific QR code
	"""
	print "generate_otp"
	otp_key = pyotp.random_base32()
	totp = pyotp.TOTP(otp_key)

	# Data for generating user specific QR code
	qrcode_data = totp.provisioning_uri(email)
	print "otp_key = ", otp_key
	print "qrcode_data = ", qrcode_data

	return (otp_key, qrcode_data)

def get_otp_key(email):
	print "get_otp_key"
	user = get_user_record(email)
	print "user.otp_key = ", user.otp_key
	return user.otp_key

def set_otp_key(email, new_otp_key):
	print "set_otp_key"
	user = get_user_record(email)
	user.otp_key = new_otp_key
	db.session.commit()
	return True

def check_otp(email, otp_code):
	"""
		Verifies the client OTP against the server OTP
	"""
	print "Inside check_otp"
	otp_key = get_otp_key(email)
	totp = pyotp.TOTP(otp_key)

	print "otp_code = ", otp_code
	print "otp_key = ", otp_key

	if (str(otp_code) == str(totp.now()) ):
		return True
	return False

# Account settings handlers
def set_password(email, new_pwd):
	user = get_user_record(email)
	user.password = new_pwd
	db.session.commit()
	return True

def set_pbkey(email, new_pbkey):
	user = get_user_record(email)
	user.pub_key = new_pbkey
	db.session.commit()
	return True

def get_pb_key(email):
	user = get_user_record(email)
	return user.pub_key


# User record handlers
def get_user_record(email):
	# Get user object from database
	user = User.query.filter_by(email = email).first()
	print "inside get_user_record: "
	return user

def set_user_record(email, password, otp_key, pub_key):
	# Set user object in database
	user = User(email, password, otp_key, pub_key)
	profile = User_Profile(email)

	# Maintaining foreign key dependency
	user.child.append(profile)

	db.session.add(user)
	db.session.commit()
	print "inside set_user_record: "

# Access token handlers
def get_token(email, service):
	# Get access token for service from db
	access_token = None
	record = User_Profile.query.filter_by(email=email).first()

	if service.lower() == 'dropbox':
		access_token = record.dropbox

	elif service.lower() == 'gdrive':
		access_token = record.gdrive

	#print "inside get_token: ", access_token
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

# External Wrappers for Tokens
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

# Table (Email + password + otp_key + pub_key)
class User(db.Model):
	# Setting the table name
	__tablename__ = 'Login'

	email = Column('email', String(120), primary_key=True)
	password = Column('password', String(120))
	otp_key = Column('otp_key', String(120))
	pub_key = Column('pub_key', BLOB)

	# Describing One-One relationship with Profile
	child = relationship("User_Profile", backref=backref('Login', uselist=False))

	def __init__(self, email, pwdhash, otp_key, pub_key):
		self.email = email.lower()
		self.password = pwdhash
		self.otp_key = otp_key
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

