#!/usr/bin/env python3
"""
Evil server for CORS demo - runs on port 8080
This serves the complete Flask app from a different origin for CORS testing
"""

import sys
import os
from urllib.parse import urlparse

# Add the main project directory to Python path
sys.path.append('/mnt/c/Users/JBLOMBE3/skrafsvscode/websecdemos')

# Import the complete Flask app
from demos import app

def parse_host_url(host_url, default_host='localhost', default_port=8080):
    """Parse a host URL like http://localhost:8080 or https://example.com"""
    try:
        if not host_url:
            return default_host, default_port
            
        parsed = urlparse(host_url)
        host = parsed.hostname or default_host
        port = parsed.port or (443 if parsed.scheme == 'https' else default_port)
        return host, port
    except:
        return default_host, default_port

if __name__ == '__main__':
    # Get configuration from environment
    #evil_host_url = os.getenv('EVIL_HOST', 'http://localhost:8080')
    #mdm_host_url = os.getenv('MDM_HOST', 'http://localhost:5000')
    evil_host_url ='http://localhost:8080'
    mdm_host_url = 'http://localhost:5000'
    
    # Parse the URLs
    evil_host, evil_port = parse_host_url(evil_host_url, 'localhost', 8080)
    mdm_host, mdm_port = parse_host_url(mdm_host_url, 'localhost', 5000)
    
    print(f"Starting evil server (full app) on {evil_host_url}")
    print(f"Evil Benefits Portal: {evil_host_url}/benefits-portal")
    print(f"All demos available: {evil_host_url}/select")
    print("")
    print("For CORS demo testing:")
    print(f"- MDM System: {mdm_host_url}/cors")
    print(f"- Evil Site: {evil_host_url}/benefits-portal")
    print("")
    app.run(host=evil_host, port=evil_port, debug=True)
