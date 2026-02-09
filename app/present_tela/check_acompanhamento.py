import sqlite3

conn = sqlite3.connect('portos.db')
cursor = conn.cursor()

# Verificar estrutura da tabela acompanhamento
cursor.execute('PRAGMA table_info(acompanhamento)')
columns = cursor.fetchall()
print('Colunas acompanhamento:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

conn.close()
