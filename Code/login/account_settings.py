# User Account settings. 
# 	- Reset Password
# 	- Reset Public key

# Flask
from flask import render_template, flash, redirect, request, url_for
from flask import session, abort

# App
from login import app
from login import login_manager 

# DB
from login import 

@app.route('/changepwd', methods=['GET', 'POST'])
def change_password():
	form = LoginForm_1()
	print "inside change_password"

	if 'user' not in session:
		return redirect(url_for('login'))

	if request.method == 'POST':
		email = session.get('user')
		old_password = request.form['old_password']
		new_password1 = request.form['new_password1']
		new_password2 = request.form['new_password2']

		# DEBUG

		print "email: ", email
		print "old_password: ", old_password
		print "new_password1: ", new_password1
		print "new_password2: ", new_password2

		# Check if email/pwd exists in DB records
		user = get_user_record(email)
		if user:
			if not form.authenticate(email, old_password):
				print "form verify = false"
				# Invalid login. Return error
				flash("User doesn't exit in records")
				return redirect(url_for('login'))
			
			# Success
			else:
				if len(new_password1) < 5: # Password length test
					flash('Password must have minimum 5 characters!')	
					print "Password must have minimum 5 characters!"
					return render_template('changepwd.html')

				if (new_password1 != new_password2): # Password match test
					flash('Passwords do not match')
					print "Passwords do not match"
					return render_template('changepwd.html')

				else:
					# If authentication is okay, hash the password and replace the
					# old password with the new one
					pwd_hash = set_pass(new_password1)

					# Replace the pwd in DB
					








