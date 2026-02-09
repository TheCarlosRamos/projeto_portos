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
        print("=== INICIANDO DEBUG ===")
        conn = get_db_connection()
        
        # Busca projetos
        projetos = conn.execute('SELECT * FROM projetos ORDER BY local, obj_concessao').fetchall()
        print(f"Projetos encontrados: {len(projetos)}")
        
        result = []
        
        for i, projeto in enumerate(projetos):
            try:
                print(f"\n--- Processando projeto {i} ---")
                projeto_dict = dict(projeto)
                print(f"ID: {projeto_dict['id']}")
                
                # Teste apenas um projeto
                if i == 0:
                    print("Campos do projeto:", list(projeto_dict.keys()))
                    print(f"Setor: {projeto_dict.get('setor')}")
                    print(f"Local: {projeto_dict.get('local')}")
                    print(f"Latitude: {projeto_dict.get('latitude')} (type: {type(projeto_dict.get('latitude'))})")
                    print(f"Longitude: {projeto_dict.get('longitude')} (type: {type(projeto_dict.get('longitude'))})")
                    
                    # Testar formatação
                    lat = projeto_dict.get('latitude')
                    lon = projeto_dict.get('longitude')
                    if lat and lon:
                        try:
                            formatted = f"{float(lat):.6f}, {float(lon):.6f}"
                            print(f"Formatação OK: {formatted}")
                        except Exception as e:
                            print(f"ERRO NA FORMATAÇÃO: {e}")
                            return jsonify({"error": f"Formatação error: {e}"}), 500
                    
                    # Criar resultado mínimo
                    result.append({
                        'id': f"projeto-{projeto_dict['id']}",
                        'nome': f"Projeto {projeto_dict['id']}",
                        'setor': projeto_dict.get('setor', ''),
                        'local': projeto_dict.get('local', ''),
                        'uf': projeto_dict.get('uf', ''),
                        'objConcessao': projeto_dict.get('obj_concessao', ''),
                        'tipo': projeto_dict.get('tipo', ''),
                        'capexTotal': projeto_dict.get('capex_total', 0),
                        'dataAssinatura': projeto_dict.get('data_assinatura'),
                        'descricao': projeto_dict.get('descricao', ''),
                        'progresso': 0,
                        'etapa': 'Teste',
                        'servicos': [],
                        'acompanhamentos': [],
                        'mapaEmbed': None,
                        'coordenadas': {},
                        'coordenadasLatLon': None
                    })
                    break
                    
            except Exception as e:
                print(f"Erro processando projeto {i}: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"Project {i} error: {e}"}), 500
        
        conn.close()
        print(f"\n=== RETORNANDO {len(result)} PROJETOS ===")
        return jsonify(result)
        
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"General error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
