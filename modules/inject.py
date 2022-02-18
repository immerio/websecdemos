from flask import Blueprint, request, render_template
import sqlite3, os, sys

tempdb_path = "dbs/inject_tempdb"

app = Blueprint('inject',__name__)
@app.route('/inject')
def pageInjection():
	return render_template('login.html', page='inject')

@app.route('/inject', methods = ['POST'])
def pageInjectPost():
	username = request.form['username']
	password = request.form['password']
	
	conn = sqlite3.connect(tempdb_path)
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