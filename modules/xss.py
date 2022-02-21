from flask import Blueprint, request, render_template, session, redirect

import sqlite3

commentdb_path = "dbs/xss_commentdb"

app = Blueprint('xss',__name__)
		
@app.route('/xsscontact')
def pageXss():
	return render_template('contact.html', page='xsscontact')
	
@app.route('/xsscontact', methods = ['POST'])
def pageXssPost():	
	comment = request.form['comment']
	name = request.form['name']
	
	conn = sqlite3.connect(commentdb_path)
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
		conn = sqlite3.connect(commentdb_path)
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
		conn.commit()
		sql = '''SELECT comment,name FROM comments'''
		c.execute(sql)
		result = c.fetchall()
		c.close()
		return render_template('inside.html', comments=result, page='xssadmin', admin=True)

@app.route('/xssadmin/removefeedback')
def pageXssadminRemovefeedback():
	if session.get('loggedin') != "True":
		return render_template('login.html', page='xssadmin', incorrect=True)
	else:
		conn = sqlite3.connect(commentdb_path)
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
	conn = sqlite3.connect(commentdb_path)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	c.execute('DELETE FROM comments')	
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
	conn = sqlite3.connect(commentdb_path)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	c.execute('''DELETE FROM evilimage''')
	c.execute('''INSERT OR IGNORE INTO evilimage(data) VALUES (?)''', (cookies,))
	conn.commit()
	c.close()
	return send_file('static/evilimg.png', mimetype='image/png', as_attachment=False)
	
@app.route('/evillog/reset')
def pageEvillogReset():
	conn = sqlite3.connect(commentdb_path)
	c = conn.cursor()	
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	c.execute('''DELETE FROM evilimage''')
	conn.commit()
	c.close()
	return "ok"
	
@app.route('/evillog')
def pageEvillog():
	conn = sqlite3.connect(commentdb_path)
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
	conn = sqlite3.connect(commentdb_path)
	c = conn.cursor()	
	c.execute('CREATE TABLE IF NOT EXISTS evilimage("data" TEXT)')
	c.execute('''DELETE FROM evilimage''')
	conn.commit()
	c.close()	
	
	conn = sqlite3.connect(commentdb_path)
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS comments("comment" TEXT, "name" TEXT)')
	c.execute('DELETE FROM comments')
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("Do you think you're living an ordinary life? You are so mistaken it's difficult to even explain. The mere fact that you exist makes you extraordinary. The odds of you existing are less than winning the lottery, but here you are. Are you going to let this extraordinary opportunity pass?","Sandeep"))
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("Indescribable oppression, which seemed to generate in some unfamiliar part of her consciousness, filled her whole being with a vague anguish. It was like a shadow, like a mist passing across her soul's summer day. It was strange and unfamiliar; it was a mood. She did not sit there inwardly upbraiding her husband, lamenting at Fate, which had directed her footsteps to the path which they had taken. She was just having a good cry all to herself. The mosquitoes made merry over her, biting her firm, round arms and nipping at her bare insteps.","Jacob"))
	c.execute('''INSERT OR IGNORE INTO comments(comment,name) VALUES (?,?)''', ("I'm heading back to Colorado tomorrow after being down in Santa Barbara over the weekend for the festival there. I will be making October plans once there and will try to arrange so I'm back here for the birthday if possible. I'll let you know as soon as I know the doctor's appointment schedule and my flight plans.","Marc"))
	conn.commit()
	c.close()
	
	if session.get('loggedin'):
		session.pop('loggedin', None)	
	session.clear()
	return render_template('select.html', message="Cookies and databases has been reset")