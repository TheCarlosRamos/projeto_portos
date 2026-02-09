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
        
        # Busca projetos
        projetos = conn.execute('SELECT * FROM projetos ORDER BY local, obj_concessao').fetchall()
        print(f"Encontrados {len(projetos)} projetos")
        
        result = []
        
        for i, projeto in enumerate(projetos):
            try:
                print(f"Processando projeto {i}: ID {projeto['id']}")
                # Converte Row para dict
                projeto_dict = dict(projeto)
                print(f"Projeto dict: {list(projeto_dict.keys())}")
                
                # Busca serviços do projeto
                servicos = conn.execute('SELECT * FROM servicos WHERE projeto_id = ?', (projeto_dict['id'],)).fetchall()
                print(f"Serviços encontrados: {len(servicos)}")
                
                # Busca acompanhamentos do projeto
                acompanhamentos = conn.execute('SELECT * FROM acompanhamento WHERE projeto_id = ?', (projeto_dict['id'],)).fetchall()
                print(f"Acompanhamentos encontrados: {len(acompanhamentos)}")
                
                # Converte para dict
                acompanhamentos_dict = [dict(a) for a in acompanhamentos] if acompanhamentos else []
                servicos_dict = [dict(s) for s in servicos] if servicos else []
                
                # Dados básicos para teste
                result.append({
                    'id': f"projeto-{projeto_dict['id']}",
                    'nome': f"Teste {projeto_dict['id']}",
                    'setor': projeto_dict.get('setor', ''),
                    'local': projeto_dict.get('local', ''),
                    'uf': projeto_dict.get('uf', ''),
                    'objConcessao': projeto_dict.get('obj_concessao', ''),
                    'tipo': projeto_dict.get('tipo', ''),
                    'capexTotal': projeto_dict.get('capex_total', 0),
                    'dataAssinatura': projeto_dict.get('data_assinatura'),
                    'descricao': projeto_dict.get('descricao', 'Sem descrição'),
                    'progresso': 0,
                    'etapa': 'Teste',
                    'servicos': servicos_dict,
                    'acompanhamentos': acompanhamentos_dict
                })
                
                if i >= 2:  # Limitar para teste
                    break
                    
            except Exception as e:
                print(f"Erro processando projeto {i}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        conn.close()
        print(f"Retornando {len(result)} projetos")
        return jsonify(result)
        
    except Exception as e:
        print(f"Erro geral no endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
