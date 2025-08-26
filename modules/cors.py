from flask import Blueprint, request, session, render_template, jsonify, make_response
import random
import os
from datetime import datetime, timedelta

cors_bp = Blueprint('cors', __name__, url_prefix='/cors')

# Get evil domain from environment and ensure it ends with /
def get_evil_domain():
    evil_host = os.getenv('EVIL_HOST', 'http://localhost:8080')
    return evil_host.rstrip('/') + '/'

EVIL_DOMAIN = get_evil_domain()

def generate_cors_devices():
    """Generate realistic device data with sensitive information for CORS demo"""
    
    # Simplified employee names (reduced from 40+ to 12 for smaller session)
    employees = [
        "Sarah Connor", "John Matrix", "Ellen Ripley", "James Bond", 
        "Lara Croft", "Ethan Hunt", "Alice Resident", "Leon Kennedy",
        "Trinity Anderson", "Neo Anderson", "Jack Ryan", "Jason Bourne"
    ]
    
    # Simplified device types (reduced for smaller session)
    device_types = [
        "iPhone 15 Pro", "iPhone 14", "Samsung Galaxy S24", "Google Pixel 8",
        "iPad Pro", "MacBook Air M2", "Surface Pro 9"
    ]
    
    # Simplified departments (reduced for smaller session)
    departments = [
        "Engineering", "Sales", "Marketing", "HR", "Finance", "IT"
    ]
    
    # Simplified app lists (reduced for smaller session)
    app_lists = [
        ["Slack", "Outlook", "Teams"],
        ["Zoom", "Gmail", "Chrome"],
        ["Salesforce", "Jira", "Office 365"],
        ["WhatsApp", "LinkedIn", "Maps"]
    ]
    
    # Simplified compliance violations (reduced for smaller session)
    violations = [
        "Outdated OS", "Weak passcode", "VPN not configured", "Encryption disabled"
    ]
    
    devices = []
    used_imeis = set()
    used_phones = set()
    
    # Generate exactly 25 devices (reduced from 385 for reasonable session size)
    for i in range(25):
        # Generate unique IMEI
        while True:
            imei = f"86153605{random.randint(1000000, 9999999)}"
            if imei not in used_imeis:
                used_imeis.add(imei)
                break
        
        # Generate unique phone number
        while True:
            phone = f"+1-555-{random.randint(1000, 9999)}"
            if phone not in used_phones:
                used_phones.add(phone)
                break
        
        # Simplified location data (reduced from 10 to 4 cities)
        locations = [
            "San Francisco", "New York", "Los Angeles", "Chicago"
        ]
        
        device = {
            "device_id": f"CORS-DEV-{i+1:04d}",
            "employee": random.choice(employees),
            "department": random.choice(departments),
            "device_type": random.choice(device_types),
            "phone_number": phone,
            "imei": imei,
            "location": random.choice(locations),
            "installed_apps": random.choice(app_lists),
            "os_version": random.choice(["iOS 17.1", "Android 14", "Windows 11"]),
            "jailbroken": random.choice([False, False, False, True]),  # Mostly not jailbroken
            "compliance_violations": random.sample(violations, random.randint(0, 1)),
            "last_seen": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S")
        }
        devices.append(device)
    
    return devices

def get_cors_devices():
    """Get or generate CORS devices for the session"""
    if 'cors_devices' not in session:
        session['cors_devices'] = generate_cors_devices()
        print(f"CORS Demo: Generated {len(session['cors_devices'])} devices")
    return session['cors_devices']

def reset_cors_demo():
    """Reset CORS demo data"""
    session.pop('cors_devices', None)
    session.pop('cors_protection_enabled', None)
    session.pop('cors_attacks_logged', None)
    print("CORS Demo: Reset complete")

@cors_bp.route('/')
def dashboard():
    """Main CORS demo dashboard - Device Analytics"""
    devices = get_cors_devices()
    cors_protection = session.get('cors_protection_enabled', False)
    
    # Calculate basic statistics for the dashboard
    stats = {
        'total_devices': len(devices),
        'active_devices': len([d for d in devices if not d.get('jailbroken', False)]),
        'compliance_issues': len([d for d in devices if d.get('compliance_violations')]),
        'departments': len(set(d['department'] for d in devices)),
        'device_types': len(set(d['device_type'] for d in devices))
    }
    
    evil_domain = EVIL_DOMAIN
    
    return render_template('cors_device_analytics.html', 
                         devices=devices[:20],  # Show first 20 for display
                         stats=stats,
                         cors_protection_enabled=cors_protection,
                         evil_domain=evil_domain,
                         total_devices=len(devices))

@cors_bp.route('/api/devices')
def api_devices_basic():
    """Basic device list API - non-sensitive data"""
    devices = get_cors_devices()
    
    # Return only basic, non-sensitive information
    basic_devices = []
    for device in devices:
        basic_devices.append({
            "device_id": device["device_id"],
            "employee": device["employee"],
            "department": device["department"],
            "device_type": device["device_type"],
            "os_version": device["os_version"],
            "last_seen": device["last_seen"]
        })
    
    response = make_response(jsonify(basic_devices))
    
    # Always allow CORS for basic data (this is intentionally permissive)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

@cors_bp.route('/api/devices/detailed', methods=['GET', 'OPTIONS'])
def api_devices_detailed():
    """Detailed device API with sensitive data - CORS vulnerable/protected based on toggle"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        cors_protection = session.get('cors_protection_enabled', False)
        
        if cors_protection:
            # Protected mode - only allow MDM origin
            allowed_origin = request.url_root.rstrip('/')
            response.headers['Access-Control-Allow-Origin'] = allowed_origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        else:
            # Vulnerable mode - allow the requesting origin (not wildcard with credentials)
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
        
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Handle actual GET request
    devices = get_cors_devices()
    
    # Log potential attack
    request_origin = request.headers.get('Origin')
    if request_origin and EVIL_DOMAIN.rstrip('/') in request_origin:
        attacks = session.get('cors_attacks_logged', [])
        attacks.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'origin': request_origin,
            'endpoint': '/api/devices/detailed',
            'method': request.method,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        session['cors_attacks_logged'] = attacks
        print(f"CORS Attack detected from: {request_origin}")
    
    # Debug: Print CORS info
    cors_protection = session.get('cors_protection_enabled', False)
    
    print(f"=== CORS DEBUG ===")
    print(f"CORS Protection: {cors_protection}")
    print(f"Request Origin: {request_origin}")
    print(f"Request URL Root: {request.url_root}")
    print(f"Evil Domain: {EVIL_DOMAIN}")
    
    response = make_response(jsonify(devices))
    
    # CORS toggle logic for actual response
    if cors_protection:
        # Secure CORS - only allow same origin as the MDM system
        allowed_origin = request.url_root.rstrip('/')
        response.headers['Access-Control-Allow-Origin'] = allowed_origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        print(f"CORS Protected - Only allowing MDM origin: {allowed_origin}")
        
        # Additional check: if request is from evil domain, block it
        if request_origin and EVIL_DOMAIN.rstrip('/') in request_origin:
            print(f"⚠️ BLOCKING: Request from evil domain: {request_origin}")
            response.headers.pop('Access-Control-Allow-Origin', None)
            response.headers.pop('Access-Control-Allow-Credentials', None)
    else:
        # Vulnerable CORS - allow the specific requesting origin (not wildcard with credentials)
        if request_origin:
            response.headers['Access-Control-Allow-Origin'] = request_origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            print(f"CORS Vulnerable - Allowing requesting origin: {request_origin}")
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
            print("CORS Vulnerable - Allowing all origins (*)")
        
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    print(f"Response CORS headers: {dict(response.headers)}")
    print("==================")
    
    return response

@cors_bp.route('/api/devices/locations')
def api_devices_locations():
    """Device location API - highly sensitive data"""
    devices = get_cors_devices()
    
    # Extract location data
    location_data = []
    for device in devices:
        location_data.append({
            "device_id": device["device_id"],
            "employee": device["employee"],
            "location": device["location"],
            "last_seen": device["last_seen"],
            "phone_number": device["phone_number"]
        })
    
    response = make_response(jsonify(location_data))
    
    # Same CORS logic as detailed API
    cors_protection = session.get('cors_protection_enabled', False)
    
    if cors_protection:
        # Secure CORS - only allow same origin as the MDM system
        allowed_origin = request.url_root.rstrip('/')  # Only allow MDM's own origin
        response.headers['Access-Control-Allow-Origin'] = allowed_origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@cors_bp.route('/toggle-protection', methods=['POST'])
def toggle_cors_protection():
    """Toggle CORS protection on/off"""
    current = session.get('cors_protection_enabled', False)
    session['cors_protection_enabled'] = not current
    
    status = 'enabled' if session['cors_protection_enabled'] else 'disabled'
    print(f"CORS Protection {status}")
    
    return jsonify({
        'cors_protection': session['cors_protection_enabled'],
        'status': status,
        'message': f'CORS protection has been {status}'
    })

@cors_bp.route('/attacks')
def view_attacks():
    """View logged CORS attacks"""
    attacks = session.get('cors_attacks_logged', [])
    return jsonify(attacks)

@cors_bp.route('/reset')
def reset():
    """Reset CORS demo"""
    reset_cors_demo()
    return jsonify({'status': 'success', 'message': 'CORS demo reset successfully'})
