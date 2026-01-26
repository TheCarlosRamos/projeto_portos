from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app)

@app.route('/api/portos', methods=['GET'])
def get_portos():
    """Retorna todos os portos com dados completos para o dashboard"""
    try:
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row
        
        query = """
        SELECT 
            c.id,
            c.zona_portuaria as name,
            c.obj_concessao as description,
            c.tipo as project_type,
            c.capex_total as investment,
            c.data_ass_contrato as contract_date,
            c.descricao as full_description,
            c.coord_e_utm,
            c.coord_s_utm,
            c.fuso,
            GROUP_CONCAT(DISTINCT uf.sigla) as ufs,
            COUNT(DISTINCT s.id) as total_services,
            COUNT(DISTINCT a.id) as total_updates,
            COALESCE(MAX(a.perc_executada), 0) as progress_percentage,
            CASE 
                WHEN MAX(a.perc_executada) >= 0.9 THEN 'Concluído'
                WHEN MAX(a.perc_executada) > 0 THEN 'Em Andamento'
                ELSE 'Planejamento'
            END as status
        FROM cadastro c
        LEFT JOIN cadastro_uf cu ON c.id = cu.cadastro_id
        LEFT JOIN uf uf ON cu.uf_sigla = uf.sigla
        LEFT JOIN servico s ON c.id = s.cadastro_id
        LEFT JOIN acompanhamento a ON s.id = a.servico_id
        GROUP BY c.id
        ORDER BY c.zona_portuaria
        """
        
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        projects = []
        for row in rows:
            project = {
                'id': str(row['id']),
                'name': row['name'] or f"Porto {row['id']}",
                'description': row['description'] or '',
                'sector': 'Portos',
                'status': row['status'] or 'Planejamento',
                'progress': float(row['progress_percentage'] or 0) * 100,
                'investment': float(row['investment'] or 0),
                'contractDate': row['contract_date'] or '',
                'fullDescription': row['full_description'] or '',
                'projectType': row['project_type'] or 'Concessão',
                'states': row['ufs'].split(',') if row['ufs'] else [],
                'totalServices': row['total_services'] or 0,
                'totalUpdates': row['total_updates'] or 0,
                'coordinates': {
                    'utm_e': row['coord_e_utm'],
                    'utm_n': row['coord_s_utm'],
                    'fuso': row['fuso']
                }
            }
            projects.append(project)
        
        return jsonify(projects)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portos/<int:porto_id>', methods=['GET'])
def get_porto_detail(porto_id):
    """Retorna detalhes completos de um porto específico"""
    try:
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # Dados principais do porto
        cursor = conn.execute("""
        SELECT 
            c.id,
            c.zona_portuaria as name,
            c.obj_concessao as description,
            c.tipo as project_type,
            c.capex_total as investment,
            c.data_ass_contrato as contract_date,
            c.descricao as full_description,
            c.coord_e_utm,
            c.coord_s_utm,
            c.fuso
        FROM cadastro c
        WHERE c.id = ?
        """, (porto_id,))
        
        porto = cursor.fetchone()
        if not porto:
            conn.close()
            return jsonify({'error': 'Porto não encontrado'}), 404
        
        # UFs do porto
        cursor = conn.execute("""
        SELECT uf.sigla FROM uf uf
        JOIN cadastro_uf cu ON uf.sigla = cu.uf_sigla
        WHERE cu.cadastro_id = ?
        """, (porto_id,))
        ufs = [row['sigla'] for row in cursor.fetchall()]
        
        # Serviços do porto
        cursor = conn.execute("""
        SELECT 
            s.id,
            s.tipo_servico,
            s.fase,
            s.servico,
            s.descricao_servico,
            s.prazo_inicio_anos,
            s.data_inicio,
            s.prazo_final_anos,
            s.data_final,
            s.fonte_prazo,
            s.perc_capex,
            s.capex_servico,
            s.fonte_perc_capex
        FROM servico s
        WHERE s.cadastro_id = ?
        ORDER BY s.tipo_servico, s.fase
        """, (porto_id,))
        services = []
        for row in cursor.fetchall():
            service = dict(row)
            if service['perc_capex']:
                service['perc_capex'] = float(service['perc_capex']) * 100
            services.append(service)
        
        # Acompanhamentos mais recentes
        cursor = conn.execute("""
        SELECT 
            a.descricao,
            a.perc_executada,
            a.capex_reaj,
            a.valor_executado,
            a.data_atualizacao,
            a.responsavel,
            a.cargo,
            a.setor,
            a.risco_tipo,
            a.risco_descricao
        FROM acompanhamento a
        JOIN servico s ON a.servico_id = s.id
        WHERE s.cadastro_id = ?
        ORDER BY a.data_atualizacao DESC
        LIMIT 10
        """, (porto_id,))
        updates = []
        for row in cursor.fetchall():
            update = dict(row)
            if update['perc_executada']:
                update['perc_executada'] = float(update['perc_executada']) * 100
            updates.append(update)
        
        conn.close()
        
        project_detail = {
            'id': str(porto['id']),
            'name': porto['name'],
            'description': porto['description'],
            'sector': 'Portos',
            'projectType': porto['project_type'],
            'investment': float(porto['investment'] or 0),
            'contractDate': porto['contract_date'],
            'fullDescription': porto['full_description'],
            'states': ufs,
            'coordinates': {
                'utm_e': porto['coord_e_utm'],
                'utm_n': porto['coord_s_utm'],
                'fuso': porto['fuso']
            },
            'services': services,
            'recentUpdates': updates,
            'totalServices': len(services),
            'totalUpdates': len(updates)
        }
        
        return jsonify(project_detail)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portos/summary', methods=['GET'])
def get_portos_summary():
    """Retorna dados resumidos para o dashboard"""
    try:
        conn = sqlite3.connect(db.DB_PATH)
        
        # Total de portos
        cursor = conn.execute("SELECT COUNT(*) as total FROM cadastro")
        total_portos = cursor.fetchone()[0]
        
        # Por status - simplificado
        cursor = conn.execute("""
        SELECT 
            CASE 
                WHEN a.perc_executada >= 0.9 THEN 'Concluído'
                WHEN a.perc_executada > 0 THEN 'Em Andamento'
                ELSE 'Planejamento'
            END as status,
            COUNT(*) as count
        FROM acompanhamento a
        GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Investimento total
        cursor = conn.execute("SELECT SUM(capex_total) as total FROM cadastro WHERE capex_total IS NOT NULL")
        total_investment = cursor.fetchone()[0] or 0
        
        # Progresso médio - simplificado
        cursor = conn.execute("""
        SELECT AVG(CASE 
            WHEN a.perc_executada IS NULL THEN 0
            ELSE a.perc_executada
        END) as avg_progress
        FROM acompanhamento a
        """)
        result = cursor.fetchone()
        avg_progress = (result[0] or 0) * 100 if result else 0
        
        conn.close()
        
        summary = {
            'totalProjects': total_portos,
            'statusCounts': status_counts,
            'totalInvestment': total_investment,
            'averageProgress': avg_progress,
            'sector': 'Portos'
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicializar o banco de dados
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
