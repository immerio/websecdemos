from flask import Blueprint, request, render_template

app = Blueprint('brokenaccess',__name__)
@app.route('/brokenaccess')
def pageBrokenaccess():
	return render_template('login.html', page='brokenaccess')

@app.route('/brokenaccess', methods = ['POST'])
def pageBrokenaccessPost():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'user' and password == 'user':
		return redirect("/brokenaccess/loggedin/user/6510", code=302)
	else:
		return render_template('login.html', page='brokenaccess', incorrect=True)
        
@app.route('/brokenaccess/loggedin/user/<userid>')
def pageBrokenaccessLoggedin(userid):
	if userid == "0":
		return render_template('inside.html', admin=True, page='brokenaccess')
	elif userid == "6510":
		return render_template('inside.html', admin=False, page='brokenaccess')
	else:
		return render_template('servererror.html', page='brokenaccess', incorrectuser='Incorrect user')
