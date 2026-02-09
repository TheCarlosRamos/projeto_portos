import sqlite3
import json
from flask import Flask, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('portos.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/projects')
def get_projects():
    try:
        print("Iniciando endpoint /api/projects")
        conn = get_db_connection()
        print("Conexão com banco estabelecida")
        
        # Teste simples
        projetos = conn.execute('SELECT COUNT(*) FROM projetos').fetchone()
        print(f"Total projetos: {projetos[0]}")
        
        # Busca projetos
        projetos = conn.execute('SELECT * FROM projetos LIMIT 1').fetchall()
        print(f"Primeiro projeto: {dict(projetos[0]) if projetos else 'Nenhum'}")
        
        conn.close()
        
        return jsonify({"test": "ok", "count": projetos[0][0] if projetos else 0})
        
    except Exception as e:
        print(f"Erro no endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
