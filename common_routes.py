from flask import Blueprint, render_template, session, request
import test_response

app = Blueprint('common_routes',__name__)

@app.route('/')
def pageFront():
	return render_template('login.html')

@app.route('/help')
def pageHelp():
	return render_template('help.html', domain=request.base_url)	
	
@app.route('/select')
def pageSelect():
	return render_template('select.html')	

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

