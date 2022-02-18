from flask import Blueprint, request, render_template, session

app = Blueprint('brokensession',__name__)
@app.route('/brokensession')
def pageBrokensession():
	if session.get('loggedin') != "True":
		session['loggedin'] = "False"
		return render_template('login.html', page='brokensession')
	else:
		return render_template('inside.html', admin=True, page='brokensession')