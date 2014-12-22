from app import db




class User(db.model):

	# Setting the table name
	__tablename__ = 'login1'

	email = db.Column('email', db.String(120), primary_key=True)
	password = db.Column('password', db.String())



class Login1(db.Model):
	email = db.Column(db.String(120),required=True, unique=True, primary_key=True)
	password = db.Column(db.String(64), required=True))
