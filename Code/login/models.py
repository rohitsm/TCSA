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

	def __init__(self, email, password):
		self.email = email.lower()
		self.password = set_pass(password)
	

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
