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
        conn = get_db_connection()
        
        # Busca projetos com coordenadas
        projetos = conn.execute('SELECT * FROM projetos WHERE latitude IS NOT NULL AND longitude IS NOT NULL LIMIT 1').fetchall()
        
        result = []
        
        for projeto in projetos:
            projeto_dict = dict(projeto)
            
            # Teste específico do mapa
            latitude = projeto_dict['latitude']
            longitude = projeto_dict['longitude']
            
            print(f"Coordenadas: lat={latitude} (type: {type(latitude)}), lon={longitude} (type: {type(longitude)})")
            
            mapa_embed = None
            coordenadas_lat_lon = None
            
            if latitude and longitude:
                try:
                    coordenadas_lat_lon = {
                        'lat': float(latitude),
                        'lon': float(longitude)
                    }
                    
                    bbox_size = 0.02
                    bbox = f"{float(longitude)-bbox_size},{float(latitude)-bbox_size},{float(longitude)+bbox_size},{float(latitude)+bbox_size}"
                    
                    mapa_embed = f'''
                        <div class="w-full h-full relative">
                            <iframe 
                                width="100%" 
                                height="100%" 
                                style="border:0; border-radius: 8px;" 
                                src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={float(latitude)},{float(longitude)}" 
                                frameborder="0"
                                allowfullscreen>
                            </iframe>
                            <div class="absolute bottom-2 left-2 bg-white bg-opacity-90 px-2 py-1 rounded text-xs text-gray-700">
                                📍 {float(latitude):.6f}, {float(longitude):.6f}
                            </div>
                        </div>
                    '''
                    print("Mapa embed gerado com sucesso")
                except Exception as e:
                    print(f"Erro gerando mapa: {e}")
                    mapa_embed = None
            
            result.append({
                'id': f"projeto-{projeto_dict['id']}",
                'nome': f"Teste Mapa {projeto_dict['id']}",
                'setor': projeto_dict.get('setor', ''),
                'local': projeto_dict.get('local', ''),
                'uf': projeto_dict.get('uf', ''),
                'objConcessao': projeto_dict.get('obj_concessao', ''),
                'tipo': projeto_dict.get('tipo', ''),
                'capexTotal': projeto_dict.get('capex_total', 0),
                'dataAssinatura': projeto_dict.get('data_assinatura'),
                'descricao': projeto_dict.get('descricao', ''),
                'progresso': 0,
                'etapa': 'Teste Mapa',
                'servicos': [],
                'acompanhamentos': [],
                'mapaEmbed': mapa_embed,
                'coordenadas': {
                    'e': projeto_dict.get('coordenada_e_utm'),
                    's': projeto_dict.get('coordenada_s_utm'),
                    'fuso': projeto_dict.get('fuso'),
                    'latitude': latitude,
                    'longitude': longitude
                },
                'coordenadasLatLon': coordenadas_lat_lon
            })
            break
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
