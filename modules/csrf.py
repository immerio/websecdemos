from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify, make_response
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

csrf_db_path = "dbs/csrf_mdm_db"

app = Blueprint('csrf', __name__)

def get_evil_domain():
	"""Get the evil domain from environment variable or fallback to url_root"""
	evil_host = os.getenv('EVIL_HOST')
	if evil_host:
		return evil_host.rstrip('/') + '/'
	return request.url_root

def init_csrf_db():
	"""Initialize CSRF demo database with sample data"""
	conn = sqlite3.connect(csrf_db_path)
	c = conn.cursor()
	
	# Create tables
	c.execute('''CREATE TABLE IF NOT EXISTS csrf_devices (
		id INTEGER PRIMARY KEY,
		device_name TEXT,
		employee_name TEXT,
		device_type TEXT,
		status TEXT,
		last_seen TEXT
	)''')
	
	c.execute('''CREATE TABLE IF NOT EXISTS csrf_policies (
		id INTEGER PRIMARY KEY,
		policy_name TEXT,
		enabled BOOLEAN,
		description TEXT
	)''')
	
	c.execute('''CREATE TABLE IF NOT EXISTS csrf_logs (
		id INTEGER PRIMARY KEY,
		admin_user TEXT,
		action TEXT,
		target TEXT,
		timestamp TEXT
	)''')
	
	# Add sample devices if none exist
	c.execute('SELECT COUNT(*) FROM csrf_devices')
	if c.fetchone()[0] == 0:
		# Generate 932 realistic devices programmatically
		import random
		
		# Device types and their probabilities
		device_types = [
			("iPhone 15 Pro", 0.15),
			("iPhone 14", 0.20),
			("iPhone 13", 0.15),
			("iPad Pro", 0.10),
			("iPad Air", 0.08),
			("Samsung Galaxy S24", 0.12),
			("Samsung Galaxy S23", 0.10),
			("Google Pixel 8", 0.05),
			("OnePlus 11", 0.03),
			("Xiaomi 13", 0.02)
		]
		
		# Department prefixes and employee count ranges
		departments = [
			("CEO", 1, 2),
			("HR", 15, 25),
			("IT", 25, 35),
			("Sales", 120, 150),
			("Finance", 30, 45),
			("Marketing", 40, 60),
			("Operations", 80, 120),
			("Legal", 8, 15),
			("R&D", 60, 90),
			("Support", 45, 70),
			("Admin", 20, 35),
			("Security", 12, 20),
			("QA", 25, 40),
			("Engineering", 150, 200),
			("Product", 35, 50),
			("Design", 20, 35)
		]
		
		# Common first and last names for realistic employees
		first_names = ["John", "Sarah", "Mike", "Lisa", "David", "Emma", "James", "Anna", "Robert", "Maria", 
					   "Chris", "Jennifer", "Michael", "Jessica", "William", "Ashley", "Daniel", "Amanda", 
					   "Matthew", "Michelle", "Andrew", "Stephanie", "Joshua", "Nicole", "Brian", "Elizabeth",
					   "Kevin", "Rebecca", "Mark", "Rachel", "Steven", "Laura", "Paul", "Catherine", "Scott"]
		
		last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", 
					  "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", 
					  "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez",
					  "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright"]
		
		sample_devices = []
		device_counter = 1
		
		# Simple approach: generate exactly 932 devices by cycling through departments
		devices_per_dept = 932 // len(departments)  # Base devices per department
		extra_devices = 932 % len(departments)     # Extra devices to distribute
		
		for i, (dept_name, min_count, max_count) in enumerate(departments):
			# Give each department base amount plus 1 extra if needed
			dept_device_count = devices_per_dept + (1 if i < extra_devices else 0)
			
			print(f"DEBUG: {dept_name} department getting {dept_device_count} devices")
			
			for j in range(dept_device_count):
				# Choose device type based on weighted probability
				rand_num = random.random()
				cumulative_prob = 0
				selected_device = "iPhone 14"  # fallback
				
				for device_type, prob in device_types:
					cumulative_prob += prob
					if rand_num <= cumulative_prob:
						selected_device = device_type
						break
				
				# Generate employee name
				first_name = random.choice(first_names)
				last_name = random.choice(last_names)
				employee_name = f"{first_name} {last_name} ({dept_name})"
				
				# Generate device name
				device_prefix = "iPhone" if "iPhone" in selected_device else "iPad" if "iPad" in selected_device else "Android"
				device_name = f"{device_prefix}-{dept_name}-{device_counter:03d}"
				
				# Generate realistic last seen time (within last 24 hours)
				import datetime
				base_time = datetime.datetime(2025, 1, 7, 16, 0, 0)
				random_minutes = random.randint(-1440, 0)  # Last 24 hours
				last_seen = (base_time + datetime.timedelta(minutes=random_minutes)).strftime("%Y-%m-%d %H:%M:%S")
				
				sample_devices.append((device_name, employee_name, selected_device, "active", last_seen))
				device_counter += 1
				device_name = f"{device_prefix}-{dept_name}-{device_counter:03d}"
				
				# Generate realistic last seen time (within last 24 hours)
				import datetime
				base_time = datetime.datetime(2025, 1, 7, 16, 0, 0)
				random_minutes = random.randint(-1440, 0)  # Last 24 hours
				last_seen = (base_time + datetime.timedelta(minutes=random_minutes)).strftime("%Y-%m-%d %H:%M:%S")
				
				sample_devices.append((device_name, employee_name, selected_device, "active", last_seen))
				device_counter += 1
		
		# Ensure we have exactly 932 devices
		sample_devices = sample_devices[:932]
		print(f"DEBUG: Generated {len(sample_devices)} devices")
		
		# Insert all devices in batches for better performance
		batch_size = 100
		for i in range(0, len(sample_devices), batch_size):
			batch = sample_devices[i:i + batch_size]
			c.executemany('INSERT INTO csrf_devices (device_name, employee_name, device_type, status, last_seen) VALUES (?, ?, ?, ?, ?)', batch)
			print(f"DEBUG: Inserted batch {i//batch_size + 1} with {len(batch)} devices")
	
	# Add sample policies if none exist
	c.execute('SELECT COUNT(*) FROM csrf_policies')
	if c.fetchone()[0] == 0:
		sample_policies = [
			("Device Encryption", True, "Require full disk encryption on all devices"),
			("Remote Wipe", True, "Allow remote wipe capabilities for lost devices"),
			("App Store Restrictions", True, "Restrict installation of unauthorized apps"),
			("Password Policy", True, "Enforce strong password requirements"),
			("VPN Requirement", True, "Require VPN connection for corporate access")
		]
		c.executemany('INSERT INTO csrf_policies (policy_name, enabled, description) VALUES (?, ?, ?)', sample_policies)
	
	conn.commit()
	c.close()

@app.route('/csrf')
def csrf_login():
	if session.get('csrf_loggedin') == "True":
		return redirect(url_for('csrf.csrf_dashboard'))
	return render_template('login.html', page='csrf')

@app.route('/csrf', methods=['POST'])
def csrf_login_post():
	username = request.form['username']
	password = request.form['password']
	
	if 'admin' in username.lower() and 'admin' in password.lower():
		session['csrf_loggedin'] = "True"
		session['csrf_username'] = username
		session['csrf_role'] = "MDM Administrator"
		init_csrf_db()
		return redirect(url_for('csrf.csrf_dashboard'))
	else:
		return render_template('login.html', page='csrf', incorrect=True)

@app.route('/csrf/dashboard')
def csrf_dashboard():
	if session.get('csrf_loggedin') != "True":
		return redirect(url_for('csrf.csrf_login'))
	
	init_csrf_db()
	conn = sqlite3.connect(csrf_db_path)
	c = conn.cursor()
	
	# Get device counts
	c.execute('SELECT COUNT(*) FROM csrf_devices WHERE status = "active"')
	active_devices = c.fetchone()[0]
	
	c.execute('SELECT COUNT(*) FROM csrf_devices WHERE status = "wiped"')
	wiped_devices = c.fetchone()[0]
	
	# Get recent logs
	c.execute('SELECT admin_user, action, target, timestamp FROM csrf_logs ORDER BY timestamp DESC LIMIT 5')
	recent_logs = c.fetchall()
	
	c.close()
	
	csrf_protection = session.get('csrf_protection_enabled', False)
	
	return render_template('csrf_mdm_dashboard.html', 
						   username=session['csrf_username'],
						   active_devices=active_devices,
						   wiped_devices=wiped_devices,
						   recent_logs=recent_logs,
						   csrf_protection=csrf_protection,
						   evil_domain=get_evil_domain())

@app.route('/csrf/devices')
def csrf_devices():
	if session.get('csrf_loggedin') != "True":
		return redirect(url_for('csrf.csrf_login'))
	
	conn = sqlite3.connect(csrf_db_path)
	c = conn.cursor()
	
	# Debug: Check total device count
	c.execute('SELECT COUNT(*) FROM csrf_devices')
	total_count = c.fetchone()[0]
	print(f"DEBUG: Total devices in database: {total_count}")
	
	c.execute('SELECT id, device_name, employee_name, device_type, status, last_seen FROM csrf_devices ORDER BY id')
	devices = c.fetchall()
	print(f"DEBUG: Retrieved {len(devices)} devices from query")
	
	c.close()
	
	csrf_protection = session.get('csrf_protection_enabled', False)
	
	return render_template('csrf_device_management.html',
						   username=session['csrf_username'],
						   devices=devices,
						   csrf_protection=csrf_protection)

@app.route('/csrf/wipe-device', methods=['POST'])
def csrf_wipe_device():
	if session.get('csrf_loggedin') != "True":
		return jsonify({"error": "Not authenticated"}), 401
	
	# Check CSRF protection
	if session.get('csrf_protection_enabled', False):
		csrf_token = request.form.get('csrf_token')
		expected_token = session.get('csrf_token')
		if not csrf_token or csrf_token != expected_token:
			return jsonify({"error": "CSRF token invalid"}), 403
	
	device_id = request.form.get('device_id')
	action_type = request.form.get('action', 'wipe')  # wipe, lock, or wipe_all
	
	conn = sqlite3.connect(csrf_db_path)
	c = conn.cursor()
	
	if action_type == 'wipe_all':
		# Wipe all devices - typical CSRF attack target
		c.execute('UPDATE csrf_devices SET status = "wiped"')
		target = "ALL_DEVICES"
		action_desc = "Wipe All Devices"
	elif action_type == 'lock':
		c.execute('UPDATE csrf_devices SET status = "locked" WHERE id = ?', (device_id,))
		target = f"Device_{device_id}"
		action_desc = "Lock Device"
	else:
		c.execute('UPDATE csrf_devices SET status = "wiped" WHERE id = ?', (device_id,))
		target = f"Device_{device_id}"
		action_desc = "Wipe Device"
	
	# Log the action
	c.execute('''INSERT INTO csrf_logs (admin_user, action, target, timestamp) 
				 VALUES (?, ?, ?, ?)''', 
			  (session['csrf_username'], action_desc, target, datetime.now().isoformat()))
	
	conn.commit()
	c.close()
	
	return jsonify({"success": True, "message": f"{action_desc} completed"})

@app.route('/csrf/toggle-protection')
def csrf_toggle_protection():
	if session.get('csrf_loggedin') != "True":
		return redirect(url_for('csrf.csrf_login'))
	
	session['csrf_protection_enabled'] = not session.get('csrf_protection_enabled', False)
	
	# Generate new CSRF token if protection is enabled
	if session['csrf_protection_enabled']:
		import secrets
		session['csrf_token'] = secrets.token_hex(16)
	
	return redirect(url_for('csrf.csrf_dashboard'))

# Evil domain routes
@app.route('/csrf/contractor-portal')
def csrf_evil_contractor():
	# Get MDM host URL for the target domain
	mdm_host = os.getenv('MDM_HOST', 'http://localhost:5000')
	mdm_target = mdm_host.rstrip('/') + '/'
	return render_template('csrf_evil_contractor.html', 
						   target_domain=mdm_target,
						   evil_domain=get_evil_domain())

@app.route('/csrf/reset')
def csrf_reset():
	"""Reset CSRF demo data"""
	conn = sqlite3.connect(csrf_db_path)
	c = conn.cursor()
	
	# Reset all devices to active
	c.execute('UPDATE csrf_devices SET status = "active"')
	
	# Clear logs
	c.execute('DELETE FROM csrf_logs')
	
	conn.commit()
	c.close()
	
	# Clear session data
	keys_to_remove = ['csrf_loggedin', 'csrf_username', 'csrf_role', 'csrf_protection_enabled', 'csrf_token']
	for key in keys_to_remove:
		session.pop(key, None)
	
	return "CSRF demo reset completed"

@app.route('/csrf/logout')
def csrf_logout():
	keys_to_remove = ['csrf_loggedin', 'csrf_username', 'csrf_role', 'csrf_protection_enabled', 'csrf_token']
	for key in keys_to_remove:
		session.pop(key, None)
	return redirect(url_for('csrf.csrf_login'))
