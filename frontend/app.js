/**
 * Aplicação Frontend - Sistema de Gestão de Concessões Portuárias
 */

let projetosData = [];
let projetosFiltrados = [];
let map = null;

// Dados estáticos (fallback quando a API não responde ou retorna vazio)
const DADOS_ESTATICOS = [
  { id: 1, name: "Porto Organizado de Santos", description: "TECON 10", full_description: "Terminal destinado à movimentação e armazenagem de carga conteinerizada e carga geral.", project_type: "Arrendamento", investment: 6454903000, progress_percentage: 0.006, status: "Em Andamento", ufs: "SP", latitude: -23.926132, longitude: -46.34027 },
  { id: 2, name: "Não se aplica", description: "Hidrovia do Paraguai", full_description: "Hidrovia no trecho brasileiro fazendo divisa com Paraguai e Bolívia.", project_type: "Concessão", investment: 63796000, progress_percentage: 0, status: "Planejamento", ufs: "MT; MS", latitude: null, longitude: null },
  { id: 3, name: "Porto Organizado de Maceió", description: "TPM Macéio", full_description: "Terminal destinado a movimentação de passageiros.", project_type: "Arrendamento", investment: 1978000, progress_percentage: 0, status: "Planejamento", ufs: "AL", latitude: null, longitude: null },
  { id: 4, name: "Porto Organizado do Rio de Janeiro", description: "RDJ07", full_description: "Terminal portuário destinado à movimentação e armazenagem de carga para apoio logístico Offshore.", project_type: "Arrendamento", investment: 101741000, progress_percentage: 0, status: "Planejamento", ufs: "RJ", latitude: -22.896621, longitude: -43.209639 },
  { id: 5, name: "Não se aplica", description: "Canal de Paranaguá", full_description: "Acesso aquaviário (canal de acesso) ao Porto de Paranaguá.", project_type: "Concessão", investment: 1226475000, progress_percentage: 0, status: "Planejamento", ufs: "PR", latitude: -25.492142, longitude: -48.479187 },
  { id: 6, name: "Porto Organizado de São Sebastião", description: "SSB01", full_description: "Pátio de cargas para movimentação de carga conteinerizada, dentre outras.", project_type: "Arrendamento", investment: 656085000, progress_percentage: 0, status: "Planejamento", ufs: "SP", latitude: -23.812704, longitude: -45.400052 }
];

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadProjects();
    setupEventListeners();
});

/**
 * Configura event listeners
 */
function setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    const reloadBtn = document.getElementById('reload-btn');
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterProjects(e.target.value);
        });
    }
    
    if (reloadBtn) {
        reloadBtn.addEventListener('click', () => {
            loadProjects();
        });
    }
}

/**
 * Inicializa o mapa
 */
function initMap() {
    map = L.map('projects-map').setView([-15.7801, -47.9292], 4); // Centro do Brasil
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

/**
 * Carrega projetos da API (com fallback para dados estáticos)
 */
async function loadProjects() {
    showLoading();
    const urls = [
        (window.API_BASE || '') + '/api/projects',
        'https://projetoportos.vercel.app/api/projects',
        'https://projeto-portos-qkwy.vercel.app/api/projects'
    ].filter((u, i, a) => a.indexOf(u) === i);
    
    for (const url of urls) {
        try {
            const response = await fetch(url);
            if (!response.ok) continue;
            const data = await response.json();
            if (Array.isArray(data) && data.length > 0) {
                projetosData = data;
                projetosFiltrados = [...projetosData];
                console.log('Projetos carregados da API:', projetosData.length);
                renderProjects();
                updateMap();
                hideLoading();
                return;
            }
        } catch (e) {
            console.warn('Tentativa falhou:', url, e);
        }
    }
    
    // Fallback: usar dados estáticos
    projetosData = DADOS_ESTATICOS;
    projetosFiltrados = [...projetosData];
    console.log('Usando dados estáticos:', projetosData.length);
    renderProjects();
    updateMap();
    hideLoading();
}

/**
 * Renderiza os cards de projetos
 */
function renderProjects() {
    const grid = document.getElementById('projects-grid');
    
    if (!grid) return;
    
    if (projetosFiltrados.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-inbox text-6xl text-gray-300 mb-4"></i>
                <p class="text-gray-500 text-lg">Nenhum projeto encontrado</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = projetosFiltrados.map(project => createProjectCard(project)).join('');
}

/**
 * Cria um card de projeto
 */
function createProjectCard(project) {
    const statusColors = {
        'Concluído': 'bg-green-100 text-green-800',
        'Em Andamento': 'bg-blue-100 text-blue-800',
        'Planejamento': 'bg-yellow-100 text-yellow-800'
    };
    
    const statusColor = statusColors[project.status] || 'bg-gray-100 text-gray-800';
    const progress = (project.progress_percentage * 100).toFixed(1);
    
    return `
        <div class="project-card bg-white rounded-xl shadow-lg p-6 cursor-pointer" onclick="showProjectDetails(${project.id})">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-xl font-bold text-gray-800 flex-1">${project.name || 'Sem nome'}</h3>
                <span class="px-3 py-1 rounded-full text-xs font-semibold ${statusColor}">
                    ${project.status}
                </span>
            </div>
            
            <p class="text-gray-600 mb-4 line-clamp-2">${project.description || 'Sem descrição'}</p>
            
            <div class="space-y-2 text-sm">
                <div class="flex items-center gap-2 text-gray-600">
                    <i class="fas fa-map-marker-alt w-4"></i>
                    <span>${project.ufs || 'N/A'}</span>
                </div>
                
                <div class="flex items-center gap-2 text-gray-600">
                    <i class="fas fa-tag w-4"></i>
                    <span>${project.project_type || 'N/A'}</span>
                </div>
                
                ${project.investment ? `
                <div class="flex items-center gap-2 text-gray-600">
                    <i class="fas fa-dollar-sign w-4"></i>
                    <span>R$ ${(project.investment / 1000000).toFixed(1)}M</span>
                </div>
                ` : ''}
            </div>
            
            <div class="mt-4 pt-4 border-t border-gray-200">
                <div class="flex justify-between items-center text-sm mb-2">
                    <span class="text-gray-600">Progresso</span>
                    <span class="font-semibold text-blue-600">${progress}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: ${progress}%"></div>
                </div>
            </div>
            
            <button class="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Ver Detalhes
            </button>
        </div>
    `;
}

/**
 * Atualiza marcadores no mapa
 */
function updateMap() {
    if (!map) return;
    
    // Limpar marcadores existentes
    map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
    
    // Adicionar novos marcadores
    projetosFiltrados.forEach(project => {
        if (project.latitude && project.longitude) {
            const marker = L.marker([project.latitude, project.longitude])
                .addTo(map)
                .bindPopup(`
                    <div class="p-2">
                        <h3 class="font-bold text-lg mb-2">${project.name}</h3>
                        <p class="text-sm text-gray-600 mb-2">${project.description}</p>
                        <button onclick="showProjectDetails(${project.id})" class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            Ver Detalhes
                        </button>
                    </div>
                `);
        }
    });
}

/**
 * Filtra projetos
 */
function filterProjects(searchTerm) {
    const term = searchTerm.toLowerCase();
    
    projetosFiltrados = projetosData.filter(project => {
        return (
            (project.name && project.name.toLowerCase().includes(term)) ||
            (project.description && project.description.toLowerCase().includes(term)) ||
            (project.ufs && project.ufs.toLowerCase().includes(term)) ||
            (project.project_type && project.project_type.toLowerCase().includes(term))
        );
    });
    
    renderProjects();
    updateMap();
}

/**
 * Mostra detalhes do projeto
 */
async function showProjectDetails(projectId) {
    const localProject = projetosData.find(p => p.id === projectId);
    
    try {
        showLoading();
        let project = localProject;
        
        const response = await fetch(`${window.API_BASE || 'https://projetoportos.vercel.app'}/api/projects/${projectId}`);
        if (response.ok) {
            project = await response.json();
        }
        if (!project && localProject) project = localProject;
        if (!project) throw new Error('Projeto não encontrado');
        
        const modal = document.getElementById('project-modal');
        const modalContent = document.getElementById('modal-content');
        
        modalContent.innerHTML = `
            <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-2xl font-bold text-gray-800">${project.name}</h2>
                    <button onclick="closeModal()" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-2xl"></i>
                    </button>
                </div>
                
                <div class="grid md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-bold text-lg mb-3">Informações Gerais</h3>
                        <div class="space-y-2 text-sm">
                            <p><strong>Descrição:</strong> ${project.description || 'N/A'}</p>
                            <p><strong>Tipo:</strong> ${project.project_type || 'N/A'}</p>
                            <p><strong>UFs:</strong> ${project.ufs || 'N/A'}</p>
                            <p><strong>Status:</strong> ${project.status}</p>
                            ${project.contract_date ? `<p><strong>Data do Contrato:</strong> ${new Date(project.contract_date).toLocaleDateString('pt-BR')}</p>` : ''}
                            ${project.investment ? `<p><strong>Investimento:</strong> R$ ${(project.investment / 1000000).toFixed(1)}M</p>` : ''}
                        </div>
                    </div>
                    
                    ${project.full_description ? `
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-bold text-lg mb-3">Descrição Completa</h3>
                        <p class="text-sm text-gray-700">${project.full_description}</p>
                    </div>
                    ` : ''}
                </div>
                
                ${project.services && project.services.length > 0 ? `
                <div class="mb-6">
                    <h3 class="font-bold text-lg mb-3">Serviços (${project.services.length})</h3>
                    <div class="space-y-3">
                        ${project.services.map(service => `
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <h4 class="font-semibold mb-2">${service.servico}</h4>
                                <div class="grid md:grid-cols-2 gap-2 text-sm text-gray-600">
                                    <p><strong>Tipo:</strong> ${service.tipo_servico || 'N/A'}</p>
                                    <p><strong>Fase:</strong> ${service.fase || 'N/A'}</p>
                                    ${service.data_inicio ? `<p><strong>Início:</strong> ${new Date(service.data_inicio).toLocaleDateString('pt-BR')}</p>` : ''}
                                    ${service.data_final ? `<p><strong>Final:</strong> ${new Date(service.data_final).toLocaleDateString('pt-BR')}</p>` : ''}
                                </div>
                                ${service.descricao_servico ? `<p class="mt-2 text-sm text-gray-700">${service.descricao_servico}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        modal.classList.remove('hidden');
        modal.classList.add('flex', 'modal-enter');
        
        hideLoading();
        
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
        if (!localProject) showError('Erro ao carregar detalhes do projeto');
        hideLoading();
    }
}

/**
 * Fecha o modal
 */
function closeModal() {
    const modal = document.getElementById('project-modal');
    modal.classList.add('modal-leave');
    
    setTimeout(() => {
        modal.classList.remove('flex', 'modal-enter', 'modal-leave');
        modal.classList.add('hidden');
    }, 300);
}

/**
 * Mostra loading
 */
function showLoading() {
    // Implementar loading spinner se necessário
    console.log('Loading...');
}

/**
 * Esconde loading
 */
function hideLoading() {
    console.log('Loading complete');
}

/**
 * Mostra erro
 */
function showError(message) {
    alert(message);
}

// Fechar modal ao clicar fora
document.addEventListener('click', (e) => {
    const modal = document.getElementById('project-modal');
    if (e.target === modal) {
        closeModal();
    }
});
