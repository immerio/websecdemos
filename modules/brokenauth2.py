from flask import Blueprint, request, render_template

app = Blueprint('brokenauth2',__name__)
@app.route('/brokenauth2')
def pageBrokenauth2():
	return render_template('login.html', page='brokenauth2')

@app.route('/brokenauth2', methods = ['POST'])
def pageBrokenauth2Post():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'Administrator' and password == '1qaz2wsx':
		return render_template('inside.html', admin=True, page='brokenauth2')
	else:
		return render_template('login.html', page='brokenauth2', incorrect=True)
