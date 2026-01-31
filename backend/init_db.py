"""
Script para inicializar o banco de dados com dados do JSON
"""
import json
from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models.project import Project, Service, Monitoring

def parse_date(date_str):
    """Converte string de data para objeto date"""
    if not date_str or date_str == "null":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def init_database():
    """Inicializa o banco de dados com dados do planilha_portos.json"""
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar se já existem dados
        if db.query(Project).count() > 0:
            print("Banco de dados já contém dados. Pulando inicialização.")
            return
        
        # Carregar dados do JSON
        with open("../planilha_portos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Mapear projetos por identificador único
        project_map = {}
        
        # Processar Tabela 00 - Cadastro
        print("Processando cadastros...")
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
            db.flush()  # Para obter o ID
            
            # Criar chave única para mapear serviços
            key = f"{item.get('Zona portuária')}|{item.get('UF')}|{item.get('Obj. de Concessão')}"
            project_map[key] = project.id
        
        db.commit()
        print(f"✓ {len(project_map)} projetos cadastrados")
        
        # Processar Tabela 01 - Serviços
        print("Processando serviços...")
        service_map = {}
        for item in data.get("Tabela 01 - Serviços", []):
            key = f"{item.get('Zona portuária')}|{item.get('UF')}|{item.get('Obj. de Concessão')}"
            project_id = project_map.get(key)
            
            if not project_id:
                print(f"⚠ Projeto não encontrado para serviço: {key}")
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
            
            # Criar chave para mapear acompanhamentos
            service_key = f"{key}|{item.get('Tipo de Serviço')}|{item.get('Fase')}|{item.get('Serviço')}|{item.get('Descrição do serviço')}"
            service_map[service_key] = service.id
        
        db.commit()
        print(f"✓ {len(service_map)} serviços cadastrados")
        
        # Processar Tabela 02 - Acompanhamento
        print("Processando acompanhamentos...")
        monitoring_count = 0
        for item in data.get("Tabela 02 - Acompanhamento", []):
            key = f"{item.get('Zona portuária')}|{item.get('UF')}|{item.get('Obj. de Concessão')}"
            service_key = f"{key}|{item.get('Tipo de Serviço')}|{item.get('Fase')}|{item.get('Serviço')}|{item.get('Descrição')}"
            service_id = service_map.get(service_key)
            
            if not service_id:
                print(f"⚠ Serviço não encontrado para acompanhamento: {service_key}")
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
            monitoring_count += 1
        
        db.commit()
        print(f"✓ {monitoring_count} acompanhamentos cadastrados")
        
        print("\n✅ Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
