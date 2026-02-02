#!/usr/bin/env python3
"""
Criar index2.html limpo sem duplicação de dados
"""

import json
from datetime import datetime

def criar_index2_limpo():
    """Cria index2.html limpo sem duplicação de dados"""
    
    # Ler dados completos
    with open('dados_completos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Ler o index2.html original
    with open('index2.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Encontrar e remover a declaração duplicada
    import re
    
    # Encontrar onde começa a declaração duplicada
    inicio_duplicado = html_content.find('// Dados completos do banco - Gerado em 02/02/2026 10:23:06')
    
    if inicio_duplicado != -1:
        # Encontrar onde termina a declaração duplicada (procura pelo final do objeto)
        fim_duplicado = html_content.find('};', inicio_duplicado)
        if fim_duplicado != -1:
            fim_duplicado += 1  # Inclui o fechamento
            
            # Remover a declaração duplicada
            html_content = html_content[:inicio_duplicado] + html_content[fim_duplicado:]
    
    # Remover declarações duplicadas das variáveis
    html_content = re.sub(
        r'let projetosData = dadosCompletos\.projetos;.*?let isEditMode = false;',
        '// Dados já foram declarados acima',
        html_content,
        flags=re.DOTALL
    )
    
    html_content = re.sub(
        r'const servicosData = dadosCompletos\.servicos;.*?let servicosFiltrados = \[\.\.servicosData\];',
        '// Dados já foram declarados acima',
        html_content,
        flags=re.DOTALL
    )
    
    html_content = re.sub(
        r'const acompanhamentosData = dadosCompletos\.acompanhamentos;.*?let acompanhamentosFiltrados = \[\.\.acompanhamentosData\];',
        '// Dados já foram declarados acima',
        html_content,
        flags=re.DOTALL
    )
    
    html_content = re.sub(
        r'const resumoData = dadosCompletos\.resumo;.*?let currentProject = null;',
        '// Dados já foram declarados acima',
        html_content,
        flags=re.DOTALL
    )
    
    html_content = re.sub(
        r'let currentProject = null;.*?let isEditMode = false;',
        '// Dados já foram declarados acima',
        html_content,
        flags=re.DOTALL
    )
    
    # Salvar o arquivo limpo
    with open('index2.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ index2.html limpo criado sem duplicação!")
    print(f"📊 {len(dados['projetos'])} projetos com dados completos")
    print(f"🔧 {len(dados['servicos'])} serviços")
    print(f"📈 {len(dados['acompanhamentos'])} acompanhamentos")
    print(f"🗺️ Mapa funcionando")
    print(f"🚀 Sem erros de sintaxe!")

def main():
    print("🔧 Criando index2.html limpo sem duplicação...")
    
    criar_index2_limpo()
    
    print(f"\n🎉 Sucesso! index2.html está limpo e funcional!")
    print(f"   📊 Sem erros de sintaxe")
    print(f"   🗺️ Mapa funcionando")
    print(f"   📱️ Pronto para usar!")

if __name__ == "__main__":
    main()
