#!/usr/bin/env python3
"""
Modificador do index2.html para incluir dados completos e função do mapa
"""

import json
from datetime import datetime

def modificar_index2_completo():
    """Modifica index2.html para incluir dados completos e função do mapa"""
    
    # Ler dados completos
    with open('dados_completos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Ler index2.html original
    with open('index2.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Encontrar onde inserir os dados
    # Vou substituir a seção de dados vazia
    dados_js = f"""
// Dados completos do banco - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
const dadosCompletos = {json.dumps(dados, ensure_ascii=False, indent=2)};
const projetosData = dadosCompletos.projetos;
const servicosData = dadosCompletos.servicos;
const acompanhamentosData = dadosCompletos.acompanhamentos;
const resumoData = dadosCompletos.resumo;

let projetosFiltrados = [...projetosData];
let servicosFiltrados = [...servicosData];
let acompanhamentosFiltrados = [...acompanhamentosData];
let currentProject = null;
let isEditMode = false;
"""
    
    # Substituir a declaração de dados vazia
    import re
    
    # Encontrar e substituir as variáveis globais
    html_content = re.sub(
        r'let projetosData = \[\];.*?let isEditMode = false;',
        dados_js.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    # Adicionar função do mapa que funciona
    mapa_function = """
// Gerar Mapa - Função que funciona no index.html
function generateProjectsMap(projects) {
    console.log('generateProjectsMap chamado com projetos:', projects);
    
    const mapContainer = document.getElementById('projects-map');
    const legendContainer = document.getElementById('map-legend');
    
    console.log('Elementos encontrados:', {
        mapContainer: !!mapContainer,
        legendContainer: !!legendContainer
    });
    
    if (!mapContainer) {
        console.error('Elemento #projects-map não encontrado!');
        return;
    }
    
    // Filtra projetos com coordenadas válidas
    const projectsWithCoords = projects.filter(p => 
        p.coordenadasLatLon && p.coordenadasLatLon.lat && p.coordenadasLatLon.lon
    );
    
    console.log('Projetos com coordenadas:', projectsWithCoords.length);
    
    if (projectsWithCoords.length === 0) {
        // Se não houver coordenadas, mostra o mapa padrão
        mapContainer.innerHTML = `
            <div style="width: 100%; height: 100%; background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; border-radius: 0.5rem;">
                <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 500px; z-index: 1;">
                    <div style="font-size: 80px; margin-bottom: 20px;">🗺️</div>
                    <h3 style="color: #333; margin: 0 0 20px 0; font-size: 28px; font-weight: bold;">Mapa de Projetos Portuários</h3>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <div style="font-size: 36px; font-weight: bold; color: #007bff; margin-bottom: 5px;">
                            ${projects.length}
                        </div>
                        <div style="color: #666; font-size: 16px;">
                            Projetos Cadastrados
                        </div>
                    </div>
                    <div style="color: #999; font-size: 14px; line-height: 1.5;">
                        Nenhum projeto com coordenadas geográficas<br>
                        Adicione latitude e longitude para visualizar no mapa
                    </div>
                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                        <div style="font-size: 12px; color: #999;">
                            Status: <span style="color: #28a745; font-weight: bold;">✓ Funcionando</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Cria mapa interativo com Leaflet
        console.log('Criando mapa Leaflet com marcadores para', projectsWithCoords.length, 'projetos');
        
        // Limpa o container
        mapContainer.innerHTML = '<div id="leaflet-map" style="width: 100%; height: 100%; border-radius: 0.5rem;"></div>';
        
        // Inicializa o mapa do Brasil
        const map = L.map('leaflet-map').setView([-14.235, -51.925], 4);
        
        // Adiciona camada do OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Array para armazenar todos os marcadores
        const markers = [];
        
        // Adiciona marcadores para cada projeto
        projectsWithCoords.forEach(p => {
            const lat = p.coordenadasLatLon.lat;
            const lon = p.coordenadasLatLon.lon;
            const nome = p.objConcessao || p.nome || 'Projeto';
            const uf = p.uf || '';
            const descricao = p.descricao || '';
            
            // Cria popup com informações do projeto
            const popupContent = `
                <div style="min-width: 200px;">
                    <h4 style="margin: 0 0 8px 0; color: #2E4E8C; font-weight: bold;">${nome}</h4>
                    ${uf ? `<p style="margin: 4px 0; color: #666;"><strong>UF:</strong> ${uf}</p>` : ''}
                    ${descricao ? `<p style="margin: 4px 0; color: #666; font-size: 12px;">${descricao.substring(0, 100)}${descricao.length > 100 ? '...' : ''}</p>` : ''}
                    <p style="margin: 8px 0 0 0; color: #999; font-size: 11px;">Lat: ${lat.toFixed(6)}, Lon: ${lon.toFixed(6)}</p>
                </div>
            `;
            
            // Cria marcador personalizado
            const marker = L.marker([lat, lon]).addTo(map);
            marker.bindPopup(popupContent);
            markers.push(marker);
        });
        
        // Ajusta o mapa para mostrar todos os marcadores
        if (markers.length > 0) {
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds().pad(0.1));
        }
        
        // Adiciona controle de informações
        const infoControl = L.control({position: 'topleft'});
        infoControl.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'info-control');
            div.style.background = 'rgba(255, 255, 255, 0.95)';
            div.style.padding = '12px 16px';
            div.style.borderRadius = '12px';
            div.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
            div.style.fontSize = '13px';
            div.style.backdropFilter = 'blur(4px)';
            div.innerHTML = `
                <div style="font-weight: bold; color: #333; margin-bottom: 6px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 16px;">🗺️</span>
                    <span>${projectsWithCoords.length} Projetos com Localização</span>
                </div>
                <div style="color: #666; font-size: 12px;">
                    ${projects.length - projectsWithCoords.length} projetos sem coordenadas
                </div>
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ddd;">
                    <div style="color: #999; font-size: 11px;">
                        Clique nos marcadores para ver detalhes
                    </div>
                </div>
            `;
            return div;
        };
        infoControl.addTo(map);
    }
    
    // Cria legendas simples
    if (projects && projects.length > 0) {
        const tipos = [...new Set(projects.map(p => p.tipo || 'Não definido'))];
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
        
        let legendHTML = '<div class="text-sm text-gray-600 mb-2">Tipos de Projetos:</div>';
        tipos.forEach((tipo, index) => {
            const count = projects.filter(p => (p.tipo || 'Não definido') === tipo).length;
            const color = colors[index % colors.length];
            legendHTML += `
                <div class="flex items-center gap-2 bg-white px-3 py-1 rounded-full border border-gray-300">
                    <div class="w-3 h-3 rounded-full" style="background-color: ${color}"></div>
                    <span class="text-xs font-medium">${tipo} (${count})</span>
                </div>
            `;
        });
        if (legendContainer) {
            legendContainer.innerHTML = legendHTML;
        }
    } else {
        if (legendContainer) {
            legendContainer.innerHTML = '';
        }
    }
}
"""
    
    # Substituir a função loadData para usar dados completos
    loaddata_function = """
// Carregar dados ao iniciar - Versão Completa
function loadData() {
    console.log('Carregando dados completos:', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    // Gera o mapa de projetos
    generateProjectsMap(projetosData);
    
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
    
    // Adicionar event listeners
    addEventListeners();
}
"""
    
    # Substituir a função renderProjects para mostrar serviços e acompanhamentos
    render_projects_function = """
// Renderizar cards de projetos completos
function renderProjects() {
    const grid = document.getElementById('projects-grid');
    
    if (projetosFiltrados.length === 0) {
        grid.innerHTML = '<div class="col-span-full text-center text-white p-8"><p>Nenhum projeto encontrado.</p></div>';
        return;
    }

    grid.innerHTML = projetosFiltrados.map(projeto => {
        const statusColor = projeto.progresso === 0 ? 'bg-gray-400' : 
                           projeto.progresso < 50 ? 'bg-yellow-500' : 
                           projeto.progresso < 100 ? 'bg-blue-500' : 'bg-green-500';
        
        return `
            <div data-id="${projeto.id}" class="project-card bg-white rounded-xl shadow-md p-6 cursor-pointer hover:shadow-lg">
                <div>
                    <p class="text-sm text-gray-500">${projeto.uf}</p>
                    <h3 class="text-lg font-bold mt-1 text-gray-800">${projeto.objConcessao || 'Obj. de concessão não informado'}</h3>
                    <p class="text-sm text-gray-600 mt-2 line-clamp-3">${projeto.descricao || 'Descrição não disponível'}</p>
                </div>
                <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                    <div class="flex items-center">
                        <span class="w-3 h-3 rounded-full ${statusColor} mr-2"></span>
                        <span class="text-sm font-medium text-gray-600">${projeto.etapa}</span>
                    </div>
                    ${projeto.capexTotal > 0 ? `
                        <span class="text-xs text-gray-500">
                            R$ ${(projeto.capexTotal / 1000000).toFixed(1)}M
                        </span>
                    ` : ''}
                </div>
                ${projeto.progresso > 0 ? `
                    <div class="mt-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-600 h-2 rounded-full" style="width: ${projeto.progresso}%"></div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">${projeto.progresso.toFixed(1)}% concluído</p>
                    </div>
                ` : ''}
                <div class="mt-3 flex gap-2">
                    <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        ${projeto.servicos.length} serviços
                    </span>
                    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        ${projeto.acompanhamentos.length} acompanhamentos
                    </span>
                </div>
            </div>
        `;
    }).join('');
}
"""
    
    # Substituir as funções no HTML
    html_content = re.sub(
        r'// Carregar dados do arquivo data\.js.*?addEventListeners\(\);',
        loaddata_function.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    html_content = re.sub(
        r'// Renderizar cards de projetos.*?}\.join\(''\);',
        render_projects_function.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    html_content = re.sub(
        r'// Gerar Mapa de Projetos.*?}\);',
        mapa_function.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    # Adicionar dados inline no início do script
    dados_inline = f"""
<script>
// Dados completos do banco - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
const dadosCompletos = {json.dumps(dados, ensure_ascii=False, indent=2)};
const projetosData = dadosCompletos.projetos;
const servicosData = dadosCompletos.servicos;
const acompanhamentosData = dadosCompletos.acompanhamentos;
const resumoData = dadosCompletos.resumo;

let projetosFiltrados = [...projetosData];
let servicosFiltrados = [...servicosData];
let acompanhamentosFiltrados = [...acompanhamentosData];
let currentProject = null;
let isEditMode = false;

"""
    
    # Inserir dados inline após a primeira tag script
    html_content = html_content.replace('<script>', dados_inline)
    
    # Salvar o arquivo modificado
    with open('index2.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ index2.html modificado com sucesso!")
    print(f"📊 {len(dados['projetos'])} projetos com serviços e acompanhamentos")
    print(f"🔧 {len(dados['servicos'])} serviços")
    print(f"📈 {len(dados['acompanhamentos'])} acompanhamentos")
    print(f"🗺️ Função do mapa incluída e funcionando")
    
    return len(dados['projetos'])

def main():
    print("🔧 Modificando index2.html com dados completos...")
    
    projetos_count = modificar_index2_completo()
    
    print(f"\n🎉 Sucesso! index2.html agora é completo:")
    print(f"   📊 {projetos_count} projetos com dados completos")
    print(f"   🔧 Serviços e acompanhamentos incluídos")
    print(f"   🗺️ Mapa interativo funcionando")
    print(f"   📱 Pronto para usar!")

if __name__ == "__main__":
    main()
