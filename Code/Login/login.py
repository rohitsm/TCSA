
# Flask
from flask import Flask
app = Flask(__name__, static_url_path = '/static')
from flask import render_template
from flask import request, redirect, url_for


@app.route('/')
def login():
	""" Return the login page """
	return render_template('login.html')

# @app.route('/loginAuth', methods = ['GET'])
# def authentication():

# 	# if request.method == 'POST':
# 	# 	try:

# 	# For GET requests
# 	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run()





