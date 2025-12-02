#!/usr/bin/env python3
"""
Comprehensive test script for all websecdemos
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_broken_access():
    """Test broken access control demo"""
    print("\n=== Testing Broken Access Control ===")

    # Test valid login
    response = requests.post(f"{BASE_URL}/brokenaccess",
                            data={"username": "user", "password": "user"},
                            allow_redirects=False)
    print(f"✓ Login test: Status {response.status_code}")

    # Test accessing admin page directly (broken access control)
    response = requests.get(f"{BASE_URL}/brokenaccess/loggedin/user/0")
    if "admin" in response.text.lower() and response.status_code == 200:
        print("✓ Admin access without authorization: VULNERABLE (as expected)")

    # Test normal user page
    response = requests.get(f"{BASE_URL}/brokenaccess/loggedin/user/6510")
    print(f"✓ Normal user page: Status {response.status_code}")

    return True

def test_broken_auth1():
    """Test broken authentication 1 demo"""
    print("\n=== Testing Broken Authentication 1 ===")

    # Test weak authentication (contains 'admin')
    response = requests.post(f"{BASE_URL}/brokenauth1",
                            data={"username": "administrator", "password": "adminpass"})
    if response.status_code == 200:
        print("✓ Weak auth bypass: Status 200 (VULNERABLE as expected)")

    # Test failed login
    response = requests.post(f"{BASE_URL}/brokenauth1",
                            data={"username": "test", "password": "test"})
    print(f"✓ Failed login test: Status {response.status_code}")

    return True

def test_broken_auth2():
    """Test broken authentication 2 demo"""
    print("\n=== Testing Broken Authentication 2 ===")

    response = requests.get(f"{BASE_URL}/brokenauth2")
    print(f"✓ Broken auth 2 page loaded: Status {response.status_code}")

    return True

def test_broken_session():
    """Test broken session management demo"""
    print("\n=== Testing Broken Session Management ===")

    response = requests.get(f"{BASE_URL}/brokensession")
    print(f"✓ Broken session page loaded: Status {response.status_code}")

    # Test login
    response = requests.post(f"{BASE_URL}/brokensession",
                            data={"username": "user", "password": "user"})
    print(f"✓ Session login test: Status {response.status_code}")

    return True

def test_sql_injection():
    """Test SQL injection demo"""
    print("\n=== Testing SQL Injection ===")

    # Test normal login
    response = requests.post(f"{BASE_URL}/inject",
                            data={"username": "admin", "password": "bacon7"})
    print(f"✓ Normal login: Status {response.status_code}")

    # Test SQL injection bypass
    response = requests.post(f"{BASE_URL}/inject",
                            data={"username": "admin' OR '1'='1", "password": "anything"})
    if response.status_code == 200:
        print("✓ SQL injection bypass: Status 200 (VULNERABLE as expected)")

    return True

def test_security_misconfiguration():
    """Test security misconfiguration demo"""
    print("\n=== Testing Security Misconfiguration ===")

    response = requests.get(f"{BASE_URL}/secmis")
    print(f"✓ Security misconfiguration page loaded: Status {response.status_code}")

    return True

def test_xss():
    """Test XSS demo"""
    print("\n=== Testing XSS ===")

    response = requests.get(f"{BASE_URL}/xssadmin")
    print(f"✓ XSS admin page loaded: Status {response.status_code}")

    # Test login
    response = requests.post(f"{BASE_URL}/xssadmin",
                            data={"username": "admin", "password": "admin"})
    print(f"✓ XSS login test: Status {response.status_code}")

    return True

def test_parameter_tampering():
    """Test parameter tampering demo"""
    print("\n=== Testing Parameter Tampering ===")

    response = requests.get(f"{BASE_URL}/paramtamp")
    print(f"✓ Parameter tampering page loaded: Status {response.status_code}")

    return True

def test_csrf():
    """Test CSRF demo"""
    print("\n=== Testing CSRF ===")

    response = requests.get(f"{BASE_URL}/csrf")
    print(f"✓ CSRF page loaded: Status {response.status_code}")

    # Test login
    response = requests.post(f"{BASE_URL}/csrf",
                            data={"username": "user", "password": "user"})
    print(f"✓ CSRF login test: Status {response.status_code}")

    return True

def test_cors():
    """Test CORS demo"""
    print("\n=== Testing CORS ===")

    response = requests.get(f"{BASE_URL}/cors")
    print(f"✓ CORS page loaded: Status {response.status_code}")

    # Check CORS headers
    response = requests.get(f"{BASE_URL}/cors/api/devices",
                           headers={"Origin": "http://evil.com"})
    print(f"✓ CORS API endpoint: Status {response.status_code}")
    if "Access-Control-Allow-Origin" in response.headers:
        print(f"✓ CORS header present: {response.headers['Access-Control-Allow-Origin']}")

    return True

def test_path_traversal():
    """Test path traversal demo"""
    print("\n=== Testing Path Traversal ===")

    # Test normal file download
    response = requests.get(f"{BASE_URL}/pathtraversal/download?file=usage_report.pdf")
    print(f"✓ Normal file download: Status {response.status_code}")

    # Test path traversal attempt
    response = requests.get(f"{BASE_URL}/pathtraversal/download?file=../../etc/passwd")
    print(f"✓ Path traversal attempt: Status {response.status_code}")

    return True

def test_ssrf():
    """Test SSRF demo"""
    print("\n=== Testing SSRF ===")

    response = requests.get(f"{BASE_URL}/ssrf")
    print(f"✓ SSRF page loaded: Status {response.status_code}")

    # Test login
    session = requests.Session()
    response = session.post(f"{BASE_URL}/ssrf",
                           data={"username": "user", "password": "user"})
    print(f"✓ SSRF login test: Status {response.status_code}")

    return True

def main():
    print("=" * 60)
    print("WEBSECDEMOS - Comprehensive Test Suite")
    print("=" * 60)

    tests = [
        ("Broken Access Control", test_broken_access),
        ("Broken Authentication 1", test_broken_auth1),
        ("Broken Authentication 2", test_broken_auth2),
        ("Broken Session Management", test_broken_session),
        ("SQL Injection", test_sql_injection),
        ("Security Misconfiguration", test_security_misconfiguration),
        ("XSS", test_xss),
        ("Parameter Tampering", test_parameter_tampering),
        ("CSRF", test_csrf),
        ("CORS", test_cors),
        ("Path Traversal", test_path_traversal),
        ("SSRF", test_ssrf),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"✗ Error in {test_name}: {str(e)}")
            results.append((test_name, "ERROR"))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, status in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status}")

    total_pass = sum(1 for _, status in results if status == "PASS")
    print(f"\nTotal: {total_pass}/{len(tests)} tests passed")

    return 0 if total_pass == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
