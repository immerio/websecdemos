#!/usr/bin/env python3
"""
Evil server for CORS demo - runs on port 8080
This serves the complete Flask app from a different origin for CORS testing
"""

import sys
import os

# Add the main project directory to Python path
sys.path.append('/mnt/c/Users/JBLOMBE3/skrafsvscode/websecdemos')

# Import the complete Flask app
from demos import app

if __name__ == '__main__':
    print("Starting evil server (full app) on http://localhost:8080")
    print("Evil Benefits Portal: http://localhost:8080/benefits-portal")
    print("All demos available: http://localhost:8080/select")
    print("")
    print("For CORS demo testing:")
    print("- MDM System: http://127.0.0.1:5000/cors")
    print("- Evil Site: http://localhost:8080/benefits-portal")
    print("")
    app.run(host='localhost', port=8080, debug=True)
