from flask import Flask, request, redirect, render_template, session, send_file, Markup
import sqlite3, os

app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'CHANGEME',
    'SESSION_COOKIE_HTTPONLY': False,
})

prod = True

if prod:
	#docker
	tempdb = "/home/mrdemo/dbs/tempdb"
	commentdb = "/home/mrdemo/dbs/commentdb"
else:
	tempdb = "tempdb"
	commentdb = "commentdb"


@app.route('/')
def pageFront():
	return render_template('login.html')

@app.route('/help')
def pageHelp():
	return render_template('help.html')	

@app.route('/test/extended')
def pageTestExtended():
	return pageTest(extended=True)
	
@app.route('/test')
def pageTest(extended=False):
	resultString = "<br>-----BEGIN TESTS-----<br><br>"

	resultString = appendResultString(resultString, "pageBrokenaccess", pageBrokenaccess())
	resultString = appendResultString(resultString, "pageBrokenaccessLoggedin", pageBrokenaccessLoggedin(6510))
	resultString = appendResultString(resultString, "pageBrokenaccessLoggedin", pageBrokenaccessLoggedin(0))
	resultString = appendResultString(resultString, "pageBrokenauth1", pageBrokenauth1())
	resultString = appendResultString(resultString, "pageBrokenauth2", pageBrokenauth2())
	resultString = appendResultString(resultString, "pageBrokensession", pageBrokensession())
	resultString = appendResultString(resultString, "pageCookies", pageCookies())
	resultString = appendResultString(resultString, "pageEvilimage", pageEvilimage())
	resultString = appendResultString(resultString, "pageEvillog", pageEvillog())
	resultString = appendResultString(resultString, "pageFront", pageFront())
	resultString = appendResultString(resultString, "pageHelp", pageHelp())
	resultString = appendResultString(resultString, "pageInjection", pageInjection())
	resultString = appendResultString(resultString, "pageSecmis", pageSecmis())
	resultString = appendResultString(resultString, "pageSecmisAdmin", pageSecmisAdmin())
	resultString = appendResultString(resultString, "pageSecmisAdmin2", pageSecmisAdmin2())
	resultString = appendResultString(resultString, "pageSelect", pageSelect())
	resultString = appendResultString(resultString, "pageXss", pageXss())
	resultString = appendResultString(resultString, "pageXssadmin", pageXssadmin())
	resultString = appendResultString(resultString, "pageXssadminRemovecookie", pageXssadminRemovecookie())
	resultString = appendResultString(resultString, "pageXssadminRemovefeedback", pageXssadminRemovefeedback())
	resultString = appendResultString(resultString, "pageLogout", pageLogout("dummy"))
	resultString = appendResultString(resultString, "pageLogoutEmptyPage", pageLogoutEmptyPage())
	resultString = appendResultString(resultString, "pageResetall", pageResetall())
	if extended:
		resultString = appendResultString(resultString, "pageDcheck", pageDcheck())
	else:
		resultString = resultString + "pageDcheck ..n/a (use /test/extended)<br>"	
		
		
	resultString = resultString + "<br>----- END TESTS -----<br>"		
	resultString = Markup(resultString)
		
	return render_template('minimal.html', content=resultString)
	
@app.route('/select')
def pageSelect():
	return render_template('select.html')	
	
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
		return render_template('inside.html', admin=True, page='brokenauth1')
	else:
		return render_template('login.html', page='brokenauth1', incorrect=True, username=username, password=password)

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
		return render_template('inside.html', admin=True, page='brokenauth2')
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
	return render_template('inside.html', admin=True, page='secmis')
	
@app.route('/secmis/admin/')
def pageSecmisAdmin2():
	return render_template('inside.html', admin=True, page='secmis')	

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
		return render_template('inside.html', admin=True, page='inject')
	else:
		return render_template('login.html', page='inject', incorrect=True, sqlline=sql, username=username, password=password)

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
		return render_template('login.html', page='brokenaccess', incorrect=True)
		
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
		return render_template('inside.html', admin=True, page='cookies')
	else:
		return render_template('login.html', page='cookies', incorrect=True)
		
@app.route('/brokenaccess/loggedin/user/<userid>')
def pageBrokenaccessLoggedin(userid):
	if userid == "0":
		return render_template('inside.html', admin=True, page='brokenaccess')
	elif userid == "6510":
		return render_template('inside.html', admin=False, page='brokenaccess')
	else:
		return render_template('servererror.html', page='brokenaccess', incorrectuser='Incorrect user')
		
@app.route('/xsscontact')
def pageXss():
	return render_template('contact.html', page='xsscontact')
	
@app.route('/xsscontact', methods = ['POST'])
def pageXssPost():	
	comment = request.form['comment']
	name = request.form['name']
	
	conn = sqlite3.connect(commentdb)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', (comment,name))
	conn.commit()
	c.close()
	return render_template('contact.html', sent=True, page='xsscontact')	
	
@app.route('/xssadmin')
def pageXssadmin():
	if session.get('loggedin') != "True":
		return render_template('login.html', page='xssadmin')
	else:
		conn = sqlite3.connect(commentdb)
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
		conn.commit()
		sql = '''SELECT comment,name FROM comments'''
		c.execute(sql)
		result = c.fetchall()
		c.close()
		return render_template('inside.html', comments=result, page='xssadmin', admin=True)
		
@app.route('/brokensession')
def pageBrokensession():
	if session.get('loggedin') != "True":
		session['loggedin'] = "False"
		return render_template('login.html', page='brokensession')
	else:
		return render_template('inside.html', admin=True, page='brokensession')

@app.route('/xssadmin/removefeedback')
def pageXssadminRemovefeedback():
	if session.get('loggedin') != "True":
		return render_template('login.html', page='xssadmin', incorrect=True)
	else:
		conn = sqlite3.connect(commentdb)
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
		sql = '''DELETE FROM comments'''
		c.execute(sql)
		conn.commit()
		c.close()
		return redirect(request.url_root + "xssadmin", code=302)
	
@app.route('/removecookies')
def pageXssadminRemovecookie():
	if session.get('loggedin'):
		session.pop('loggedin', None)	
		session.clear()
		return render_template('select.html', message="Ok, removed cookies.")
	else:
		session.clear()
		return render_template('select.html', message="Cleared all cookies, couldn't find the loggedin cookie.")
		
		
		
@app.route('/logout/')
def pageLogoutEmptyPage():
		return pageSelect()
		
@app.route('/logout/<page>')
def pageLogout(page):
	if session.get('loggedin'):
		session.pop('loggedin', None)	
		session.clear()
		return render_template('login.html', page=page)
	else:
		session.clear()
		return render_template('login.html', page=page)	
		
@app.route('/xssadmin', methods = ['POST'])
def pageXssadminPost():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'Administrator' and password == 'admin':
		session['loggedin'] = "True"
		return redirect(request.url_root + "xssadmin", code=302)
	else:
		return render_template('login.html', page='xssadmin', incorrect=True)
		
@app.route('/xssadmin/adddummydata')
def pageXssadminAdddummydata():
	conn = sqlite3.connect(commentdb)
	c = conn.cursor()
	c.execute('DELETE FROM comments')
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("Do you think you're living an ordinary life? You are so mistaken it's difficult to even explain. The mere fact that you exist makes you extraordinary. The odds of you existing are less than winning the lottery, but here you are. Are you going to let this extraordinary opportunity pass?","Sandeep"))
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("Indescribable oppression, which seemed to generate in some unfamiliar part of her consciousness, filled her whole being with a vague anguish. It was like a shadow, like a mist passing across her soul's summer day. It was strange and unfamiliar; it was a mood. She did not sit there inwardly upbraiding her husband, lamenting at Fate, which had directed her footsteps to the path which they had taken. She was just having a good cry all to herself. The mosquitoes made merry over her, biting her firm, round arms and nipping at her bare insteps.","Jacob"))
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("I'm heading back to Colorado tomorrow after being down in Santa Barbara over the weekend for the festival there. I will be making October plans once there and will try to arrange so I'm back here for the birthday if possible. I'll let you know as soon as I know the doctor's appointment schedule and my flight plans.","Marc"))
	conn.commit()
	c.close()
	return render_template('select.html', message="Dummy data added")
	
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
	return send_file('static/evilimg.png', mimetype='image/png', as_attachment=False)
	
@app.route('/evillog/reset')
def pageEvillogReset():
	conn = sqlite3.connect(tempdb)
	c = conn.cursor()	
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	c.execute('''DELETE FROM evilimage''')
	conn.commit()
	c.close()
	return "ok"
	
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
		
@app.route('/resetall')
def pageResetall():	
	conn = sqlite3.connect(tempdb)
	c = conn.cursor()	
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	c.execute('''DELETE FROM evilimage''')
	conn.commit()
	c.close()	
	
	conn = sqlite3.connect(commentdb)
	c = conn.cursor()
	c.execute('DELETE FROM comments')
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("Do you think you're living an ordinary life? You are so mistaken it's difficult to even explain. The mere fact that you exist makes you extraordinary. The odds of you existing are less than winning the lottery, but here you are. Are you going to let this extraordinary opportunity pass?","Sandeep"))
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("Indescribable oppression, which seemed to generate in some unfamiliar part of her consciousness, filled her whole being with a vague anguish. It was like a shadow, like a mist passing across her soul's summer day. It was strange and unfamiliar; it was a mood. She did not sit there inwardly upbraiding her husband, lamenting at Fate, which had directed her footsteps to the path which they had taken. She was just having a good cry all to herself. The mosquitoes made merry over her, biting her firm, round arms and nipping at her bare insteps.","Jacob"))
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("I'm heading back to Colorado tomorrow after being down in Santa Barbara over the weekend for the festival there. I will be making October plans once there and will try to arrange so I'm back here for the birthday if possible. I'll let you know as soon as I know the doctor's appointment schedule and my flight plans.","Marc"))
	conn.commit()
	c.close()
	
	if session.get('loggedin'):
		session.pop('loggedin', None)	
	session.clear()
	return render_template('select.html', message="Cookies and databases has been reset")
	
@app.route('/dcheck')
def pageDcheck():
	return render_template('depcheck.html')	

def appendResultString(resultString, label, testResult):
	try:
		if testResult:
			resultString = resultString + label + " ..ok<br>"
		else:
			resultString = resultString + label + " ..fail!<br>"
	except Exception:
		resultString = resultString + label + " ..fail!<br>"
		return resultString

	return resultString
		

if __name__ == "__main__":
	if prod:
		app.run()
		
if not prod:
	app.run(host='0.0.0.0', port=8080)
