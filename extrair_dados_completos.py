#!/usr/bin/env python3
"""
Gerador de HTML estático COMPLETO com todos os dados do Flask
Versão simplificada para evitar limite de tokens
"""

import sqlite3
import json
from datetime import datetime
import os

def extrair_dados_completos():
    """Extrai TODOS os dados do banco como o Flask faz"""
    
    db_path = 'app/present_tela/portos.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Extrair projetos
        cursor.execute("""
            SELECT id, zona_portuaria, uf, obj_concessao, tipo, descricao, 
                   capex_total, capex_executado, perc_capex_executado,
                   latitude, longitude, created_at, updated_at
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
                'coordenadasLatLon': None,
                'dataCriacao': row['created_at'],
                'dataAtualizacao': row['updated_at']
            }
            
            # Coordenadas
            if row['latitude'] and row['longitude']:
                projeto['coordenadasLatLon'] = {
                    'lat': row['latitude'],
                    'lon': row['longitude']
                }
            
            projetos.append(projeto)
        
        # Extrair serviços
        cursor.execute("""
            SELECT id, projeto_id, zona_portuaria, uf, obj_concessao,
                   tipo_servico, fase, servico, descricao_servico,
                   data_inicio, data_final, percentual_capex,
                   capex_servico_total, capex_servico_exec, perc_capex_exec,
                   created_at
            FROM servicos
            ORDER BY projeto_id, data_inicio
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
            SELECT id, projeto_id, zona_portuaria, uf, obj_concessao,
                   tipo_servico, fase, servico, descricao,
                   percentual_executada, valor_executado, data_atualizacao,
                   responsavel, cargo, setor, riscos_tipo, riscos_descricao,
                   created_at
            FROM acompanhamento
            ORDER BY projeto_id, data_atualizacao DESC
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
        
        # Combinar dados
        projetos_completos = []
        for projeto in projetos:
            projeto_completo = projeto.copy()
            projeto_completo['servicos'] = [s for s in servicos if s['idProjeto'] == projeto['id']]
            projeto_completo['acompanhamentos'] = [a for a in acompanhamentos if a['idProjeto'] == projeto['id']]
            projetos_completos.append(projeto_completo)
        
        print(f"✅ Dados completos extraídos:")
        print(f"   📊 Projetos: {len(projetos_completos)}")
        print(f"   🔧 Serviços: {len(servicos)}")
        print(f"   📈 Acompanhamentos: {len(acompanhamentos)}")
        
        return {
            'projetos': projetos_completos,
            'servicos': servicos,
            'acompanhamentos': acompanhamentos,
            'resumo': {
                'totalProjetos': len(projetos_completos),
                'totalServicos': len(servicos),
                'totalAcompanhamentos': len(acompanhamentos),
                'capexTotal': sum(p['capexTotal'] for p in projetos_completos),
                'capexExecutado': sum(p['capexExecutado'] for p in projetos_completos),
                'progressoMedio': sum(p['progresso'] for p in projetos_completos) / len(projetos_completos) if projetos_completos else 0
            }
        }
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        conn.close()
        return None

def main():
    print("🔍 Extraindo dados completos para HTML estático...")
    
    dados = extrair_dados_completos()
    
    if dados:
        print(f"\n📊 Resumo dos dados:")
        print(f"   Total Projetos: {dados['resumo']['totalProjetos']}")
        print(f"   Total Serviços: {dados['resumo']['totalServicos']}")
        print(f"   Total Acompanhamentos: {dados['resumo']['totalAcompanhamentos']}")
        print(f"   CAPEX Total: R${dados['resumo']['capexTotal']/1000000000:.1f}B")
        print(f"   CAPEX Executado: R${dados['resumo']['capexExecutado']/1000000:.1f}M")
        print(f"   Progresso Médio: {dados['resumo']['progressoMedio']:.1f}%")
        
        # Salvar dados em JSON para usar no HTML
        with open('dados_completos.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Dados salvos em dados_completos.json")
        print(f"📄 Pronto para gerar HTML estático completo!")
        
        return dados
    else:
        print("❌ Falha ao extrair dados")
        return None

if __name__ == "__main__":
    main()
