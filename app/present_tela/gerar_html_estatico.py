#!/usr/bin/env python3
"""
Gerador de HTML estático para GitHub Pages
Gera um arquivo HTML com todos os dados embutidos
"""

import json
import os
from datetime import datetime

def gerar_html_estatico():
    """Gera HTML estático com dados embutidos"""
    
    # Carregar dados do JSON
    with open('planilha_portos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    cadastros = dados['Tabela 00 - Cadastro']
    servicos = dados['Tabela 01 - Serviços']
    acompanhamentos = dados['Tabela 02 - Acompanhamento']
    
    # Processar projetos
    projetos_data = []
    for i, cadastro in enumerate(cadastros):
        projeto_id = f"projeto-{i}"
        
        # Calcular progresso
        progresso = 0
        if cadastro['CAPEX Total'] and cadastro['CAPEX Total'] > 0:
            if cadastro['CAPEX Executado']:
                progresso = (cadastro['CAPEX Executado'] / cadastro['CAPEX Total']) * 100
        
        # Coordenadas
        coordenadas_lat_lon = None
        if cadastro['Latitude'] and cadastro['Longitude']:
            coordenadas_lat_lon = {
                'lat': cadastro['Latitude'],
                'lon': cadastro['Longitude']
            }
        
        projeto = {
            'id': projeto_id,
            'zona': cadastro['Zona portuária'],
            'uf': cadastro['UF'],
            'objConcessao': cadastro['Obj. de Concessão'],
            'tipo': cadastro['Tipo'],
            'descricao': cadastro['Descrição'],
            'capexTotal': cadastro['CAPEX Total'],
            'capexExecutado': cadastro['CAPEX Executado'],
            'progresso': round(progresso, 2),
            'coordenadasLatLon': coordenadas_lat_lon,
            'dataAssinatura': cadastro['Data de assinatura do contrato'],
            'etapa': 'Em Andamento' if progresso < 100 else 'Concluído'
        }
        
        projetos_data.append(projeto)
    
    # Gerar JavaScript com dados embutidos
    js_dados = f"""
// Dados dos projetos - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
const projetosData = {json.dumps(projetos_data, ensure_ascii=False, indent=2)};
let projetosFiltrados = [...projetosData];
let currentProject = null;
let isEditMode = false;

// Função para carregar dados (agora usa dados embutidos)
async function loadData() {{
    console.log('Carregando dados embutidos:', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    // Gera o mapa de projetos
    generateProjectsMap(projetosData);
    
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
    
    // Atualizar contador do mapa
    updateMapCounter();
    
    // Adicionar event listeners
    addEventListeners();
}}
"""
    
    # Ler o HTML original
    with open('portos.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Substituir a função loadData original
    import re
    pattern = r'// Carregar dados ao iniciar\s+async function loadData\(\) \{[^}]*\}'
    replacement = js_dados.strip()
    html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    # Remover chamadas de API externas
    html_content = html_content.replace(
        'const response = await fetch(\'/api/projects\');',
        '// Dados já carregados localmente'
    )
    html_content = html_content.replace(
        'projetosData = await response.json();',
        '// Dados já carregados na variável projetosData'
    )
    
    # Adicionar banner indicando versão estática
    banner_estatico = """
<!-- BANNER VERSÃO ESTÁTICA -->
<div style="position: fixed; top: 0; left: 0; right: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 8px; font-size: 12px; z-index: 9999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    🚢 Versão Estática - GitHub Pages | Dados atualizados em {} | 
    <a href="https://github.com/TheCarlosRamos/projeto_portos" target="_blank" style="color: white; text-decoration: underline;">Ver código</a>
</div>

<!-- ESPAÇO PARA O BANNER -->
<div style="height: 40px;"></div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    # Inserir banner após o <body>
    html_content = html_content.replace('<body>', '<body>' + banner_estatico)
    
    # Salvar HTML estático
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML estático gerado: index.html")
    print(f"📊 {len(projetos_data)} projetos embutidos")
    print(f"🌐 Pronto para GitHub Pages!")
    
    return len(projetos_data)

if __name__ == "__main__":
    gerar_html_estatico()
