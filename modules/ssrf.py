from flask import Blueprint, request, render_template, redirect, session, send_file
import requests
import io
import base64

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

@app.route('/ssrf/profile/upload', methods=['POST'])
def pageSsrfUpload():
	if not session.get('ssrf_loggedin'):
		return redirect('/ssrf', code=302)
	
	img_url = request.form.get('imageUrl')
	
	if not img_url:
		session['ssrf_error'] = 'Please provide an image URL'
		return redirect('/ssrf/profile', code=302)
	
	try:
		# VULNERABLE (but controlled for demo): Limited URL validation
		# This allows specific demo URLs to work while blocking real attacks
		
		# Mock responses for demo purposes
		mock_response = get_mock_response(img_url)
		
		if mock_response:
			# Use mock response
			session_id = session.get('ssrf_username', 'default')
			ssrf_images[session_id] = {
				'data': mock_response['content'],
				'type': mock_response['content_type']
			}
			session['ssrf_has_image'] = True
			session['ssrf_message'] = 'Profile picture updated successfully!'
			print(f"Stored mock response for {session_id}, size: {len(mock_response['content'])}")
		elif is_allowed_url(img_url):
			# Only allow specific external domain for real requests
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
	
	return redirect('/ssrf/profile', code=302)

def is_allowed_url(url):
	"""Check if URL is allowed for real requests (only evil.lab.zdt.se)"""
	return url.startswith('http://evil.lab.zdt.se/') or url.startswith('https://evil.lab.zdt.se/')

def get_mock_response(url):
	"""Return mock responses for demo URLs"""
	
	# AWS Metadata
	if url == 'http://169.254.169.254/latest/meta-data/':
		return {
			'content': b'''ami-id
ami-launch-index
ami-manifest-path
block-device-mapping/
events/
hostname
iam/
instance-action
instance-id
instance-life-cycle
instance-type
local-hostname
local-ipv4
mac
metrics/
network/
placement/
profile
public-hostname
public-ipv4
public-keys/
reservation-id
security-groups
services/''',
			'content_type': 'text/plain'
		}
	
	elif url == 'http://169.254.169.254/latest/meta-data/iam/security-credentials/':
		return {
			'content': b'AdminRole',
			'content_type': 'text/plain'
		}
	
	elif url == 'http://169.254.169.254/latest/meta-data/iam/security-credentials/AdminRole':
		return {
			'content': b'''{
  "Code" : "Success",
  "LastUpdated" : "2025-11-06T10:15:32Z",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "AKIAIOSFODNN7EXAMPLE",
  "SecretAccessKey" : "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Token" : "IQoJb3JpZ2luX2VjEHoaCXVzLWVhc3QtMSJHMEUCIQDEXAMPLETOKEN...",
  "Expiration" : "2025-11-06T16:42:18Z"
}''',
			'content_type': 'application/json'
		}
	
	# File protocol - /etc/passwd
	elif url == 'file:///etc/passwd' or url == 'file://etc/passwd':
		return {
			'content': b'''root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
postgres:x:105:113:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
mysql:x:106:114:MySQL Server,,,:/nonexistent:/bin/false
admin:x:1000:1000:Admin User,,,:/home/admin:/bin/bash''',
			'content_type': 'text/plain'
		}
	
	# Localhost admin page
	elif url == 'http://localhost/admin' or url == 'http://127.0.0.1/admin':
		return {
			'content': b'''<!DOCTYPE html>
<html>
<head><title>Admin Panel - INTERNAL ONLY</title></head>
<body>
<h1>Internal Admin Panel</h1>
<p><strong>WARNING: This page should not be accessible from external networks!</strong></p>
<h2>System Configuration</h2>
<ul>
<li>Database: postgres://admin:P@ssw0rd123!@db.internal:5432/production</li>
<li>API Key: sk_live_51HxYzABC123XYZ789...</li>
<li>Admin Password: SuperSecret2024!</li>
<li>Backup Server: backup.internal.company.com</li>
</ul>
<h2>Recent Activity</h2>
<p>Last login: admin@localhost - 2025-11-06 09:23:45</p>
</body>
</html>''',
			'content_type': 'text/html'
		}
	
	# Localhost secret recipe
	elif url == 'http://localhost/secrets/coca_cola_recipe.txt' or url == 'http://127.0.0.1/secrets/coca_cola_recipe.txt':
		return {
			'content': b'''CONFIDENTIAL - COCA-COLA SECRET RECIPE
========================================

*** TOP SECRET - DO NOT DISTRIBUTE ***

Original Recipe - 1886
Author: John Pemberton

Ingredients (for 1 gallon):
---------------------------
- Citric Acid: 3 oz
- Caffeine: 1 oz
- Sugar: 30 lbs (unspecified amount of water)
- Water: 2.5 gallons
- Lime Juice: 2 pints
- Vanilla Extract: 1 oz
- Caramel: 1.5 oz or more for color

Flavor Base (7X):
-----------------
- Alcohol: 8 oz
- Orange Oil: 20 drops
- Lemon Oil: 30 drops  
- Nutmeg Oil: 10 drops
- Coriander Oil: 5 drops
- Neroli Oil: 10 drops
- Cinnamon Oil: 10 drops

Mix citric acid and caffeine in the water.
Add vanilla and flavoring.
Let stand for 24 hours.


*** INTERNAL USE ONLY - DESTROY AFTER READING ***''',
			'content_type': 'text/plain'
		}
	
	return None

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
