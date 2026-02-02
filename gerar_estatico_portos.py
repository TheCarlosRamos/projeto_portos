#!/usr/bin/env python3
"""
Gerador de HTML estático baseado no portos.html com dados do banco
Cria uma versão estática exatamente como o Flask serve
"""

import sqlite3
import json
from datetime import datetime
import os
import re

def extrair_dados_completos_banco():
    """Extrai todos os dados do banco SQLite como o Flask faz"""
    
    # Conectar ao banco
    db_path = 'portos.db'
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Extrair projetos (mesma lógica do app.py)
        cursor.execute("""
            SELECT p.id, p.zona_portuaria, p.uf, p.obj_concessao, p.tipo, 
                   p.capex_total, p.capex_executado, p.perc_capex_executado,
                   p.data_assinatura, p.descricao, p.latitude, p.longitude,
                   p.coordenada_e_utm, p.coordenada_s_utm, p.fuso,
                   p.created_at, p.updated_at
            FROM projetos p
            ORDER BY p.zona_portuaria, p.obj_concessao
        """)
        
        projetos = []
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
                'progresso': (row['perc_capex_executado'] or 0) * 100,
                'dataAssinatura': row['data_assinatura'],
                'etapa': 'Em Andamento',
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'coordenadaEUTM': row['coordenada_e_utm'],
                'coordenadaSUTM': row['coordenada_s_utm'],
                'fuso': row['fuso'],
                'dataCriacao': row['created_at'],
                'dataAtualizacao': row['updated_at']
            }
            
            # Coordenadas para o mapa
            projeto['coordenadasLatLon'] = None
            if projeto['latitude'] and projeto['longitude']:
                projeto['coordenadasLatLon'] = {
                    'lat': projeto['latitude'],
                    'lon': projeto['longitude']
                }
            
            projetos.append(projeto)
        
        # Extrair serviços
        cursor.execute("""
            SELECT s.id, s.projeto_id, s.zona_portuaria, s.uf, s.obj_concessao,
                   s.tipo_servico, s.fase, s.servico, s.descricao_servico,
                   s.data_inicio, s.data_final, s.percentual_capex,
                   s.capex_servico_total, s.capex_servico_exec, s.perc_capex_exec,
                   s.created_at
            FROM servicos s
            ORDER BY s.projeto_id, s.data_inicio
        """)
        
        servicos = []
        for row in cursor.fetchall():
            servico = {
                'id': row['id'],
                'idProjeto': f"projeto-{row['projeto_id']}",
                'zonaPortuaria': row['zona_portuaria'],
                'uf': row['uf'],
                'objConcessao': row['obj_concessao'],
                'tipoServico': row['tipo_servico'],
                'fase': row['fase'],
                'servico': row['servico'],
                'descricao': row['descricao_servico'],
                'dataInicio': row['data_inicio'],
                'dataFim': row['data_final'],
                'percentualCapex': row['percentual_capex'],
                'capexServicoTotal': row['capex_servico_total'],
                'capexServicoExec': row['capex_servico_exec'],
                'percCapexExec': row['perc_capex_exec'],
                'dataCriacao': row['created_at']
            }
            servicos.append(servico)
        
        # Extrair acompanhamentos
        cursor.execute("""
            SELECT a.id, a.projeto_id, a.zona_portuaria, a.uf, a.obj_concessao,
                   a.tipo_servico, a.fase, a.servico, a.descricao,
                   a.percentual_executada, a.valor_executado, a.data_atualizacao,
                   a.responsavel, a.cargo, a.setor, a.riscos_tipo, a.riscos_descricao,
                   a.created_at
            FROM acompanhamento a
            ORDER BY a.projeto_id, a.data_atualizacao DESC
        """)
        
        acompanhamentos = []
        for row in cursor.fetchall():
            acompanhamento = {
                'id': row['id'],
                'idProjeto': f"projeto-{row['projeto_id']}",
                'zonaPortuaria': row['zona_portuaria'],
                'uf': row['uf'],
                'objConcessao': row['obj_concessao'],
                'tipoServico': row['tipo_servico'],
                'fase': row['fase'],
                'servico': row['servico'],
                'descricao': row['descricao'],
                'percentualExecutada': row['percentual_executada'],
                'valorExecutado': row['valor_executado'],
                'dataAtualizacao': row['data_atualizacao'],
                'responsavel': row['responsavel'],
                'cargo': row['cargo'],
                'setor': row['setor'],
                'riscosTipo': row['riscos_tipo'],
                'riscosDescricao': row['riscos_descricao'],
                'dataCriacao': row['created_at']
            }
            acompanhamentos.append(acompanhamento)
        
        conn.close()
        
        # Combinar dados como o Flask faz
        projetos_completos = []
        for projeto in projetos:
            projeto_completo = projeto.copy()
            projeto_completo['servicos'] = [s for s in servicos if s['idProjeto'] == projeto['id']]
            projeto_completo['acompanhamentos'] = [a for a in acompanhamentos if a['idProjeto'] == projeto['id']]
            projetos_completos.append(projeto_completo)
        
        print(f"✅ Dados extraídos do banco:")
        print(f"   📊 Projetos: {len(projetos_completos)}")
        print(f"   🔧 Serviços: {len(servicos)}")
        print(f"   📈 Acompanhamentos: {len(acompanhamentos)}")
        
        return projetos_completos
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados do banco: {e}")
        conn.close()
        return None

def gerar_html_estatico_portos(dados):
    """Gera HTML estático baseado no portos.html com dados embutidos"""
    
    # Ler o portos.html original
    with open('portos.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Gerar JavaScript com dados embutidos
    js_dados = f"""
// Dados do banco - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
// Versão estática - GitHub Pages
const projetosData = {json.dumps(dados, ensure_ascii=False, indent=2)};
let projetosFiltrados = [...projetosData];
let currentProject = null;
let isEditMode = false;

// Substituir função loadData para usar dados embutidos
function loadData() {{
    console.log('Carregando dados embutidos (versão estática):', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    // Gera o mapa de projetos
    generateProjectsMap(projetosData);
    
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
    
    // Atualizar contador do mapa
    if (typeof updateMapCounter === 'function') {{
        updateMapCounter(projetosData);
    }}
    
    // Adicionar event listeners
    if (typeof addEventListeners === 'function') {{
        addEventListeners();
    }}
}}
"""
    
    # Substituir as declarações de variáveis globais
    html_content = re.sub(
        r'let projetosData = \[\];.*?let isEditMode = false;',
        js_dados.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    # Substituir a função loadData original
    html_content = re.sub(
        r'// Carregar dados da API.*?addEventListeners\(\);',
        '''// Carregar dados embutidos (versão estática)
function loadData() {
    console.log('Carregando dados embutidos (versão estática):', projetosData.length, 'projetos');
    projetosFiltrados = [...projetosData];
    
    // Gera o mapa de projetos
    generateProjectsMap(projetosData);
    
    renderProjects();
    console.log('Dados carregados:', projetosData.length, 'projetos');
    
    // Atualizar contador do mapa
    if (typeof updateMapCounter === 'function') {
        updateMapCounter(projetosData);
    }
    
    // Adicionar event listeners
    if (typeof addEventListeners === 'function') {
        addEventListeners();
    }
}''',
        html_content,
        flags=re.DOTALL
    )
    
    # Adicionar banner versão estática
    banner = f"""
<!-- BANNER VERSÃO ESTÁTICA - BASEADO NO PORTOS.HTML -->
<div style="position: fixed; top: 0; left: 0; right: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 8px; font-size: 12px; z-index: 9999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    🚢 Versão Estática - Baseado no portos.html | Dados do banco em {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
    <a href="https://github.com/TheCarlosRamos/projeto_portos" target="_blank" style="color: white; text-decoration: underline;">Ver código</a>
</div>
<div style="height: 40px;"></div>
"""
    
    # Inserir banner após <body>
    html_content = html_content.replace('<body>', '<body>' + banner)
    
    # Salvar HTML estático
    with open('../index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML estático baseado em portos.html gerado: ../index.html")
    print(f"📊 {len(dados)} projetos com dados completos")
    print(f"🌐 Pronto para GitHub Pages!")
    
    return len(dados)

def main():
    """Função principal"""
    print("🔍 Extraindo dados do banco para versão estática do portos.html...")
    
    # Mudar para o diretório correto
    os.chdir('app/present_tela')
    
    # Extrair dados do banco
    dados = extrair_dados_completos_banco()
    
    if dados:
        print("\n📝 Gerando HTML estático baseado no portos.html...")
        projetos_count = gerar_html_estatico_portos(dados)
        print(f"\n🎉 Sucesso! HTML estático com {projetos_count} projetos gerado!")
        print("📋 Este HTML é idêntico ao servido pelo Flask, mas com dados embutidos")
    else:
        print("❌ Falha ao extrair dados do banco")

if __name__ == "__main__":
    main()
