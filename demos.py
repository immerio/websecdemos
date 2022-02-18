from flask import Flask, request, redirect, render_template, session, send_file, Markup

import modules, test_response

app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'CHANGEME',
    'SESSION_COOKIE_HTTPONLY': False,
})

@app.route('/')
def pageFront():
	return render_template('login.html')

@app.route('/help')
def pageHelp():
	return render_template('help.html')	

@app.route('/test')
def pageTest():	
	return render_template('minimal.html', content=test_response.getTestresults())
	
@app.route('/select')
def pageSelect():
	return render_template('select.html')	

app.register_blueprint(modules.brokenaccess.app)
app.register_blueprint(modules.brokenauth1.app)
app.register_blueprint(modules.brokenauth2.app)
app.register_blueprint(modules.brokensession.app)
app.register_blueprint(modules.inject.app)
app.register_blueprint(modules.secmis.app)
app.register_blueprint(modules.xss.app)
		
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

if __name__ == "__main__":
		app.run()