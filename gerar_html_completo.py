#!/usr/bin/env python3
"""
Gerador de HTML estático completo com dados do banco SQLite
Extrai todas as informações que portos.html usa do banco
"""

import sqlite3
import json
from datetime import datetime
import os

def extrair_dados_banco():
    """Extrai todos os dados do banco SQLite"""
    
    # Conectar ao banco
    db_path = 'portos.db'
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
    cursor = conn.cursor()
    
    dados_completos = {
        'projetos': [],
        'servicos': [],
        'acompanhamentos': []
    }
    
    try:
        # Extrair projetos
        cursor.execute("""
            SELECT id, zona_portuaria, uf, obj_concessao, tipo, descricao, 
                   capex_total, capex_executado, perc_capex_executado, data_assinatura,
                   latitude, longitude, coordenada_e_utm, coordenada_s_utm, fuso,
                   created_at, updated_at
            FROM projetos
            ORDER BY zona_portuaria, obj_concessao
        """)
        
        for row in cursor.fetchall():
            projeto = {
                'id': f"projeto-{row['id']}",
                'zona': row['zona_portuaria'] or 'Não informado',
                'uf': row['uf'] or 'Não informado',
                'objConcessao': row['obj_concessao'] or 'Não informado',
                'tipo': row['tipo'] or 'Não informado',
                'descricao': row['descricao'] or 'Sem descrição disponível',
                'capexTotal': row['capex_total'] or 0,
                'capexExecutado': row['capex_executado'] or 0,
                'dataAssinatura': row['data_assinatura'],
                'etapa': 'Em Andamento',  # Calculado baseado no progresso
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'coordenadaEUTM': row['coordenada_e_utm'],
                'coordenadaSUTM': row['coordenada_s_utm'],
                'fuso': row['fuso'],
                'dataCriacao': row['created_at'],
                'dataAtualizacao': row['updated_at']
            }
            
            # Calcular progresso
            if projeto['capexTotal'] > 0 and projeto['capexExecutado']:
                projeto['progresso'] = (projeto['capexExecutado'] / projeto['capexTotal']) * 100
            else:
                projeto['progresso'] = 0
            
            # Coordenadas para o mapa
            projeto['coordenadasLatLon'] = None
            if projeto['latitude'] and projeto['longitude']:
                projeto['coordenadasLatLon'] = {
                    'lat': projeto['latitude'],
                    'lon': projeto['longitude']
                }
            
            dados_completos['projetos'].append(projeto)
        
        # Extrair serviços
        cursor.execute("""
            SELECT id, projeto_id, zona_portuaria, uf, obj_concessao, tipo_servico,
                   fase, servico, descricao_servico, data_inicio, data_final,
                   percentual_capex, capex_servico_total, capex_servico_exec,
                   created_at
            FROM servicos
            ORDER BY projeto_id, data_inicio
        """)
        
        for row in cursor.fetchall():
            servico = {
                'id': row['id'],
                'idProjeto': f"projeto-{row['projeto_id']}",
                'zonaPortuaria': row['zona_portuaria'] or 'Não informado',
                'uf': row['uf'] or 'Não informado',
                'objConcessao': row['obj_concessao'] or 'Não informado',
                'tipoServico': row['tipo_servico'] or 'Não informado',
                'fase': row['fase'] or 'Não informado',
                'servico': row['servico'] or 'Não informado',
                'descricao': row['descricao_servico'] or 'Sem descrição',
                'dataInicio': row['data_inicio'],
                'dataFim': row['data_final'],
                'percentualCapex': row['percentual_capex'] or 0,
                'capexServicoTotal': row['capex_servico_total'] or 0,
                'capexServicoExec': row['capex_servico_exec'] or 0,
                'dataCriacao': row['created_at']
            }
            dados_completos['servicos'].append(servico)
        
        # Extrair acompanhamentos
        cursor.execute("""
            SELECT id, projeto_id, zona_portuaria, uf, obj_concessao, tipo_servico,
                   fase, servico, descricao, percentual_executada, valor_executado,
                   data_atualizacao, responsavel, cargo, setor, riscos_tipo, riscos_descricao
            FROM acompanhamento
            ORDER BY projeto_id, data_atualizacao DESC
        """)
        
        for row in cursor.fetchall():
            acompanhamento = {
                'id': row['id'],
                'idProjeto': f"projeto-{row['projeto_id']}",
                'zonaPortuaria': row['zona_portuaria'] or 'Não informado',
                'uf': row['uf'] or 'Não informado',
                'objConcessao': row['obj_concessao'] or 'Não informado',
                'tipoServico': row['tipo_servico'] or 'Não informado',
                'fase': row['fase'] or 'Não informado',
                'servico': row['servico'] or 'Não informado',
                'descricao': row['descricao'] or 'Sem descrição',
                'percentualExecutada': row['percentual_executada'] or 0,
                'valorExecutado': row['valor_executado'] or 0,
                'dataAtualizacao': row['data_atualizacao'],
                'responsavel': row['responsavel'] or 'Não informado',
                'cargo': row['cargo'] or 'Não informado',
                'setor': row['setor'] or 'Não informado',
                'riscosTipo': row['riscos_tipo'] or 'Não informado',
                'riscosDescricao': row['riscos_descricao'] or 'Não informado'
            }
            dados_completos['acompanhamentos'].append(acompanhamento)
        
        conn.close()
        
        print(f"✅ Dados extraídos do banco:")
        print(f"   📊 Projetos: {len(dados_completos['projetos'])}")
        print(f"   🔧 Serviços: {len(dados_completos['servicos'])}")
        print(f"   📈 Acompanhamentos: {len(dados_completos['acompanhamentos'])}")
        
        return dados_completos
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados do banco: {e}")
        conn.close()
        return None

def gerar_html_completo(dados):
    """Gera HTML estático completo com todos os dados"""
    
    # Ler o template do portos.html
    with open('portos.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # Gerar JavaScript com dados completos
    js_dados = f"""
// Dados completos do banco - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
const dadosBanco = {json.dumps(dados, ensure_ascii=False, indent=2)};

// Extrair projetos para compatibilidade
const projetosData = dadosBanco.projetos.map(projeto => ({{
    ...projeto,
    servicos: dadosBanco.servicos.filter(s => s.idProjeto === projeto.id),
    acompanhamentos: dadosBanco.acompanhamentos.filter(a => a.idProjeto === projeto.id)
}}));

let projetosFiltrados = [...projetosData];
let currentProject = null;
let isEditMode = false;

// Substituir função loadData para usar dados do banco
function loadData() {{
    console.log('Carregando dados do banco (estático):', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    // Gera o mapa de projetos
    generateProjectsMap(projetosData);
    
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
    
    // Atualizar contador do mapa
    updateMapCounter(projetosData);
    
    // Adicionar event listeners
    addEventListeners();
}}
"""
    
    # Substituir a seção de dados no HTML
    import re
    
    # Encontrar e substituir as declarações de variáveis
    html_template = re.sub(
        r'let projetosData = \[\];.*?let isEditMode = false;',
        js_dados.strip(),
        html_template,
        flags=re.DOTALL
    )
    
    # Substituir a função loadData
    html_template = re.sub(
        r'// Carregar dados da API.*?addEventListeners\(\);',
        '''// Carregar dados do banco (versão estática)
function loadData() {
    console.log('Carregando dados do banco (estático):', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    // Gera o mapa de projetos
    generateProjectsMap(projetosData);
    
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
    
    // Atualizar contador do mapa
    updateMapCounter(projetosData);
    
    // Adicionar event listeners
    addEventListeners();
}''',
        html_template,
        flags=re.DOTALL
    )
    
    # Adicionar banner
    banner = f"""
<!-- BANNER VERSÃO ESTÁTICA COMPLETA -->
<div style="position: fixed; top: 0; left: 0; right: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 8px; font-size: 12px; z-index: 9999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    🚢 Versão Estática Completa - GitHub Pages | Dados do banco em {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
    <a href="https://github.com/TheCarlosRamos/projeto_portos" target="_blank" style="color: white; text-decoration: underline;">Ver código</a>
</div>
<div style="height: 40px;"></div>
"""
    
    # Inserir banner após <body>
    html_template = html_template.replace('<body>', '<body>' + banner)
    
    # Salvar HTML estático completo
    with open('../index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ HTML estático completo gerado: ../index.html")
    print(f"📊 {len(dados['projetos'])} projetos com dados completos")
    print(f"🌐 Pronto para GitHub Pages!")
    
    return len(dados['projetos'])

def main():
    """Função principal"""
    print("🔍 Extraindo dados do banco SQLite...")
    
    # Mudar para o diretório do banco
    os.chdir('app/present_tela')
    
    # Extrair dados do banco
    dados = extrair_dados_banco()
    
    if dados:
        print("\n📝 Gerando HTML estático completo...")
        projetos_count = gerar_html_completo(dados)
        print(f"\n🎉 Sucesso! HTML estático com {projetos_count} projetos gerado!")
    else:
        print("❌ Falha ao extrair dados do banco")

if __name__ == "__main__":
    main()
