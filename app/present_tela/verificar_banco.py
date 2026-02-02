import sqlite3

conn = sqlite3.connect('portos.db')
cursor = conn.cursor()

print("=== TABELAS DO BANCO ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n=== ESTRUTURA DA TABELA projetos ===")
cursor.execute("PRAGMA table_info(projetos);")
columns = cursor.fetchall()
for col in columns:
    print(f"- {col[1]} ({col[2]})")

print("\n=== PRIMEIROS 2 REGISTROS DA TABELA projetos ===")
cursor.execute("SELECT * FROM projetos LIMIT 2;")
rows = cursor.fetchall()
for i, row in enumerate(rows):
    print(f"Registro {i+1}: {row}")

conn.close()
