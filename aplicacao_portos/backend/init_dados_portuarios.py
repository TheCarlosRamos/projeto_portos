"""
Script para inicializar dados básicos do sistema portuário
Baseado na estrutura real das planilhas
"""
import sys
from pathlib import Path

# Adicionar diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models_portuarios import Base, ZonaPortuaria, TipoServico, Risco

def inicializar_dados():
    """Inicializa dados básicos do sistema portuário"""
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Inicializando dados basicos do sistema portuario...")
        
        # Zonas Portuárias (baseadas na planilha real)
        zonas_portuarias = [
            {"nome": "Porto Organizado de Santos", "uf": "SP"},
            {"nome": "Porto Organizado do Rio de Janeiro", "uf": "RJ"},
            {"nome": "Porto Organizado de Maceió", "uf": "AL"},
            {"nome": "Porto Organizado de São Sebastião", "uf": "SP"},
            {"nome": "Não se aplica - MT/MS", "uf": "MT; MS"},  # Para Hidrovia do Paraguai
            {"nome": "Não se aplica - PR", "uf": "PR"},  # Para Canal de Paranaguá
        ]
        
        for zona_data in zonas_portuarias:
            # Verificar se já existe (evitar duplicação de "Não se aplica")
            existente = db.query(ZonaPortuaria).filter(
                ZonaPortuaria.nome == zona_data["nome"],
                ZonaPortuaria.uf == zona_data["uf"]
            ).first()
            
            if not existente:
                zona = ZonaPortuaria(**zona_data)
                db.add(zona)
                print(f"  Zona Portuaria criada: {zona_data['nome']} - {zona_data['uf']}")
        
        # Tipos de Serviço (baseados na planilha real)
        tipos_servico = [
            "CMO",  # Construção, Manutenção e Operação
            "Disponibilidade de Infraestrutura",
        ]
        
        for tipo_nome in tipos_servico:
            existente = db.query(TipoServico).filter(
                TipoServico.nome == tipo_nome
            ).first()
            
            if not existente:
                tipo = TipoServico(nome=tipo_nome)
                db.add(tipo)
                print(f"  Tipo de Servico criado: {tipo_nome}")
        
        # Riscos (baseados na planilha real)
        riscos = [
            {"tipo": "Meio Ambiente", "descricao": "Riscos relacionados ao licenciamento e impacto ambiental"},
            {"tipo": "Financeiro", "descricao": "Riscos de orçamento e financiamento"},
            {"tipo": "Técnico", "descricao": "Riscos de engenharia e execução"},
            {"tipo": "Regulatório", "descricao": "Riscos de aprovações e normativas"},
            {"tipo": "Social", "descricao": "Riscos relacionados a comunidades e stakeholders"},
            {"tipo": "Climático", "descricao": "Riscos de condições meteorológicas adversas"},
            {"tipo": "Geotécnico", "descricao": "Riscos de condições do solo e subsolo"},
            {"tipo": "Logístico", "descricao": "Riscos de suprimentos e logística"},
            {"tipo": "Contratual", "descricao": "Riscos de contratos e fornecedores"},
            {"tipo": "Operacional", "descricao": "Riscos de operação e manutenção"}
        ]
        
        for risco_data in riscos:
            existente = db.query(Risco).filter(
                Risco.tipo == risco_data["tipo"]
            ).first()
            
            if not existente:
                risco = Risco(**risco_data)
                db.add(risco)
                print(f"  Risco criado: {risco_data['tipo']}")
        
        db.commit()
        print("\nDados basicos inicializados com sucesso!")
        
        # Resumo
        total_zonas = db.query(ZonaPortuaria).count()
        total_tipos = db.query(TipoServico).count()
        total_riscos = db.query(Risco).count()
        
        print(f"\nResumo:")
        print(f"   Zonas Portuarias: {total_zonas}")
        print(f"   Tipos de Servico: {total_tipos}")
        print(f"   Riscos: {total_riscos}")
        
    except Exception as e:
        print(f"Erro ao inicializar dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    inicializar_dados()
