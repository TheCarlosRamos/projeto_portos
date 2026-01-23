from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, TIMESTAMP, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Tabelas de Domínio
class ZonaPortuaria(Base):
    __tablename__ = "zona_portuaria"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    uf = Column(String(2), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relacionamentos
    concessoes = relationship("Concessao", back_populates="zona_portuaria")

class TipoServico(Base):
    __tablename__ = "tipo_servico"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relacionamentos
    servicos = relationship("Servico", back_populates="tipo_servico")

class Risco(Base):
    __tablename__ = "risco"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    descricao = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relacionamentos
    acompanhamentos = relationship("Acompanhamento", secondary="acompanhamento_risco", back_populates="riscos")

# Tabela Principal
class Concessao(Base):
    __tablename__ = "concessao"
    
    id = Column(Integer, primary_key=True, index=True)
    zona_portuaria_id = Column(Integer, ForeignKey("zona_portuaria.id"), nullable=False, index=True)
    objeto_concessao = Column(String(200), nullable=False, index=True)
    tipo = Column(String(50), nullable=False)  # FIXO: Concessão, Arrendamento, Autorização
    capex_total = Column(Numeric(15, 2), nullable=False)
    data_assinatura = Column(Date)
    descricao = Column(Text)
    coord_e = Column(Numeric(10, 2))
    coord_s = Column(Numeric(10, 2))
    fuso = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    zona_portuaria = relationship("ZonaPortuaria", back_populates="concessoes")
    servicos = relationship("Servico", back_populates="concessao", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('capex_total > 0', name='capex_total_positivo'),
        CheckConstraint('tipo IN ("Concessão", "Arrendamento", "Autorização")', name='tipo_valido'),
    )

class Servico(Base):
    __tablename__ = "servico"
    
    id = Column(Integer, primary_key=True, index=True)
    concessao_id = Column(Integer, ForeignKey("concessao.id"), nullable=False, index=True)
    tipo_servico_id = Column(Integer, ForeignKey("tipo_servico.id"), nullable=False, index=True)
    fase = Column(String(10), nullable=False)  # 1ª, 2ª, 3ª, etc.
    nome = Column(String(200), nullable=False)  # Nome do serviço
    descricao = Column(Text)
    prazo_inicio_anos = Column(Integer)
    data_inicio = Column(Date)
    prazo_final_anos = Column(Integer)
    data_final = Column(Date)
    fonte_prazo = Column(String(100))
    percentual_capex = Column(Numeric(5, 2), nullable=False)  # % de CAPEX para o serviço
    capex_servico = Column(Numeric(15, 2), nullable=False)  # CAPEX do Serviço
    fonte_percentual = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    concessao = relationship("Concessao", back_populates="servicos")
    tipo_servico = relationship("TipoServico", back_populates="servicos")
    acompanhamentos = relationship("Acompanhamento", back_populates="servico", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('percentual_capex >= 0 AND percentual_capex <= 100', name='percentual_capex_range'),
        CheckConstraint('capex_servico >= 0', name='capex_servico_positivo'),
    )

class Acompanhamento(Base):
    __tablename__ = "acompanhamento"
    
    id = Column(Integer, primary_key=True, index=True)
    servico_id = Column(Integer, ForeignKey("servico.id"), nullable=False, index=True)
    percentual_executado = Column(Numeric(5, 2), nullable=False)
    capex_reajustado = Column(Numeric(15, 2), nullable=False)
    valor_executado = Column(Numeric(15, 2), nullable=False)
    data_atualizacao = Column(Date, nullable=False)
    responsavel = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    setor = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relacionamentos
    servico = relationship("Servico", back_populates="acompanhamentos")
    riscos = relationship("Risco", secondary="acompanhamento_risco", back_populates="acompanhamentos")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('percentual_executado >= 0 AND percentual_executado <= 100', name='percentual_executado_range'),
        CheckConstraint('valor_executado >= 0', name='valor_executado_positivo'),
        CheckConstraint('capex_reajustado >= 0', name='capex_reajustado_positivo'),
    )

# Tabela Associativa
class AcompanhamentoRisco(Base):
    __tablename__ = "acompanhamento_risco"
    
    acompanhamento_id = Column(Integer, ForeignKey("acompanhamento.id"), primary_key=True)
    risco_id = Column(Integer, ForeignKey("risco.id"), primary_key=True)
    
    # Relacionamentos
    acompanhamento = relationship("Acompanhamento")
    risco = relationship("Risco")
