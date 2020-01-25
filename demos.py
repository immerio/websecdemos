from flask import Flask, request, redirect, render_template, session
import sqlite3, os

app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'CHANGEME',
    'SESSION_COOKIE_HTTPONLY': False,
})

prod = False

if prod:
	tempdb = "/home/runner/flaskapp/tempdb"
	commentdb = "/home/runner/flaskapp/commentdb"
else:
	tempdb = "tempdb"
	commentdb = "commentdb"

@app.route('/')
def pageFront():
	return render_template('home.html')
	
# # # #
# Problem: Default credentials
# Use "Administrator" and "admin" to get in

@app.route('/brokenauth1')
def pageBrokenauth1():
	return render_template('login.html', page='brokenauth1')

@app.route('/brokenauth1', methods = ['POST'])
def pageBrokenauth1Post():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'Administrator' and password == 'admin':
		return render_template('inside.html', admin=True)
	else:
		return render_template('login.html', page='brokenauth1', incorrect=True)

# # # #
# Problem: Common credentials
# Use "Administrator" as username and find the "1qaz2wsx" password with a bruteforce attack

@app.route('/brokenauth2')
def pageBrokenauth2():
	return render_template('login.html', page='brokenauth2')

@app.route('/brokenauth2', methods = ['POST'])
def pageBrokenauth2Post():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'Administrator' and password == '1qaz2wsx':
		return render_template('inside.html', admin=True)
	else:
		return render_template('login.html', page='brokenauth2', incorrect=True)

# # # #
# Problem: Displaying error message
# Use the information in the error message - /secmis/admin to get to the admin panel

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
	return render_template('inside.html', admin=True)

# # # #
# Problem: SQL Injection
# Use an SQL Injection .. Ex: ' OR 1=1 --

@app.route('/inject')
def pageInjection():
	return render_template('login.html', page='inject')

@app.route('/inject', methods = ['POST'])
def pageInjectPost():
	username = request.form['username']
	password = request.form['password']
	
	conn = sqlite3.connect(tempdb)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS users("username" TEXT, "password" TEXT)')
	c.execute('INSERT OR IGNORE INTO users VALUES ("admin", "bacon7")')
	conn.commit()
	sql = '''SELECT username FROM users WHERE username = '%s' and password = '%s' ''' % (username, password)
	c.execute(sql)
	result = c.fetchone()
	c.execute('DROP TABLE users')
	conn.commit()
	c.close()
	if result is not None:
		return render_template('inside.html', admin=True)
	else:
		return render_template('login.html', page='inject', incorrect=True, sqlline=sql)

# # # #
# Problem: Broken Access Control
# Change the userid logged in via the URL

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
		return render_template('login.html', page='brokenauth2', incorrect=True)
		
# # # #
# Problem: Unencrypted sensitive data in cookies
# Found out secret key and then send loggedin = true to the server

@app.route('/cookies')
def pageCookies():
	session['loggedin'] = "False"
	return render_template('login.html', page='cookies')

@app.route('/cookies', methods = ['POST'])
def pageCookiesPost():

	if session['loggedin'] == "True":
		return render_template('inside.html', admin=True)
	else:
		return render_template('login.html', page='brokenauth2', incorrect=True)
		
@app.route('/brokenaccess/loggedin/user/<userid>')
def pageBrokenaccessLoggedin(userid):
	if userid == "0":
		return render_template('inside.html', admin=True)
	elif userid == "6510":
		return render_template('inside.html', admin=False)
	else:
		return render_template('minimal.html', page='brokenaccess', content='Error: Incorrect user')
		
@app.route('/xss')
def pageXss():
	conn = sqlite3.connect(commentdb)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	conn.commit()
	sql = '''SELECT comment,name FROM comments'''
	c.execute(sql)
	result = c.fetchall()
	c.close()
	return render_template('feedback.html')
	
@app.route('/xss', methods = ['POST'])
def pageXssPost():	
	comment = request.form['comment']
	name = request.form['name']
	
	conn = sqlite3.connect(commentdb)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', (comment,name))
	conn.commit()
	c.close()
	return render_template('feedback.html', sent=True)	
	
@app.route('/xssvictim')
def pageXssvictim():
	if session.get('loggedin') != "True":
		return render_template('feedbacklogin.html', page='xssvictim', incorrect=True)
	else:
		conn = sqlite3.connect(commentdb)
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
		conn.commit()
		sql = '''SELECT comment,name FROM comments'''
		c.execute(sql)
		result = c.fetchall()
		c.close()
		return render_template('feedbackadmin.html', dbresult=result)
		
@app.route('/brokensession')
def pageBrokensession():
	if session.get('loggedin') != "True":
		session['loggedin'] = "False"
		return render_template('login.html', page='brokensession')
	else:
		return render_template('inside.html', admin=True)

@app.route('/xssvictim/removefeedback')
def pageXssvictimRemovefeedback():
	if session.get('loggedin') != "True":
		return render_template('feedbacklogin.html', page='xssvictim', incorrect=True)
	else:
		conn = sqlite3.connect(commentdb)
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
		sql = '''DELETE FROM comments'''
		c.execute(sql)
		conn.commit()
		c.close()
		return redirect(request.url_root + "xssvictim", code=302)
	
@app.route('/xssvictim/removecookie')
def pageXssvictimRemovecookie():
	if session.get('loggedin'):
		session.pop('loggedin', None)	
		return "ok"
	else:
		return "didnt find the cookie"
		
@app.route('/xssvictim', methods = ['POST'])
def pageXssvictimPost():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'Administrator' and password == 'admin':
		session['loggedin'] = "True"
		return redirect(request.url_root + "xssvictim", code=302)
	else:
		return render_template('feedbacklogin.html', page='xssvictim', incorrect=True)
			

@app.route('/evilimage')
def pageEvilimage():
	cookies = request.args.get('get')
	if not cookies:
		return "Incorrect attributes"
	conn = sqlite3.connect(tempdb)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	c.execute('''DELETE FROM evilimage''')
	c.execute('''INSERT OR IGNORE INTO evilimage(data) VALUES (?)''', (cookies,))
	conn.commit()
	c.close()
	return "Couldnt display image"
	
@app.route('/evillog')
def pageEvillog():
	conn = sqlite3.connect(tempdb)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	conn.commit()
	c.execute('''SELECT data FROM evilimage''')
	
	result = c.fetchone()
	c.close()
	if result:
		return str(result[0])
	else:
		return "No data"

if __name__ == "__main__":
	if prod:
		app.run()
		
if not prod:
	app.run(host='0.0.0.0', port=8080)
