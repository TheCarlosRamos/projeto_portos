import sqlite3
import os
import json

# Remover banco antigo
if os.path.exists('portos.db'):
    os.remove('portos.db')
    print('Banco antigo removido')

# Importar funções do app
from app import init_db, import_from_json

# Inicializar banco novo
init_db()
print('Banco novo inicializado')

# Importar dados
success = import_from_json()
print('Importação:', 'Sucesso' if success else 'Falha')

# Verificar resultado
conn = sqlite3.connect('portos.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM projetos')
count = cursor.fetchone()[0]
print(f'Projetos importados: {count}')

cursor.execute('PRAGMA table_info(projetos)')
columns = cursor.fetchall()
print('Colunas:', [col[1] for col in columns])

conn.close()
