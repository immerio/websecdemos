import requests, pytest, subprocess

base_url = "http://127.0.0.1:5000/"

def checkGet(path):
    response = requests.get(base_url + path)
    assert response.status_code == 200 

def checkPost(path, post_data):
    response = requests.post(base_url + path, data=post_data)
    assert response.status_code == 200     

def test_inject():
    checkGet("inject")

def test_inject_post():
    post_data = {'username':'test','password':'test'}
    checkPost("inject", post_data)

def test_brokenauth1():
    checkGet("brokenauth1")
    
def test_brokenauth2():
    checkGet("brokenauth2")

def test_brokenaccess():
    checkGet("brokenaccess")

def test_brokenaccess_user_0():
    checkGet("brokenaccess/loggedin/user/0")    

def test_brokenaccess_user_6510():
    checkGet("brokenaccess/loggedin/user/6510")

def test_brokensession():
    checkGet("brokensession")

def test_secmis():
    checkGet("secmis")

def test_secmis_admin():
    checkGet("secmis/admin")    

def test_xss_contact():
    checkGet("xsscontact")

def test_xss_admin():
    checkGet("xssadmin")

def test_xss_admin_post():
    post_data = {'username':'Administrator','password':'admin'}
    checkPost("xssadmin", post_data)

def test_xss_evillog():
    checkGet("evillog")

def getTestresults():
    pytest_command_string = 'pytest -q'
    pytest_command = subprocess.Popen(pytest_command_string.split(), shell=False, stdout=subprocess.PIPE)
    pytest_command_out = pytest_command.communicate()[0]

    return pytest_command_out.decode("utf-8")