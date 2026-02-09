import requests

try:
    response = requests.get('http://localhost:5000/api/projects')
    print(f'Status: {response.status_code}')
    print(f'Content-Type: {response.headers.get("content-type", "Not set")}')
    print('First 200 chars:')
    print(response.text[:200])
except Exception as e:
    print(f'Error: {e}')
