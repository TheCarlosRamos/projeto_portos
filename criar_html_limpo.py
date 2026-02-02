#!/usr/bin/env python3
"""
Gerador de HTML estático LIMPO baseado no portos.html
Cria versão limpa sem conflitos de funções
"""

import sqlite3
import json
from datetime import datetime
import os
import re

def extrair_dados_banco():
    """Extrai dados do banco SQLite"""
    
    db_path = 'app/present_tela/portos.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Extrair projetos
        cursor.execute("""
            SELECT id, zona_portuaria, uf, obj_concessao, tipo, descricao, 
                   capex_total, capex_executado, perc_capex_executado,
                   latitude, longitude
            FROM projetos
            ORDER BY id
        """)
        
        projetos = []
        for row in cursor.fetchall():
            projeto = {
                'id': f"projeto-{row['id']}",
                'zona': row['zona_portuaria'] or 'Não informado',
                'uf': row['uf'] or 'Não informado',
                'objConcessao': row['obj_concessao'] or 'Não informado',
                'tipo': row['tipo'] or 'Não informado',
                'descricao': row['descricao'] or 'Sem descrição',
                'capexTotal': row['capex_total'] or 0,
                'capexExecutado': row['capex_executado'] or 0,
                'progresso': (row['perc_capex_executado'] or 0) * 100,
                'etapa': 'Em Andamento',
                'coordenadasLatLon': None
            }
            
            # Coordenadas
            if row['latitude'] and row['longitude']:
                projeto['coordenadasLatLon'] = {
                    'lat': row['latitude'],
                    'lon': row['longitude']
                }
            
            projetos.append(projeto)
        
        conn.close()
        return projetos
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.close()
        return None

def criar_html_limpo(dados):
    """Cria HTML estático limpo com dados embutidos"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão de Concessões Portuárias - Versão Estática</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ background: linear-gradient(135deg, #2E4E8C 0%, #3E5FA4 100%); }}
        #leaflet-map {{ z-index: 1 !important; }}
        .leaflet-container {{ z-index: 1 !important; }}
    </style>
</head>
<body>
<!-- BANNER VERSÃO ESTÁTICA -->
<div style="position: fixed; top: 0; left: 0; right: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 8px; font-size: 12px; z-index: 9999;">
    🚢 Versão Estática - GitHub Pages | Dados em {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
<div style="height: 40px;"></div>

<div class="flex h-screen">
    <!-- Sidebar -->
    <div class="w-64 bg-white shadow-xl">
        <div class="p-6">
            <div class="flex items-center gap-3 mb-8">
                <i class="fas fa-ship text-2xl text-blue-600"></i>
                <h1 class="text-xl font-bold text-gray-800">Sistema Portuário</h1>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto">
        <div class="p-8">
            <h1 class="text-3xl font-bold text-white mb-8">Gestão de Concessões Portuárias</h1>
            
            <!-- Mapa -->
            <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">
                    <i class="fas fa-map-marked-alt text-blue-600"></i>
                    Mapa de Projetos
                </h2>
                <div id="projects-map" class="w-full h-96 rounded-lg"></div>
            </div>
            
            <!-- Busca -->
            <div class="mb-6">
                <input type="text" id="search-input" 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg"
                       placeholder="Buscar projetos...">
            </div>

            <!-- Projects Grid -->
            <div id="projects-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Cards inseridos via JavaScript -->
            </div>
        </div>
    </div>
</div>

<!-- Modal -->
<div id="project-modal" class="fixed inset-0 bg-black bg-opacity-60 hidden p-4 z-50">
    <div class="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 id="modal-title" class="text-2xl font-bold"></h2>
                <button id="close-modal" class="text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            <div id="modal-body"></div>
        </div>
    </div>
</div>

<script>
// Dados do banco - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
const projetosData = {json.dumps(dados, ensure_ascii=False, indent=2)};
let projetosFiltrados = [...projetosData];

// Carregar dados ao iniciar
function loadData() {{
    console.log('Carregando dados embutidos:', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    generateProjectsMap(projetosData);
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
}}

// Renderizar cards
function renderProjects() {{
    const grid = document.getElementById('projects-grid');
    
    if (projetosFiltrados.length === 0) {{
        grid.innerHTML = '<div class="col-span-full text-center p-8"><p class="text-white">Nenhum projeto encontrado.</p></div>';
        return;
    }}

    grid.innerHTML = projetosFiltrados.map(projeto => {{
        const statusColor = projeto.progresso === 0 ? 'bg-gray-400' : 
                           projeto.progresso < 50 ? 'bg-yellow-500' : 
                           projeto.progresso < 100 ? 'bg-blue-500' : 'bg-green-500';
        
        return `
            <div data-id="${{projeto.id}}" class="project-card bg-white rounded-xl shadow-md p-6 cursor-pointer hover:shadow-lg">
                <div>
                    <p class="text-sm text-gray-500">${{projeto.uf}}</p>
                    <h3 class="text-lg font-bold text-gray-800">${{projeto.objConcessao}}</h3>
                    <p class="text-sm text-gray-600 mt-2">${{projeto.descricao}}</p>
                </div>
                <div class="flex justify-between items-center mt-4 pt-4 border-t">
                    <div class="flex items-center">
                        <span class="w-3 h-3 rounded-full ${{statusColor}} mr-2"></span>
                        <span class="text-sm text-gray-600">${{projeto.etapa}}</span>
                    </div>
                    <span class="text-xs text-gray-500">
                        R$ ${{(projeto.capexTotal / 1000000).toFixed(1)}}M
                    </span>
                </div>
                ${{projeto.progresso > 0 ? `
                    <div class="mt-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-600 h-2 rounded-full" style="width: ${{projeto.progresso}}%"></div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">${{projeto.progresso.toFixed(1)}}% concluído</p>
                    </div>
                ` : ''}}
            </div>
        `;
    }}).join('');
}}

// Gerar mapa
function generateProjectsMap(projects) {{
    const mapContainer = document.getElementById('projects-map');
    const projectsWithCoords = projects.filter(p => p.coordenadasLatLon);
    
    if (projectsWithCoords.length === 0) {{
        mapContainer.innerHTML = '<div class="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center"><p class="text-gray-500">Nenhum projeto com coordenadas</p></div>';
        return;
    }}
    
    mapContainer.innerHTML = '<div id="leaflet-map" style="width: 100%; height: 100%;"></div>';
    const map = L.map('leaflet-map').setView([-14.235, -51.925], 4);
    
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '© OpenStreetMap contributors'
    }}).addTo(map);
    
    const markers = [];
    projectsWithCoords.forEach(p => {{
        const marker = L.marker([p.coordenadasLatLon.lat, p.coordenadasLatLon.lon]).addTo(map);
        marker.bindPopup(`
            <div>
                <h4 style="margin: 0 0 8px 0; color: #2E4E8C; font-weight: bold;">${{p.objConcessao}}</h4>
                <p style="margin: 4px 0; color: #666;"><strong>UF:</strong> ${{p.uf}}</p>
                <p style="margin: 4px 0; color: #666; font-size: 12px;">${{p.descricao.substring(0, 100)}}${{p.descricao.length > 100 ? '...' : ''}}</p>
            </div>
        `);
        markers.push(marker);
    }});
    
    if (markers.length > 0) {{
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }}
}}

// Event listeners
function addEventListeners() {{
    // Fechar modal
    document.getElementById('close-modal').addEventListener('click', () => {{
        document.getElementById('project-modal').classList.add('hidden');
    }});
    
    // Clicar nos cards
    document.addEventListener('click', (e) => {{
        const card = e.target.closest('.project-card');
        if (card) {{
            const projectId = card.dataset.id;
            renderProjectDetails(projectId);
        }}
    }});
    
    // Busca
    document.getElementById('search-input').addEventListener('input', (e) => {{
        const searchTerm = e.target.value.toLowerCase();
        projetosFiltrados = projetosData.filter(projeto => 
            projeto.objConcessao.toLowerCase().includes(searchTerm) ||
            projeto.descricao.toLowerCase().includes(searchTerm) ||
            projeto.uf.toLowerCase().includes(searchTerm)
        );
        renderProjects();
    }});
}}

// Renderizar detalhes
function renderProjectDetails(projectId) {{
    const project = projetosData.find(p => p.id === projectId);
    if (!project) return;
    
    const modal = document.getElementById('project-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    const nomeProjeto = project.zona === 'Não se aplica' ? project.objConcessao : `${{project.zona}} - ${{project.objConcessao}}`;
    
    modalTitle.textContent = nomeProjeto;
    modalBody.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <span class="text-sm font-medium text-gray-600">Zona Portuária:</span>
                <span class="text-gray-800 ml-2">${{project.zona}}</span>
            </div>
            <div>
                <span class="text-sm font-medium text-gray-600">UF:</span>
                <span class="text-gray-800 ml-2">${{project.uf}}</span>
            </div>
            <div>
                <span class="text-sm font-medium text-gray-600">Objeto de Concessão:</span>
                <span class="text-gray-800 ml-2">${{project.objConcessao}}</span>
            </div>
            <div>
                <span class="text-sm font-medium text-gray-600">Tipo:</span>
                <span class="text-gray-800 ml-2">${{project.tipo}}</span>
            </div>
            <div>
                <span class="text-sm font-medium text-gray-600">CAPEX Total:</span>
                <span class="text-gray-800 ml-2">R$ ${{(project.capexTotal / 1000000).toFixed(1)}}M</span>
            </div>
            <div>
                <span class="text-sm font-medium text-gray-600">Progresso:</span>
                <span class="text-gray-800 ml-2">${{project.progresso.toFixed(1)}}%</span>
            </div>
        </div>
        ${{project.descricao ? `
            <div class="mt-4">
                <span class="text-sm font-medium text-gray-600">Descrição:</span>
                <p class="text-gray-800 mt-1">${{project.descricao}}</p>
            </div>
        ` : ''}}
    `;
    
    modal.classList.remove('hidden');
}}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {{
    loadData();
    addEventListeners();
}});
</script>
</body>
</html>"""
    
    # Salvar HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ HTML estático limpo gerado: index.html")
    print(f"📊 {len(dados)} projetos com dados")
    
    return len(dados)

def main():
    print("🔍 Criando HTML estático limpo...")
    
    dados = extrair_dados_banco()
    
    if dados:
        projetos_count = criar_html_limpo(dados)
        print(f"🎉 Sucesso! HTML estático com {projetos_count} projetos gerado!")
    else:
        print("❌ Falha ao extrair dados")

if __name__ == "__main__":
    main()
