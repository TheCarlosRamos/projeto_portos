"""
Inicializa o banco com dados do JSON (para Vercel)
"""
import json
import os
from datetime import datetime
from pathlib import Path

# Dados embutidos do planilha_portos.json
INITIAL_DATA = {
    "Tabela 00 - Cadastro": [
        {
            "Zona portuária": "Porto Organizado de Santos",
            "UF": "SP",
            "Obj. de Concessão": "TECON 10",
            "Tipo": "Arrendamento",
            "CAPEX Total": 6454903000,
            "CAPEX Executado": 40473675.0,
            "% CAPEX Executado": 0.006270222031221848,
            "Data de assinatura do contrato": None,
            "Descrição": "Terminal destinado à movimentação e armazenagem de carga conteinerizada e carga geral.",
            "Latitude": -23.926132,
            "Longitude": -46.34027
        },
        {
            "Zona portuária": "Não se aplica",
            "UF": "MT; MS",
            "Obj. de Concessão": "Hidrovia do Paraguai",
            "Tipo": "Concessão",
            "CAPEX Total": 63796000,
            "CAPEX Executado": None,
            "% CAPEX Executado": 0.0,
            "Data de assinatura do contrato": None,
            "Descrição": "Hidrovia no trecho brasileiro fazendo divisa com Paraguai e Bolívia.",
            "Latitude": None,
            "Longitude": None
        },
        {
            "Zona portuária": "Porto Organizado de Maceió",
            "UF": "AL",
            "Obj. de Concessão": "TPM Macéio",
            "Tipo": "Arrendamento",
            "CAPEX Total": 1978000,
            "CAPEX Executado": None,
            "% CAPEX Executado": 0.0,
            "Data de assinatura do contrato": None,
            "Descrição": "Terminal destinado a movimentação de passageiros.",
            "Latitude": None,
            "Longitude": None
        },
        {
            "Zona portuária": "Porto Organizado do Rio de Janeiro",
            "UF": "RJ",
            "Obj. de Concessão": "RDJ07",
            "Tipo": "Arrendamento",
            "CAPEX Total": 101741000,
            "CAPEX Executado": None,
            "% CAPEX Executado": 0.0,
            "Data de assinatura do contrato": None,
            "Descrição": "Terminal portuário destinado à movimentação e armazenagem de carga para apoio logístico Offshore.",
            "Latitude": -22.896621,
            "Longitude": -43.209639
        },
        {
            "Zona portuária": "Não se aplica",
            "UF": "PR",
            "Obj. de Concessão": "Canal de Paranaguá",
            "Tipo": "Concessão",
            "CAPEX Total": 1226475000,
            "CAPEX Executado": None,
            "% CAPEX Executado": 0.0,
            "Data de assinatura do contrato": "2026-02-20",
            "Descrição": "Acesso aquaviário (canal de acesso) ao Porto de Paranaguá.",
            "Latitude": -25.492142,
            "Longitude": -48.479187
        },
        {
            "Zona portuária": "Porto Organizado de São Sebastião",
            "UF": "SP",
            "Obj. de Concessão": "SSB01",
            "Tipo": "Arrendamento",
            "CAPEX Total": 656085000,
            "CAPEX Executado": None,
            "% CAPEX Executado": 0.0,
            "Data de assinatura do contrato": None,
            "Descrição": "Pátio de cargas para movimentação de carga conteinerizada, dentre outras.",
            "Latitude": -23.812704,
            "Longitude": -45.400052
        }
    ],
    "Tabela 01 - Serviços": [
        {
            "Zona portuária": "Não se aplica",
            "UF": "PR",
            "Obj. de Concessão": "Canal de Paranaguá",
            "Tipo de Serviço": "CMO",
            "Fase": "1ª",
            "Serviço": "Dragagem de Implantação de canal",
            "Descrição do serviço": "Evolução para  13,3m",
            "Prazo início (anos)": 3,
            "Data de início": "2028-02-20",
            "Prazo final (anos)": 3.0,
            "Data final": "2029-02-19",
            "Fonte (Prazo)": "EVTEA - Plano de Exploração",
            "% de CAPEX para o serviço": 0.1,
            "CAPEX do Serviço (total)": 122647500,
            "CAPEX do Serviço (exec.)": 40473675.0,
            "% CAPEX exec.": 0.33,
            "Fonte (% do CAPEX)": "Estimado"
        },
        {
            "Zona portuária": "Não se aplica",
            "UF": "PR",
            "Obj. de Concessão": "Canal de Paranaguá",
            "Tipo de Serviço": "CMO",
            "Fase": "1ª",
            "Serviço": "Dragagem de Implantação de berços",
            "Descrição do serviço": "a) berços 201-215; e b) berços 216-218",
            "Prazo início (anos)": 3,
            "Data de início": "2028-02-20",
            "Prazo final (anos)": 5.0,
            "Data final": "2031-02-19",
            "Fonte (Prazo)": "EVTEA - Plano de Exploração",
            "% de CAPEX para o serviço": 0.1,
            "CAPEX do Serviço (total)": 122647500,
            "CAPEX do Serviço (exec.)": None,
            "% CAPEX exec.": 0.0,
            "Fonte (% do CAPEX)": "Estimado"
        }
    ],
    "Tabela 02 - Acompanhamento": [
        {
            "Zona portuária": "Não se aplica",
            "UF": "PR",
            "Obj. de Concessão": "Canal de Paranaguá",
            "Tipo de Serviço": "CMO",
            "Fase": "1ª",
            "Serviço": "Dragagem de Implantação de canal",
            "Descrição": "Evolução para  13,3m",
            "% executada": 0.1,
            "Valor executado": 12264750,
            "Data da atualização": "2029-06-06",
            "Responsável": "Mateus",
            "Cargo": "Analista",
            "Setor": "PPI",
            "Riscos Relacionados (Tipo)": "Meio Ambiente",
            "Riscos Relacionados (Descrição)": "Parte do trecho está com pendência de licenciamento ambiental"
        }
    ]
}

def parse_date(date_str):
    """Converte string de data para objeto date"""
    if not date_str or date_str == "null":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def get_initial_data():
    """Retorna os dados iniciais"""
    return INITIAL_DATA

def init_from_json(db):
    """Inicializa o banco com dados do JSON"""
    from app.models.project import Project, Service, Monitoring
    
    # Verificar se já existem dados
    if db.query(Project).count() > 0:
        return False
    
    data = get_initial_data()
    project_map = {}
    
    # Processar cadastros
    for item in data.get("Tabela 00 - Cadastro", []):
        project = Project(
            zona_portuaria=item.get("Zona portuária"),
            uf=item.get("UF"),
            obj_concessao=item.get("Obj. de Concessão"),
            tipo=item.get("Tipo"),
            capex_total=item.get("CAPEX Total"),
            capex_executado=item.get("CAPEX Executado"),
            perc_capex_executado=item.get("% CAPEX Executado"),
            data_assinatura=parse_date(item.get("Data de assinatura do contrato")),
            descricao=item.get("Descrição"),
            latitude=item.get("Latitude"),
            longitude=item.get("Longitude")
        )
        db.add(project)
        db.flush()
        
        key = f"{item.get('Zona portuária')}|{item.get('UF')}|{item.get('Obj. de Concessão')}"
        project_map[key] = project.id
    
    db.commit()
    
    # Processar serviços
    service_map = {}
    for item in data.get("Tabela 01 - Serviços", []):
        key = f"{item.get('Zona portuária')}|{item.get('UF')}|{item.get('Obj. de Concessão')}"
        project_id = project_map.get(key)
        
        if not project_id:
            continue
        
        service = Service(
            project_id=project_id,
            tipo_servico=item.get("Tipo de Serviço"),
            fase=item.get("Fase"),
            servico=item.get("Serviço"),
            descricao_servico=item.get("Descrição do serviço"),
            prazo_inicio_anos=item.get("Prazo início (anos)"),
            data_inicio=parse_date(item.get("Data de início")),
            prazo_final_anos=item.get("Prazo final (anos)"),
            data_final=parse_date(item.get("Data final")),
            fonte_prazo=item.get("Fonte (Prazo)"),
            perc_capex=item.get("% de CAPEX para o serviço"),
            capex_servico_total=item.get("CAPEX do Serviço (total)"),
            capex_servico_exec=item.get("CAPEX do Serviço (exec.)"),
            perc_capex_exec=item.get("% CAPEX exec."),
            fonte_perc_capex=item.get("Fonte (% do CAPEX)")
        )
        db.add(service)
        db.flush()
        
        service_key = f"{key}|{item.get('Tipo de Serviço')}|{item.get('Fase')}|{item.get('Serviço')}|{item.get('Descrição do serviço')}"
        service_map[service_key] = service.id
    
    db.commit()
    
    # Processar acompanhamentos
    for item in data.get("Tabela 02 - Acompanhamento", []):
        key = f"{item.get('Zona portuária')}|{item.get('UF')}|{item.get('Obj. de Concessão')}"
        service_key = f"{key}|{item.get('Tipo de Serviço')}|{item.get('Fase')}|{item.get('Serviço')}|{item.get('Descrição')}"
        service_id = service_map.get(service_key)
        
        if not service_id:
            continue
        
        monitoring = Monitoring(
            service_id=service_id,
            descricao=item.get("Descrição"),
            perc_executada=item.get("% executada"),
            valor_executado=item.get("Valor executado"),
            data_atualizacao=parse_date(item.get("Data da atualização")),
            responsavel=item.get("Responsável"),
            cargo=item.get("Cargo"),
            setor=item.get("Setor"),
            risco_tipo=item.get("Riscos Relacionados (Tipo)"),
            risco_descricao=item.get("Riscos Relacionados (Descrição)")
        )
        db.add(monitoring)
    
    db.commit()
    return True
