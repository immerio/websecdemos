from flask import Blueprint, request, render_template

app = Blueprint('brokenauth1',__name__)
@app.route("/brokenauth1")
def pageBrokenauth1():
    return render_template('login.html', page='brokenauth1')

@app.route("/brokenauth1", methods = ['POST'])
def pageBrokenauth1Post():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'Administrator' and password == 'admin':
		return render_template('inside.html', admin=True, page='brokenauth1')
	else:
		return render_template('login.html', page='brokenauth1', incorrect=True, username=username, password=password)