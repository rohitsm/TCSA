from login import db
from werkzeug import generate_password_hash, check_password_hash


# Table 1
class User_1(db.Model):

	# Setting the table name
	__tablename__ = 'Login_1'

	email = db.Column('email', db.String(120), primary_key=True, unique=True)
	password = db.Column('password', db.String(100))

	def __init__(self, email, password):
		self.email = email.lower()
		self.set_password(password)

	# Sets salted hash of the password
	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

# Table 2
class User_2(db.Model):

	# Setting the table name
	__tablename__ = 'Login_2'

	email = db.Column('email', db.String(120), primary_key=True, unique=True)
	passphrase = db.Column('passphrase', db.String(100))

	def __init__(self, email, passphrase):
		eml = Login_1()
		self.email = eml.email
		self.set_passphrase(passphrase)

	# Sets salted hash of the passphrase
	def set_passphrase(seld, passphrase):
		self.passphrase = generate_password_hash(passphrase)

	def check_passphrase(self, passphrase):
		return check_password_hash(self.passphrase, passphrase)



