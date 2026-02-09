import requests

try:
    response = requests.get('http://localhost:5005/api/projects', timeout=5)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Sucesso! {len(data)} projetos')
        if data:
            print(f'Primeiro: {data[0].get("nome", "Sem nome")}')
    else:
        print('Erro:', response.text[:500])
except Exception as e:
    print(f'Erro de conexão: {e}')
