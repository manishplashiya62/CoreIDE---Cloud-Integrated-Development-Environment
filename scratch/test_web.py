import urllib.request
import urllib.parse
import json
import http.cookiejar

BASE_URL = "http://127.0.0.1:5000"

# Setup cookie jar to maintain session
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

def test_home():
    print("Testing Home page...")
    req = urllib.request.Request(BASE_URL)
    with urllib.request.urlopen(req) as res:
        html = res.read().decode('utf-8')
        assert "CoreIDE" in html, "Homepage does not contain CoreIDE"
    print("✓ Homepage OK")

def test_register():
    print("Testing Registration...")
    data = urllib.parse.urlencode({
        'username': 'test_dev_user',
        'email': 'test_dev@coreide.io',
        'password': 'password123',
        'confirm_password': 'password123'
    }).encode('utf-8')
    
    req = urllib.request.Request(f"{BASE_URL}/register", data=data)
    with urllib.request.urlopen(req) as res:
        # Should redirect or succeed
        assert res.getcode() == 200, "Registration failed"
    print("✓ Registration OK")

def test_login():
    print("Testing Login...")
    data = urllib.parse.urlencode({
        'username_or_email': 'test_dev_user',
        'password': 'password123'
    }).encode('utf-8')
    
    req = urllib.request.Request(f"{BASE_URL}/login", data=data)
    with urllib.request.urlopen(req) as res:
        assert res.getcode() == 200, "Login failed"
    print("✓ Login OK")

def test_create_project():
    print("Testing Project Creation...")
    payload = json.dumps({
        'project_name': 'python_test_project',
        'template': 'python'
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/projects", 
        data=payload, 
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        assert res.getcode() == 201, "Project creation failed"
        project = json.loads(res.read().decode('utf-8'))
        print("✓ Created project:", project)
        return project['id']

def test_get_project_tree(project_id):
    print(f"Testing Project Tree for ID {project_id}...")
    req = urllib.request.Request(f"{BASE_URL}/api/projects/{project_id}/tree")
    with urllib.request.urlopen(req) as res:
        assert res.getcode() == 200, "Project tree fetch failed"
        tree = json.loads(res.read().decode('utf-8'))
        print("✓ Project Tree:", tree)
        return tree[0]['id']

def test_run_code():
    print("Testing Code Run API...")
    payload = json.dumps({
        'language': 'python',
        'source_code': 'print("Hello from test suite!")',
        'stdin_data': ''
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/compiler/run",
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        assert res.getcode() == 200, "Compiler execution API failed"
        result = json.loads(res.read().decode('utf-8'))
        print("✓ Compilation result:", result)
        assert "Hello from test suite!" in result['stdout'], "Output mismatch"
    print("✓ Compiler execution OK")

def test_chatbot_api():
    print("Testing Chatbot API...")
    payload = json.dumps({
        'prompt': 'Explain this code',
        'code': 'print("Hello from test suite!")'
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/compiler/chat",
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        assert res.getcode() == 200, "Chatbot API failed"
        result = json.loads(res.read().decode('utf-8'))
        print("✓ Chatbot Response:", result)
        assert 'response' in result, "No response key in chatbot API result"
    print("✓ Chatbot API OK")

if __name__ == "__main__":
    try:
        test_home()
        # Since the database persists, registration might fail if user already exists.
        # We catch registration exceptions to keep tests idempotent.
        try:
            test_register()
        except Exception:
            print("! User already registered, skipping registration")
            
        test_login()
        p_id = test_create_project()
        f_id = test_get_project_tree(p_id)
        test_run_code()
        test_chatbot_api()
        print("\nAll Web API tests (including Chatbot) passed successfully!")
    except Exception as e:
        print("\nTest failed:", e)
        exit(1)

