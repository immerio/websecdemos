from flask import Blueprint, render_template, session, request
from dotenv import load_dotenv
import os
import test_response

# Load environment variables from .env file
load_dotenv()

app = Blueprint('common_routes',__name__)

def get_evil_domain():
	"""Get the evil domain from environment variable or fallback to url_root"""
	evil_domain = os.getenv('EVIL_DOMAIN')
	if evil_domain:
		return evil_domain
	return request.url_root

@app.route('/')
def pageFront():
	return render_template('login.html')

@app.route('/help')
def pageHelp():
	return render_template('help.html', evil_domain=get_evil_domain())	
	
@app.route('/select')
def pageSelect():
	return render_template('select.html', evil_domain=get_evil_domain())	

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

