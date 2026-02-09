#!/usr/bin/env python3
"""
API Flask para Gestão de Concessões Portuárias
Integra banco de dados com frontend HTML
"""

from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Configurações
DATABASE = 'portos.db'
JSON_FILE = 'planilha_portos.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Banco de Dados ---------------------------------------------------------

def init_db():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de projetos (Cadastro)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setor TEXT,
            local TEXT,
            uf TEXT,
            obj_concessao TEXT,
            tipo TEXT CHECK(tipo IN ('Concessão', 'Arrendamento', 'Autorização') OR tipo IS NULL),
            capex_total REAL,
            capex_executado REAL,
            perc_capex_executado REAL CHECK(perc_capex_executado IS NULL OR (perc_capex_executado >= 0 AND perc_capex_executado <= 1)),
            data_assinatura TEXT,
            descricao TEXT,
            latitude REAL,
            longitude REAL,
            coordenada_e_utm REAL,
            coordenada_s_utm REAL,
            fuso INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(local, obj_concessao)
        )
    ''')
    
    # Tabela de serviços
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            local TEXT,
            uf TEXT,
            obj_concessao TEXT,
            tipo_servico TEXT,
            fase TEXT,
            servico TEXT,
            descricao_servico TEXT,
            prazo_inicio_anos REAL,
            data_inicio TEXT,
            prazo_final_anos REAL,
            data_final TEXT,
            fonte_prazo TEXT,
            percentual_capex REAL,
            capex_servico REAL,
            capex_servico_exec REAL,
            perc_capex_exec REAL,
            fonte_percentual TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')
    
    # Tabela de acompanhamento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acompanhamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            local TEXT,
            uf TEXT,
            obj_concessao TEXT,
            tipo_servico TEXT,
            fase TEXT,
            servico TEXT,
            descricao TEXT,
            percentual_executada REAL,
            valor_executado REAL,
            data_atualizacao TEXT,
            responsavel TEXT,
            cargo TEXT,
            setor TEXT,
            setor2 TEXT,
            riscos_tipo TEXT,
            riscos_descricao TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Importação de Dados ----------------------------------------------------

def import_from_json():
    """Importa dados do JSON para o banco de dados"""
    if not Path(JSON_FILE).exists():
        return False
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Limpa tabelas
    cursor.execute('DELETE FROM acompanhamento')
    cursor.execute('DELETE FROM servicos')
    cursor.execute('DELETE FROM projetos')
    
    # Importa projetos
    cadastros = data.get('Tabela 00 - Cadastro', [])
    for cadastro in cadastros:
        cursor.execute('''
            INSERT INTO projetos (
                setor, local, uf, obj_concessao, tipo, capex_total,
                capex_executado, perc_capex_executado, data_assinatura, descricao, latitude, longitude,
                coordenada_e_utm, coordenada_s_utm, fuso
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cadastro.get('Setor'),
            cadastro.get('Local'),
            cadastro.get('UF'),
            cadastro.get('Obj. de Concessão'),
            cadastro.get('Tipo'),
            cadastro.get('CAPEX Total'),
            cadastro.get('CAPEX Executado'),
            cadastro.get('% CAPEX Executado'),
            cadastro.get('Data de assinatura do contrato'),
            cadastro.get('Descrição'),
            cadastro.get('Latitude'),
            cadastro.get('Longitude'),
            cadastro.get('Coordenada E (UTM)'),
            cadastro.get('Coordenada S (UTM)'),
            cadastro.get('Fuso')
        ))
        
        projeto_id = cursor.lastrowid
        
        # Importa serviços relacionados
        servicos = data.get('Tabela 01 - Serviços', [])
        servicos_projeto = [
            s for s in servicos 
            if s.get('Local') == cadastro.get('Local') and
               s.get('UF') == cadastro.get('UF') and
               s.get('Obj. de Concessão') == cadastro.get('Obj. de Concessão')
        ]
        
        for servico in servicos_projeto:
            cursor.execute('''
                INSERT INTO servicos (
                    projeto_id, local, uf, obj_concessao,
                    tipo_servico, fase, servico, descricao_servico,
                    prazo_inicio_anos, data_inicio, prazo_final_anos, data_final,
                    fonte_prazo, percentual_capex, capex_servico, capex_servico_exec, perc_capex_exec, fonte_percentual
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                projeto_id,
                servico.get('Local'),
                servico.get('UF'),
                servico.get('Obj. de Concessão'),
                servico.get('Tipo de Serviço'),
                servico.get('Fase'),
                servico.get('Serviço'),
                servico.get('Descrição do serviço'),
                servico.get('Prazo início (anos)'),
                servico.get('Data de início'),
                servico.get('Prazo final (anos)'),
                servico.get('Data final'),
                servico.get('Fonte (Prazo)'),
                servico.get('% de CAPEX para o serviço'),
                servico.get('CAPEX do Serviço'),
                servico.get('CAPEX do Serviço (exec.)'),
                servico.get('% CAPEX exec.'),
                servico.get('Fonte (% do CAPEX)')
            ))
        
        # Importa acompanhamentos relacionados
        acompanhamentos = data.get('Tabela 02 - Acompanhamento', [])
        acompanhamentos_projeto = [
            a for a in acompanhamentos
            if a.get('Local') == cadastro.get('Local') and
               a.get('UF') == cadastro.get('UF') and
               a.get('Obj. de Concessão') == cadastro.get('Obj. de Concessão')
        ]
        
        for acomp in acompanhamentos_projeto:
            cursor.execute('''
                INSERT INTO acompanhamento (
                    projeto_id, local, uf, obj_concessao,
                    tipo_servico, fase, servico, descricao,
                    percentual_executada, valor_executado, data_atualizacao,
                    responsavel, cargo, setor, setor2, riscos_tipo, riscos_descricao, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                projeto_id,
                acomp.get('Local'),
                acomp.get('UF'),
                acomp.get('Obj. de Concessão'),
                acomp.get('Tipo de Serviço'),
                acomp.get('Fase'),
                acomp.get('Serviço'),
                acomp.get('Descrição'),
                acomp.get('% executada'),
                acomp.get('Valor executado'),
                acomp.get('Data da atualização'),
                acomp.get('Responsável'),
                acomp.get('Cargo'),
                acomp.get('Setor'),
                acomp.get('Setor2'),
                acomp.get('Riscos Relacionados (Tipo)'),
                acomp.get('Riscos Relacionados (Descrição)')
            ))
    
    conn.commit()
    conn.close()
    return True

# --- API Endpoints ----------------------------------------------------------

@app.route('/')
def index():
    """Serve a página HTML principal"""
    return send_from_directory('.', 'portos.html')

@app.route('/api/projects')
def get_projects():
    """Retorna todos os projetos no formato esperado pelo frontend"""
    try:
        conn = get_db_connection()
        
        # Busca projetos
        projetos = conn.execute('SELECT * FROM projetos ORDER BY local, obj_concessao').fetchall()
        
        result = []
        
        for projeto in projetos:
            projeto_dict = dict(projeto)
            
            # Busca serviços do projeto
            servicos = conn.execute('SELECT * FROM servicos WHERE projeto_id = ?', (projeto_dict['id'],)).fetchall()
            servicos_dict = [dict(s) for s in servicos] if servicos else []
            
            # Busca acompanhamentos do projeto
            acompanhamentos = conn.execute('SELECT * FROM acompanhamento WHERE projeto_id = ?', (projeto_dict['id'],)).fetchall()
            acompanhamentos_dict = [dict(a) for a in acompanhamentos] if acompanhamentos else []
            
            # Calcula progresso baseado nos acompanhamentos
            progresso = 0
            if acompanhamentos_dict:
                progresso = max([a.get('percentual_executada', 0) or 0 for a in acompanhamentos_dict])
            
            # Determina etapa baseada nos acompanhamentos
            etapa = 'Planejamento'
            if acompanhamentos_dict:
                # Pega o acompanhamento mais recente
                mais_recente = max(acompanhamentos_dict, key=lambda x: x.get('data_atualizacao', ''))
                if mais_recente.get('fase'):
                    etapa = mais_recente['fase']
                elif progresso > 0:
                    etapa = 'Em execução'
                else:
                    etapa = 'Em andamento'
            
            # Coordenadas
            latitude = projeto_dict.get('latitude')
            longitude = projeto_dict.get('longitude')
            
            # Mapa (só se tiver coordenadas válidas)
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
                except Exception:
                    mapa_embed = None
            
            # Nome do projeto
            local = projeto_dict.get('local') or 'Não informado'
            obj = projeto_dict.get('obj_concessao') or ''
            nome_projeto = local if local == 'Não se aplica' else f"{local} - {obj}"
            
            result.append({
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
            })
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/import', methods=['POST'])
def import_data():
    """Importa dados do JSON para o banco"""
    try:
        success = import_from_json()
        if success:
            return jsonify({'message': 'Dados importados com sucesso!'})
        else:
            return jsonify({'error': 'Arquivo JSON não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Cria um novo projeto"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO projetos (
                zona_portuaria, uf, obj_concessao, tipo, capex_total,
                capex_executado, perc_capex_executado, data_assinatura, descricao, latitude, longitude,
                coordenada_e_utm, coordenada_s_utm, fuso
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('zona_portuaria'),
            data.get('uf'),
            data.get('obj_concessao'),
            data.get('tipo'),
            data.get('capex_total'),
            data.get('capex_executado'),
            data.get('perc_capex_executado'),
            data.get('data_assinatura'),
            data.get('descricao'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('coordenada_e_utm'),
            data.get('coordenada_s_utm'),
            data.get('fuso')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Projeto criado com sucesso!',
            'id': cursor.lastrowid
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/<int:projeto_id>')
def get_project(projeto_id):
    """Retorna um projeto específico no formato esperado pelo frontend"""
    conn = get_db_connection()
    
    # Busca o projeto
    projeto = conn.execute('SELECT * FROM projetos WHERE id = ?', (projeto_id,)).fetchone()
    
    if not projeto:
        return jsonify({'error': 'Projeto não encontrado'}), 404
    
    # Converte para dict
    projeto_dict = dict(projeto)
    
    # Busca serviços do projeto
    servicos = conn.execute('''
        SELECT * FROM servicos WHERE projeto_id = ?
    ''', (projeto_dict['id'],)).fetchall()
    
    # Busca acompanhamentos do projeto
    acompanhamentos = conn.execute('''
        SELECT * FROM acompanhamento WHERE projeto_id = ?
    ''', (projeto_dict['id'],)).fetchall()
    
    # Converte para dict
    acompanhamentos_dict = [dict(a) for a in acompanhamentos] if acompanhamentos else []
    servicos_dict = [dict(s) for s in servicos] if servicos else []
    
    # Calcula progresso baseado nos acompanhamentos
    progresso = 0
    if acompanhamentos_dict:
        progresso = max([a.get('percentual_executada', 0) or 0 for a in acompanhamentos_dict])
    
    # Determina etapa baseada nos acompanhamentos
    etapa = 'Planejamento'
    if acompanhamentos_dict:
        # Pega o acompanhamento mais recente
        mais_recente = max(acompanhamentos_dict, key=lambda x: x.get('data_atualizacao', ''))
        if mais_recente.get('fase'):
            etapa = mais_recente['fase']
        elif progresso > 0:
            etapa = 'Em execução'
        else:
            etapa = 'Em andamento'
    
    # Prepara coordenadas
    latitude = projeto_dict['latitude']
    longitude = projeto_dict['longitude']
    
    # Gera mapa se tiver coordenadas
    mapa_embed = None
    coordenadas_lat_lon = None
    
    if latitude and longitude:
        coordenadas_lat_lon = {
            'lat': latitude,
            'lon': longitude
        }
        
        bbox_size = 0.02
        bbox = f"{longitude-bbox_size},{latitude-bbox_size},{longitude+bbox_size},{latitude+bbox_size}"
        
        mapa_embed = f'''
            <div class="w-full h-full relative">
                <iframe 
                    width="100%" 
                    height="100%" 
                    style="border:0; border-radius: 8px;" 
                    src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={latitude},{longitude}" 
                    frameborder="0"
                    allowfullscreen>
                </iframe>
                <div class="absolute bottom-2 left-2 bg-white bg-opacity-90 px-2 py-1 rounded text-xs text-gray-700">
                    📍 {latitude:.6f}, {longitude:.6f}
                </div>
            </div>
        '''
    
    # Nome do projeto
    zona = projeto_dict['zona_portuaria'] or 'Não informado'
    obj = projeto_dict['obj_concessao'] or ''
    nome_projeto = zona if zona == 'Não se aplica' else f"{zona} - {obj}"
    
    result = {
        'id': f"projeto-{projeto_dict['id']}",
        'nome': nome_projeto,
        'zona': zona,
        'uf': projeto_dict['uf'] or '',
        'objConcessao': obj,
        'tipo': projeto_dict['tipo'] or '',
        'capexTotal': projeto_dict['capex_total'] or 0,
        'dataAssinatura': projeto_dict['data_assinatura'],
        'descricao': projeto_dict['descricao'] or 'Sem descrição disponível',
        'progresso': progresso,
        'etapa': etapa,
        'servicos': servicos_dict,
        'acompanhamentos': acompanhamentos_dict,
        'mapaEmbed': mapa_embed,
        'coordenadas': {
            'e': projeto_dict['coordenada_e_utm'],
            's': projeto_dict['coordenada_s_utm'],
            'fuso': projeto_dict['fuso'],
            'latitude': latitude,
            'longitude': longitude
        },
        'coordenadasLatLon': coordenadas_lat_lon
    }
    
    conn.close()
    
    return jsonify(result)

@app.route('/api/projects/<int:projeto_id>', methods=['PUT'])
def update_project(projeto_id):
    """Atualiza um projeto"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        # Busca o projeto atual
        projeto = conn.execute('SELECT * FROM projetos WHERE id = ?', (projeto_id,)).fetchone()
        
        if not projeto:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        cursor = conn.execute('''
            UPDATE projetos SET
                zona_portuaria = ?, uf = ?, obj_concessao = ?, tipo = ?,
                capex_total = ?, data_assinatura = ?, descricao = ?,
                latitude = ?, longitude = ?, coordenada_e_utm = ?,
                coordenada_s_utm = ?, fuso = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('zona_portuaria', projeto['zona_portuaria']),
            data.get('uf', projeto['uf']),
            data.get('obj_concessao', projeto['obj_concessao']),
            data.get('tipo', projeto['tipo']),
            data.get('capex_total', projeto['capex_total']),
            data.get('data_assinatura', projeto['data_assinatura']),
            data.get('descricao', projeto['descricao']),
            data.get('latitude', projeto['latitude']),
            data.get('longitude', projeto['longitude']),
            data.get('coordenada_e_utm', projeto['coordenada_e_utm']),
            data.get('coordenada_s_utm', projeto['coordenada_s_utm']),
            data.get('fuso', projeto['fuso']),
            projeto_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Projeto atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/servicos', methods=['POST'])
def create_servico():
    """Cria um novo serviço"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO servicos (
                projeto_id, zona_portuaria, uf, obj_concessao,
                tipo_servico, fase, servico, descricao_servico,
                prazo_inicio_anos, data_inicio, prazo_final_anos, data_final,
                fonte_prazo, percentual_capex, capex_servico_total, capex_servico_exec, perc_capex_exec, fonte_percentual
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('projeto_id'),
            data.get('zona_portuaria'),
            data.get('uf'),
            data.get('obj_concessao'),
            data.get('tipo_servico'),
            data.get('fase'),
            data.get('servico'),
            data.get('descricao_servico'),
            data.get('prazo_inicio_anos'),
            data.get('data_inicio'),
            data.get('prazo_final_anos'),
            data.get('data_final'),
            data.get('fonte_prazo'),
            data.get('percentual_capex'),
            data.get('capex_servico_total'),
            data.get('capex_servico_exec'),
            data.get('perc_capex_exec'),
            data.get('fonte_percentual')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Serviço criado com sucesso!', 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/servicos/<int:servico_id>', methods=['PUT'])
def update_servico(servico_id):
    """Atualiza um serviço existente"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        # Busca o serviço atual
        servico = conn.execute('SELECT * FROM servicos WHERE id = ?', (servico_id,)).fetchone()
        
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        cursor = conn.execute('''
            UPDATE servicos SET
                tipo_servico = ?, fase = ?, servico = ?, descricao_servico = ?,
                data_inicio = ?, data_final = ?, capex_servico_total = ?,
                capex_servico_exec = ?, perc_capex_exec = ?
            WHERE id = ?
        ''', (
            data.get('tipo_servico', servico['tipo_servico']),
            data.get('fase', servico['fase']),
            data.get('servico', servico['servico']),
            data.get('descricao_servico', servico['descricao_servico']),
            data.get('data_inicio', servico['data_inicio']),
            data.get('data_final', servico['data_final']),
            data.get('capex_servico_total', servico['capex_servico_total']),
            data.get('capex_servico_exec', servico['capex_servico_exec']),
            data.get('perc_capex_exec', servico['perc_capex_exec']),
            servico_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Serviço atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/acompanhamento', methods=['POST'])
def create_acompanhamento():
    """Cria um novo acompanhamento"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO acompanhamento (
                projeto_id, zona_portuaria, uf, obj_concessao,
                tipo_servico, fase, servico, descricao,
                percentual_executada, valor_executado, data_atualizacao,
                responsavel, cargo, setor, riscos_tipo, riscos_descricao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('projeto_id'),
            data.get('zona_portuaria'),
            data.get('uf'),
            data.get('obj_concessao'),
            data.get('tipo_servico'),
            data.get('fase'),
            data.get('servico'),
            data.get('descricao'),
            data.get('percentual_executada'),
            data.get('valor_executado'),
            data.get('data_atualizacao'),
            data.get('responsavel'),
            data.get('cargo'),
            data.get('setor'),
            data.get('riscos_tipo'),
            data.get('riscos_descricao')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Acompanhamento criado com sucesso!', 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Endpoints de Upload e Arquivos -----------------------------------------

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Faz upload de planilha Excel ou JSON e importa para o banco"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Processa o arquivo
            if filename.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                success = import_json_data(data)
            elif filename.endswith(('.xlsx', '.xls')):
                data = process_excel_file(filepath)
                success = import_json_data(data)
            
            if success:
                return jsonify({
                    'message': f'Arquivo {filename} importado com sucesso!',
                    'filename': filename,
                    'records': len(data.get('Tabela 00 - Cadastro', []))
                })
            else:
                return jsonify({'error': 'Erro ao processar arquivo'}), 500
        else:
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_excel_file(filepath):
    """Processa arquivo Excel e converte para formato JSON"""
    try:
        xls = pd.ExcelFile(filepath, engine='openpyxl')
        data = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
            df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
            
            # Normaliza headers se começar com ##
            if not df.empty and isinstance(df.iat[0,0], str) and df.iat[0,0].strip().startswith('##'):
                headers = df.iloc[1].astype(str).str.strip().tolist()
                df = df.iloc[2:].copy()
                df.columns = headers
            
            df.columns = [str(c).strip() for c in df.columns]
            data[sheet_name] = df.to_dict('records')
        
        return data
    except Exception as e:
        print(f"Erro ao processar Excel: {e}")
        return {}

def import_json_data(data):
    """Importa dados no formato JSON para o banco"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Limpa tabelas
        cursor.execute('DELETE FROM acompanhamento')
        cursor.execute('DELETE FROM servicos')
        cursor.execute('DELETE FROM projetos')
        
        # Importa projetos
        cadastros = data.get('Tabela 00 - Cadastro', [])
        for cadastro in cadastros:
            cursor.execute('''
                INSERT INTO projetos (
                    zona_portuaria, uf, obj_concessao, tipo, capex_total,
                    data_assinatura, descricao, latitude, longitude,
                    coordenada_e_utm, coordenada_s_utm, fuso
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cadastro.get('Zona portuária'),
                cadastro.get('UF'),
                cadastro.get('Obj. de Concessão'),
                cadastro.get('Tipo'),
                cadastro.get('CAPEX Total'),
                cadastro.get('Data de assinatura do contrato'),
                cadastro.get('Descrição'),
                cadastro.get('Latitude'),
                cadastro.get('Longitude'),
                cadastro.get('Coordenada E (UTM)'),
                cadastro.get('Coordenada S (UTM)'),
                cadastro.get('Fuso')
            ))
            
            projeto_id = cursor.lastrowid
            
            # Importa serviços e acompanhamentos (lógica similar)
            # ... (código de importação de serviços e acompanhamentos)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro na importação: {e}")
        return False

@app.route('/api/projects/<int:projeto_id>', methods=['DELETE'])
def delete_project(projeto_id):
    """Exclui um projeto"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Exclui acompanhamentos e serviços primeiro
        cursor.execute('DELETE FROM acompanhamento WHERE projeto_id = ?', (projeto_id,))
        cursor.execute('DELETE FROM servicos WHERE projeto_id = ?', (projeto_id,))
        
        # Exclui o projeto
        cursor.execute('DELETE FROM projetos WHERE id = ?', (projeto_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Projeto excluído com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/acompanhamento/<int:acompanhamento_id>', methods=['PUT'])
def update_acompanhamento(acompanhamento_id):
    """Atualiza um acompanhamento específico"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        conn.execute('''
            UPDATE acompanhamento SET
                fase = ?, servico = ?, descricao = ?,
                percentual_executada = ?, valor_executado = ?,
                data_atualizacao = ?, responsavel = ?, cargo = ?,
                setor = ?, riscos_tipo = ?, riscos_descricao = ?
            WHERE id = ?
        ''', (
            data.get('fase'),
            data.get('servico'),
            data.get('descricao'),
            data.get('percentual_executada'),
            data.get('valor_executado'),
            data.get('data_atualizacao'),
            data.get('responsavel'),
            data.get('cargo'),
            data.get('setor'),
            data.get('riscos_tipo'),
            data.get('riscos_descricao'),
            acompanhamento_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Acompanhamento atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/acompanhamento/<int:acompanhamento_id>', methods=['DELETE'])
def delete_acompanhamento(acompanhamento_id):
    """Exclui um acompanhamento específico"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM acompanhamento WHERE id = ?', (acompanhamento_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Acompanhamento excluído com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Páginas HTML ----------------------------------------------------------

@app.route('/cadastro')
def cadastro_page():
    """Página de cadastro de projetos"""
    return send_from_directory('.', 'cadastro.html')

@app.route('/planilhas')
def planilhas_page():
    """Página de gestão de planilhas"""
    return send_from_directory('.', 'planilhas.html')

@app.route('/editar/<int:projeto_id>')
def editar_page(projeto_id):
    """Página de edição de projeto"""
    return send_from_directory('.', 'editar.html')

# --- Inicialização ----------------------------------------------------------

if __name__ == '__main__':
    # Inicializa banco de dados
    init_db()
    
    # Importa dados do JSON se existir
    if Path(JSON_FILE).exists():
        print("Importando dados do JSON...")
        import_from_json()
        print("Importação concluída!")
    
    print("Servidor iniciado em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
