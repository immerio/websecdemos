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
		# VULNERABLE: No URL validation or filtering
		# This allows attackers to make requests to internal resources
		response = requests.get(img_url, timeout=5)
		
		if response.status_code == 200:
			# Store the fetched image data server-side (not in cookie-based session)
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
			
	except requests.exceptions.Timeout:
		session['ssrf_error'] = 'Request timed out'
	except requests.exceptions.RequestException as e:
		session['ssrf_error'] = f'Request failed: {str(e)}'
	
	return redirect('/ssrf/profile', code=302)

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
