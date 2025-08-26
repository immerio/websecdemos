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
    
    # Employee names with realistic variety
    employees = [
        "Sarah Connor", "John Matrix", "Ellen Ripley", "James Bond", "Lara Croft",
        "Ethan Hunt", "Alice Resident", "Leon Kennedy", "Jill Valentine", "Chris Redfield",
        "Ada Wong", "Claire Redfield", "Rebecca Chambers", "Barry Burton", "Albert Wesker",
        "Jack Ryan", "Jason Bourne", "John Rambo", "Dutch Schaefer", "Ripley Ellen",
        "Trinity Anderson", "Neo Anderson", "Morpheus Captain", "Agent Smith", "Niobe Captain",
        "Max Rockatansky", "Furiosa Imperator", "Rick Deckard", "Roy Batty", "Rachel Tyrell",
        "John Connor", "Kyle Reese", "T-800 Model", "Marcus Wright", "Kate Connor",
        "Diana Prince", "Bruce Wayne", "Clark Kent", "Barry Allen", "Arthur Curry",
        "Victor Stone", "Hal Jordan", "Oliver Queen", "Dinah Lance", "Zatanna Zatara"
    ]
    
    # Device types with realistic distribution
    device_types = [
        "iPhone 15 Pro", "iPhone 15", "iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro",
        "Samsung Galaxy S24", "Samsung Galaxy S23", "Samsung Galaxy A54", "Google Pixel 8",
        "Google Pixel 7", "OnePlus 11", "Xiaomi 13 Pro", "iPad Pro 12.9", "iPad Air",
        "Samsung Galaxy Tab S9", "Surface Pro 9", "MacBook Air M2", "MacBook Pro M3",
        "Dell Latitude 5530", "HP EliteBook 850", "Lenovo ThinkPad X1", "Surface Laptop 5"
    ]
    
    # Departments for realistic organizational structure
    departments = [
        "Engineering", "Sales", "Marketing", "HR", "Finance", "Legal", "Operations",
        "Customer Support", "Product", "Security", "IT", "Executive", "Research"
    ]
    
    # Apps commonly found on corporate devices
    app_lists = [
        ["Slack", "Outlook", "Teams", "VPN Client", "Authenticator"],
        ["Zoom", "Gmail", "Chrome", "Dropbox", "1Password"],
        ["Salesforce", "Jira", "Confluence", "Tableau", "Office 365"],
        ["WhatsApp", "LinkedIn", "Adobe Reader", "Spotify", "Netflix"],
        ["Banking App", "Uber", "Maps", "Calendar", "Notes"],
        ["CRM Mobile", "Expense Tracker", "Project Tracker", "Time Logger", "Scanner"]
    ]
    
    # Compliance violations for realism
    violations = [
        "Location services disabled", "Outdated OS version", "Jailbroken device detected",
        "Weak passcode", "Auto-lock disabled", "VPN not configured", "Encryption disabled",
        "Unknown app installed", "Developer mode enabled", "Debug mode active"
    ]
    
    devices = []
    used_imeis = set()
    used_phones = set()
    
    # Generate exactly 385 devices (different from CSRF's 932 for isolation)
    for i in range(385):
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
        
        # Generate realistic location coordinates (major US cities)
        locations = [
            "37.7749,-122.4194",  # San Francisco
            "40.7128,-74.0060",   # New York
            "34.0522,-118.2437",  # Los Angeles
            "41.8781,-87.6298",   # Chicago
            "29.7604,-95.3698",   # Houston
            "33.4484,-112.0740",  # Phoenix
            "39.9526,-75.1652",   # Philadelphia
            "32.7767,-96.7970",   # Dallas
            "30.2672,-97.7431",   # Austin
            "25.7617,-80.1918"    # Miami
        ]
        
        device = {
            "device_id": f"CORS-DEV-{i+1:04d}",
            "employee": random.choice(employees),
            "department": random.choice(departments),
            "device_type": random.choice(device_types),
            "phone_number": phone,
            "imei": imei,
            "serial_number": f"C{random.randint(100000000, 999999999)}",
            "location": random.choice(locations),
            "installed_apps": random.choice(app_lists),
            "last_backup": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S"),
            "os_version": random.choice(["iOS 17.1", "iOS 16.7", "Android 14", "Android 13", "Windows 11"]),
            "encryption_status": random.choice(["enabled", "disabled"]),
            "jailbroken": random.choice([False, False, False, True]),  # Mostly not jailbroken
            "compliance_violations": random.sample(violations, random.randint(0, 2)),
            "emergency_contacts": [f"+1-555-{random.randint(1000, 9999)}", f"+1-555-{random.randint(1000, 9999)}"],
            "last_seen": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S"),
            "battery_level": random.randint(15, 100),
            "storage_used": f"{random.randint(32, 256)}GB",
            "network_info": random.choice(["WiFi", "Cellular", "VPN"]),
            "device_value": f"${random.randint(500, 1500)}"
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
