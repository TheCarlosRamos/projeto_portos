from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    zona_portuaria = Column(String, nullable=False)
    uf = Column(String)
    obj_concessao = Column(String, nullable=False)
    tipo = Column(String)  # Concessão, Arrendamento, Autorização
    capex_total = Column(Float)
    capex_executado = Column(Float)
    perc_capex_executado = Column(Float)
    data_assinatura = Column(Date)
    descricao = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relacionamentos
    services = relationship("Service", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Converte o projeto para o formato esperado pelo frontend"""
        return {
            "id": self.id,
            "name": self.zona_portuaria,
            "description": self.obj_concessao,
            "full_description": self.descricao,
            "project_type": self.tipo,
            "investment": self.capex_total,
            "contract_date": self.data_assinatura.isoformat() if self.data_assinatura else None,
            "ufs": self.uf,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capex_executado": self.capex_executado,
            "perc_capex_executado": self.perc_capex_executado,
            "total_services": len(self.services) if self.services else 0,
            "progress_percentage": self.perc_capex_executado or 0,
            "status": self._get_status()
        }
    
    def _get_status(self):
        """Determina o status do projeto baseado no progresso"""
        if not self.perc_capex_executado:
            return "Planejamento"
        elif self.perc_capex_executado >= 0.9:
            return "Concluído"
        else:
            return "Em Andamento"


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tipo_servico = Column(String)  # CMO, Disponibilidade de Infraestrutura
    fase = Column(String)  # 1ª, 2ª, 3ª
    servico = Column(String, nullable=False)
    descricao_servico = Column(Text)
    prazo_inicio_anos = Column(Integer)
    data_inicio = Column(Date)
    prazo_final_anos = Column(Float)
    data_final = Column(Date)
    fonte_prazo = Column(String)
    perc_capex = Column(Float)
    capex_servico_total = Column(Float)
    capex_servico_exec = Column(Float)
    perc_capex_exec = Column(Float)
    fonte_perc_capex = Column(String)
    
    # Relacionamentos
    project = relationship("Project", back_populates="services")
    monitoring = relationship("Monitoring", back_populates="service", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Converte o serviço para o formato esperado pelo frontend"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "tipo_servico": self.tipo_servico,
            "fase": self.fase,
            "servico": self.servico,
            "descricao_servico": self.descricao_servico,
            "prazo_inicio_anos": self.prazo_inicio_anos,
            "data_inicio": self.data_inicio.isoformat() if self.data_inicio else None,
            "prazo_final_anos": self.prazo_final_anos,
            "data_final": self.data_final.isoformat() if self.data_final else None,
            "fonte_prazo": self.fonte_prazo,
            "perc_capex": self.perc_capex,
            "capex_servico_total": self.capex_servico_total,
            "capex_servico_exec": self.capex_servico_exec,
            "perc_capex_exec": self.perc_capex_exec,
            "fonte_perc_capex": self.fonte_perc_capex
        }


class Monitoring(Base):
    __tablename__ = "monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    descricao = Column(Text)
    perc_executada = Column(Float)
    valor_executado = Column(Float)
    data_atualizacao = Column(Date)
    responsavel = Column(String)
    cargo = Column(String)
    setor = Column(String)
    risco_tipo = Column(String)  # Meio Ambiente, Financeiro, etc
    risco_descricao = Column(Text)
    
    # Relacionamentos
    service = relationship("Service", back_populates="monitoring")
    
    def to_dict(self):
        """Converte o acompanhamento para o formato esperado pelo frontend"""
        return {
            "id": self.id,
            "service_id": self.service_id,
            "descricao": self.descricao,
            "perc_executada": self.perc_executada,
            "valor_executado": self.valor_executado,
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            "responsavel": self.responsavel,
            "cargo": self.cargo,
            "setor": self.setor,
            "risco_tipo": self.risco_tipo,
            "risco_descricao": self.risco_descricao
        }
