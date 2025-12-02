from flask import Blueprint, request, render_template, redirect, session, send_file, send_from_directory
import requests
import io
import base64
import os

# Store images server-side with session ID as key
ssrf_images = {}

app = Blueprint('ssrf',__name__)

@app.route('/ssrf')
def pageSsrf():
	return render_template('login.html', page='ssrf')

@app.route('/ssrf', methods=['POST'])
def pageSsrfPost():
	username = request.form['username']
	password = request.form['password']
	
	if username == 'user' and password == 'user':
		session['ssrf_loggedin'] = True
		session['ssrf_username'] = username
		return redirect("/ssrf/profile", code=302)
	else:
		return render_template('login.html', page='ssrf', incorrect=True)

@app.route('/ssrf/profile')
def pageSsrfProfile():
	if not session.get('ssrf_loggedin'):
		return redirect('/ssrf', code=302)
	
	# Get messages but don't pop them yet
	ssrf_message = session.get('ssrf_message')
	ssrf_error = session.get('ssrf_error')
	
	# Clear messages after reading
	if ssrf_message:
		session.pop('ssrf_message', None)
	if ssrf_error:
		session.pop('ssrf_error', None)
	
	return render_template('inside.html', admin=False, page='ssrf', ssrf_message=ssrf_message, ssrf_error=ssrf_error)

#To make the demo a bit smoother, append the server port to localhost URLs
#So that a SSRF payload to localhost works even if the server is on a non-standard port
def append_server_port_if_localhost(img_url):
	server_port = request.environ.get('SERVER_PORT')
	img_url = img_url.replace("://localhost/", f"://localhost:{server_port}/")
	
	return img_url

@app.route('/ssrf/profile/upload', methods=['POST'])
def pageSsrfUpload():
	if not session.get('ssrf_loggedin'):
		return redirect('/ssrf', code=302)
	
	img_url = request.form.get('imageUrl')
	img_url = img_url.strip().lower()

	#Fake that we're on AWS
	img_url = img_url.replace("169.254.169.254","localhost")
	
	if not img_url:
		session['ssrf_error'] = 'Please provide an image URL'
		return redirect('/ssrf/profile', code=302)
	
	try:
		# VULNERABLE (but controlled for demo): Limited URL validation
		# This allows specific demo URLs to work while blocking real attacks

		if is_allowed_url(img_url):
			img_url = append_server_port_if_localhost(img_url)
			# Handle HTTP/HTTPS URLs
			print(f"SSRF url being called: {img_url}")
			response = requests.get(img_url, timeout=5)
			
			if response.status_code == 200:
				session_id = session.get('ssrf_username', 'default')
				ssrf_images[session_id] = {
					'data': response.content[:50000],  # Limit to 50KB
					'type': response.headers.get('Content-Type', 'image/jpeg')
				}
				session['ssrf_has_image'] = True
				session['ssrf_message'] = 'Profile picture updated successfully!'
				print(f"Stored image for {session_id}, size: {len(response.content)}")
			else:
				session['ssrf_error'] = f'Failed to fetch image: HTTP {response.status_code}'
		else:
			session['ssrf_error'] = 'URL not allowed. Only demo URLs are permitted for security reasons.'
			
	except requests.exceptions.Timeout:
		session['ssrf_error'] = 'Request timed out'
	except requests.exceptions.RequestException as e:
		session['ssrf_error'] = f'Request failed: {str(e)}'
	except Exception as e:
		session['ssrf_error'] = f'Error: {str(e)}'
	
	return redirect('/ssrf/profile', code=302)

def is_allowed_url(url):
	"""Check if URL is allowed for real requests"""

	# Check if begins with http:// or https://
	if not (url.startswith("http://") or url.startswith("https://")):
		return False
	
	# Allowed hosts
	localhost_variants = [
		'localhost',
		'127.0.0.1',
		'evil.lab.zdt.se',
	]

	from urllib.parse import urlparse
	parsed = urlparse(url.lower())
	hostname = parsed.hostname
	for variant in localhost_variants:
		if hostname == variant:
			return True
	
	# Allow oastify.com domains (for out-of-band testing)
	# Extract hostname to check domain properly
	try:
		if hostname.endswith('.oastify.com') or hostname == 'oastify.com':
			return True
	except:
		return False
	
	# Block everything else
	return False


@app.route('/ssrf/profile/profile_picture')
def pageSsrfImage():
	if not session.get('ssrf_loggedin'):
		return redirect('/ssrf', code=302)
	
	session_id = session.get('ssrf_username', 'default')
	image_info = ssrf_images.get(session_id)
	
	# Debug: print to console
	print(f"SSRF Image Request - Session ID: {session_id}, Has image: {image_info is not None}")
	
	if image_info:
		# Return whatever was fetched, even if it's not an image
		# This will cause a broken image if it's HTML/JSON/text
		return send_file(
			io.BytesIO(image_info['data']),
			mimetype=image_info['type'],
			as_attachment=False
		)
	else:
		# Return default image only if nothing was uploaded yet
		return redirect('/static/img/user.jpg', code=302)

@app.route('/ssrf/logout')
def pageSsrfLogout():
	session_id = session.get('ssrf_username', 'default')
	# Clean up server-side image storage
	if session_id in ssrf_images:
		del ssrf_images[session_id]
	
	session.pop('ssrf_loggedin', None)
	session.pop('ssrf_username', None)
	session.pop('ssrf_message', None)
	session.pop('ssrf_error', None)
	session.pop('ssrf_has_image', None)
	return redirect('/ssrf', code=302)

# Helper function for localhost-only access
def localhost_only(f):
	"""Decorator to restrict access to localhost only"""
	from functools import wraps
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if request.remote_addr not in ['127.0.0.1', 'localhost', '::1']:
			return "Access denied: This resource is only accessible from localhost", 403
		return f(*args, **kwargs)
	return decorated_function

# Internal routes that should only be accessible from localhost
# These simulate internal admin pages
@app.route('/admin')
@localhost_only
def pageAdmin():
	return render_template('ssrf_admin.html')

@app.route('/secrets/coca_cola_recipe.txt')
@localhost_only
def pageSecrets():
	return render_template('ssrf_secrets_coca_cola_recipe.txt'), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# AWS Metadata simulation routes (localhost only)
@app.route('/latest/meta-data/')
@localhost_only
def awsMetadata():
	return render_template('ssrf_latest_metadata_index.txt'), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/latest/meta-data/iam/security-credentials/')
@localhost_only
def awsSecurityCredentials():
	return render_template('ssrf_latest_metadata_index_security-credentials_index.txt'), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/latest/meta-data/iam/security-credentials/AdminRole')
@localhost_only
def awsAdminRole():
	return render_template('ssrf_latest_metadata_AdminRole'), 200, {'Content-Type': 'application/json; charset=utf-8'}
