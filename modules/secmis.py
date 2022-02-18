from flask import Blueprint, request, render_template

app = Blueprint('secmis',__name__)
@app.route('/secmis')
def pageSecmis():
	return render_template('login.html', page='secmis')

@app.route('/secmis', methods = ['POST'])
def pageSecmisPost():
	username = request.form['username']
	password = request.form['password']
	
	if "'" in username or "'" in password:
		#return page(errorstring)
		return render_template('servererror.html')
	else:
		return render_template('login.html', page='secmis', incorrect=True)

@app.route('/secmis/admin')
def pageSecmisAdmin():
	return render_template('inside.html', admin=True, page='secmis')
	
@app.route('/secmis/admin/')
def pageSecmisAdmin2():
	return render_template('inside.html', admin=True, page='secmis')	