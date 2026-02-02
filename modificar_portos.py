#!/usr/bin/env python3
"""
Modificador do portos.html para funcionar com Flask e Live Server
Adiciona fallback inteligente para dados estáticos
"""

import sqlite3
import json
from datetime import datetime
import os
import re

def extrair_dados_banco():
    """Extrai dados do banco SQLite"""
    
    db_path = 'portos.db'
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

def modificar_portos_html(dados):
    """Modifica portos.html para ter fallback inteligente"""
    
    # Ler o portos.html original
    with open('portos.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Gerar JavaScript com dados de fallback
    js_fallback = f"""
// Dados de fallback - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
// Usado quando API não está disponível (Live Server)
const dadosFallback = {json.dumps(dados, ensure_ascii=False, indent=2)};

// Função loadData com fallback inteligente
async function loadData() {{
    console.log('Tentando carregar dados...');
    
    // Tentar carregar da API primeiro (Flask)
    try {{
        const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const isPort5000 = window.location.port === '5000';
        
        if (isLocalhost && isPort5000) {{
            console.log('Detectado Flask server, tentando API...');
            const response = await fetch('/api/projects');
            
            if (response.ok) {{
                const data = await response.json();
                projetosData = data;
                projetosFiltrados = [...projetosData];
                console.log('✅ Dados carregados da API Flask:', data.length, 'projetos');
            }} else {{
                throw new Error('API não respondeu');
            }}
        }} else {{
            throw new Error('Não é Flask server');
        }}
    }} catch (error) {{
        console.log('❌ API não disponível, usando dados estáticos (fallback)');
        console.log('Erro:', error.message);
        
        // Usar dados estáticos como fallback
        projetosData = dadosFallback;
        projetosFiltrados = [...projetosData];
        console.log('✅ Dados carregados do fallback:', dadosFallback.length, 'projetos');
        
        // Mostrar aviso
        mostrarAvisoFallback();
    }}
    
    // Carregar interface
    generateProjectsMap(projetosData);
    renderProjects();
    
    // Atualizar contador
    if (typeof updateMapCounter === 'function') {{
        updateMapCounter(projetosData);
    }}
    
    // Adicionar event listeners
    if (typeof addEventListeners === 'function') {{
        addEventListeners();
    }}
}}

// Mostrar aviso de fallback
function mostrarAvisoFallback() {{
    const aviso = document.createElement('div');
    aviso.style.cssText = `
        position: fixed;
        top: 60px;
        right: 20px;
        background: #f59e0b;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        font-size: 14px;
        max-width: 300px;
    `;
    aviso.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-info-circle"></i>
            <div>
                <strong>Modo Offline</strong><br>
                <small>Usando dados estáticos embutidos</small>
            </div>
        </div>
    `;
    
    document.body.appendChild(aviso);
    
    // Remover após 5 segundos
    setTimeout(() => {{
        if (aviso.parentNode) {{
            avivo.parentNode.removeChild(aviso);
        }}
    }}, 5000);
}}
"""
    
    # Substituir a função loadData original
    html_content = re.sub(
        r'// Carregar dados da API.*?addEventListeners\(\);',
        js_fallback.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    # Adicionar banner informativo
    banner = f"""
<!-- BANNER VERSÃO HÍBRIDA -->
<div id="mode-banner" style="position: fixed; top: 0; left: 0; right: 0; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-align: center; padding: 8px; font-size: 12px; z-index: 9999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    🚢 Versão Híbrida - Flask + Live Server | Dados em {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
    <span id="mode-indicator">Detectando modo...</span>
</div>
<div style="height: 40px;"></div>

<script>
// Atualizar banner baseado no modo
document.addEventListener('DOMContentLoaded', () => {{
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const isPort5000 = window.location.port === '5000';
    const indicator = document.getElementById('mode-indicator');
    
    if (isLocalhost && isPort5000) {{
        indicator.innerHTML = '🔧 <strong>Modo Flask</strong> - API dinâmica';
    }} else {{
        indicator.innerHTML = '📱 <strong>Modo Live Server</strong> - Dados estáticos';
    }}
}});
</script>
"""
    
    # Inserir banner após <body>
    html_content = html_content.replace('<body>', '<body>' + banner)
    
    # Salvar portos.html modificado
    with open('portos.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ portos.html modificado para funcionar com Flask e Live Server")
    print(f"📊 {len(dados)} projetos incluídos como fallback")
    
    return len(dados)

def main():
    print("🔧 Modificando portos.html para funcionar com Flask e Live Server...")
    
    # Mudar para o diretório correto
    os.chdir('app/present_tela')
    
    # Extrair dados do banco
    dados = extrair_dados_banco()
    
    if dados:
        projetos_count = modificar_portos_html(dados)
        print(f"\n🎉 Sucesso! portos.html agora funciona em ambos os modos:")
        print(f"   🔧 Flask (localhost:5000) - API dinâmica")
        print(f"   📱 Live Server (localhost:5500) - Dados estáticos")
        print(f"   📊 {projetos_count} projetos disponíveis")
    else:
        print("❌ Falha ao extrair dados do banco")

if __name__ == "__main__":
    main()
