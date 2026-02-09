import sys
import traceback
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('portos.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Erro conectando ao banco: {e}")
        raise

@app.route('/api/projects')
def get_projects():
    try:
        print("=== INICIANDO ENDPOINT COMPLETO ===")
        
        conn = get_db_connection()
        print("✓ Conexão OK")
        
        # Teste simples primeiro
        projetos = conn.execute('SELECT COUNT(*) FROM projetos').fetchone()
        print(f"✓ Count OK: {projetos[0]}")
        
        # Busca projetos
        projetos = conn.execute('SELECT * FROM projetos ORDER BY local, obj_concessao').fetchall()
        print(f"✓ Select OK: {len(projetos)} projetos")
        
        result = []
        
        for i, projeto in enumerate(projetos):
            try:
                print(f"\n--- Processando projeto {i} ---")
                projeto_dict = dict(projeto)
                
                # Busca serviços
                servicos = conn.execute('SELECT * FROM servicos WHERE projeto_id = ?', (projeto_dict['id'],)).fetchall()
                servicos_dict = [dict(s) for s in servicos] if servicos else []
                print(f"✓ Serviços OK: {len(servicos_dict)}")
                
                # Busca acompanhamentos
                acompanhamentos = conn.execute('SELECT * FROM acompanhamento WHERE projeto_id = ?', (projeto_dict['id'],)).fetchall()
                acompanhamentos_dict = [dict(a) for a in acompanhamentos] if acompanhamentos else []
                print(f"✓ Acompanhamentos OK: {len(acompanhamentos_dict)}")
                
                # Progresso
                progresso = 0
                if acompanhamentos_dict:
                    progresso = max([a.get('percentual_executada', 0) or 0 for a in acompanhamentos_dict])
                print(f"✓ Progresso OK: {progresso}")
                
                # Etapa
                etapa = 'Planejamento'
                if acompanhamentos_dict:
                    mais_recente = max(acompanhamentos_dict, key=lambda x: x.get('data_atualizacao', ''))
                    if mais_recente.get('fase'):
                        etapa = mais_recente['fase']
                    elif progresso > 0:
                        etapa = 'Em execução'
                    else:
                        etapa = 'Em andamento'
                print(f"✓ Etapa OK: {etapa}")
                
                # Coordenadas
                latitude = projeto_dict.get('latitude')
                longitude = projeto_dict.get('longitude')
                print(f"✓ Coordenadas: lat={latitude}, lon={longitude}")
                
                # Mapa (só se tiver coordenadas)
                mapa_embed = None
                coordenadas_lat_lon = None
                
                if latitude and longitude:
                    try:
                        lat_float = float(latitude)
                        lon_float = float(longitude)
                        coordenadas_lat_lon = {'lat': lat_float, 'lon': lon_float}
                        
                        bbox_size = 0.02
                        bbox = f"{lon_float-bbox_size},{lat_float-bbox_size},{lon_float+bbox_size},{lat_float+bbox_size}"
                        
                        mapa_embed = f'''
                            <div class="w-full h-full relative">
                                <iframe width="100%" height="100%" style="border:0; border-radius: 8px;" 
                                    src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat_float},{lon_float}" 
                                    frameborder="0" allowfullscreen>
                                </iframe>
                                <div class="absolute bottom-2 left-2 bg-white bg-opacity-90 px-2 py-1 rounded text-xs text-gray-700">
                                    📍 {lat_float:.6f}, {lon_float:.6f}
                                </div>
                            </div>
                        '''
                        print("✓ Mapa OK")
                    except Exception as map_error:
                        print(f"✗ Erro no mapa: {map_error}")
                        mapa_embed = None
                else:
                    print("✓ Sem coordenadas, mapa = None")
                
                # Nome do projeto
                local = projeto_dict.get('local') or 'Não informado'
                obj = projeto_dict.get('obj_concessao') or ''
                nome_projeto = local if local == 'Não se aplica' else f"{local} - {obj}"
                print(f"✓ Nome OK: {nome_projeto}")
                
                # Monta resultado
                projeto_result = {
                    'id': f"projeto-{projeto_dict['id']}",
                    'nome': nome_projeto,
                    'setor': projeto_dict.get('setor', ''),
                    'local': local,
                    'uf': projeto_dict.get('uf', ''),
                    'objConcessao': obj,
                    'tipo': projeto_dict.get('tipo', ''),
                    'capexTotal': projeto_dict.get('capex_total', 0),
                    'dataAssinatura': projeto_dict.get('data_assinatura'),
                    'descricao': projeto_dict.get('descricao', 'Sem descrição disponível'),
                    'progresso': progresso,
                    'etapa': etapa,
                    'servicos': servicos_dict,
                    'acompanhamentos': acompanhamentos_dict,
                    'mapaEmbed': mapa_embed,
                    'coordenadas': {
                        'e': projeto_dict.get('coordenada_e_utm'),
                        's': projeto_dict.get('coordenada_s_utm'),
                        'fuso': projeto_dict.get('fuso'),
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'coordenadasLatLon': coordenadas_lat_lon
                }
                
                result.append(projeto_result)
                print(f"✓ Projeto {i} adicionado ao resultado")
                
                # Limitar a 3 projetos para teste
                if i >= 2:
                    break
                    
            except Exception as proj_error:
                print(f"✗ Erro processando projeto {i}: {proj_error}")
                traceback.print_exc()
                continue
        
        conn.close()
        print(f"\n=== SUCESSO: Retornando {len(result)} projetos ===")
        return jsonify(result)
        
    except Exception as e:
        print(f"\n=== ERRO GERAL ===")
        print(f"Erro: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    print("Iniciando servidor de debug na porta 5005...")
    app.run(debug=True, host='0.0.0.0', port=5005)
