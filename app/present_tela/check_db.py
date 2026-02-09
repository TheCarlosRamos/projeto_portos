import sqlite3

conn = sqlite3.connect('portos.db')
cursor = conn.cursor()

# Verificar tabelas
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tabelas:', [t[0] for t in tables])

# Verificar dados
cursor.execute('SELECT COUNT(*) FROM projetos')
count = cursor.fetchone()[0]
print('Projetos:', count)

cursor.execute('SELECT COUNT(*) FROM servicos')
count = cursor.fetchone()[0]
print('Serviços:', count)

cursor.execute('SELECT COUNT(*) FROM acompanhamento')
count = cursor.fetchone()[0]
print('Acompanhamentos:', count)

if count > 0:
    cursor.execute('PRAGMA table_info(projetos)')
    columns = cursor.fetchall()
    print('Colunas projetos:', [col[1] for col in columns])

conn.close()
