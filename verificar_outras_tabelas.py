import sqlite3

conn = sqlite3.connect('app/present_tela/portos.db')
cursor = conn.cursor()

print("=== ESTRUTURA DA TABELA servicos ===")
cursor.execute("PRAGMA table_info(servicos);")
columns = cursor.fetchall()
for col in columns:
    print(f"- {col[1]} ({col[2]})")

print("\n=== ESTRUTURA DA TABELA acompanhamento ===")
cursor.execute("PRAGMA table_info(acompanhamento);")
columns = cursor.fetchall()
for col in columns:
    print(f"- {col[1]} ({col[2]})")

print("\n=== PRIMEIRO REGISTRO DA TABELA servicos ===")
cursor.execute("SELECT * FROM servicos LIMIT 1;")
row = cursor.fetchone()
if row:
    print(f"Registro: {row}")
else:
    print("Nenhum registro encontrado")

print("\n=== PRIMEIRO REGISTRO DA TABELA acompanhamento ===")
cursor.execute("SELECT * FROM acompanhamento LIMIT 1;")
row = cursor.fetchone()
if row:
    print(f"Registro: {row}")
else:
    print("Nenhum registro encontrado")

conn.close()
