import requests

try:
    response = requests.get('http://localhost:5000/api/projects', timeout=5)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'✓ Sucesso! {len(data)} projetos carregados')
        if data:
            print(f'Primeiro: {data[0].get("nome", "Sem nome")}')
            print(f'Setor: {data[0].get("setor", "N/A")}')
            print(f'Local: {data[0].get("local", "N/A")}')
    else:
        print('✗ Erro:', response.text[:500])
except Exception as e:
    print(f'Erro de conexão: {e}')
