# Used for data validation

class Validator():
	def validateEmail(self, email):
		atpos = email.find('@')
		dotpos = email.rfind('.')
		if ((atpos < 1) or (dotpos < atpos+2) or (dotpos+2 >=len(email)) ):
			return False
		return True

	def allowed_file(self, filename):
		ALLOWED_EXTENSIONS = set(['pub'])
		return '.' in filename and \
				filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# USAGE

# from validator import Validator
# vd = Validator()

# Example: 
# a = Validator()
# print a.allowed_file('hello.pu')

