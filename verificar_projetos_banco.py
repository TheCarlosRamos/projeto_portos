import sqlite3

conn = sqlite3.connect('app/present_tela/portos.db')
cursor = conn.cursor()

print("=== TODOS OS PROJETOS NO BANCO ===")
cursor.execute("""
    SELECT id, zona_portuaria, uf, obj_concessao, tipo, descricao, 
           capex_total, capex_executado, perc_capex_executado
    FROM projetos
    ORDER BY id
""")

rows = cursor.fetchall()
for i, row in enumerate(rows):
    print(f"\nProjeto {i+1} (ID: {row[0]}):")
    print(f"  Zona: {row[1]}")
    print(f"  UF: {row[2]}")
    print(f"  Obj: {row[3]}")
    print(f"  Tipo: {row[4]}")
    print(f"  Desc: {row[5]}")
    print(f"  CAPEX: R${row[6]/1000000:.1f}M" if row[6] else "  CAPEX: N/A")
    print(f"  Executado: R${row[7]/1000000:.1f}M" if row[7] else "  Executado: N/A")
    print(f"  % Exec: {row[8]*100:.1f}%" if row[8] else "  % Exec: N/A")

conn.close()
