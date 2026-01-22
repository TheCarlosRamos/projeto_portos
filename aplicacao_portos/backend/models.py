from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Situacao(Base):
    __tablename__ = "situacao"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    processos = relationship("Processo", back_populates="situacao")

class Processo(Base):
    __tablename__ = "processo"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_processo = Column(String(50), unique=True, nullable=False, index=True)
    data_protocolo = Column(Date)
    licenca = Column(String(100))
    situacao_geral_id = Column(Integer, ForeignKey("situacao.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    situacao = relationship("Situacao", back_populates="processos")
    metas = relationship("Meta", back_populates="processo", cascade="all, delete-orphan")

class Meta(Base):
    __tablename__ = "meta"
    
    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processo.id"), nullable=False, index=True)
    ano = Column(Integer, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    processo = relationship("Processo", back_populates="metas")
    indicadores = relationship("Indicador", back_populates="meta", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"postgresql_partition_by": "RANGE (ano)"} if False else {},
    )  # Opcional: particionamento por ano

class Indicador(Base):
    __tablename__ = "indicador"
    
    id = Column(Integer, primary_key=True, index=True)
    meta_id = Column(Integer, ForeignKey("meta.id"), nullable=False, index=True)
    tipo_intervencao = Column(String(50), nullable=False, index=True)
    financeiro_planejado = Column(Numeric(15, 2), default=0)
    financeiro_executado = Column(Numeric(15, 2), default=0)
    km_planejado = Column(Numeric(10, 2), default=0)
    km_executado = Column(Numeric(10, 2), default=0)
    extensao_km = Column(Numeric(10, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    meta = relationship("Meta", back_populates="indicadores")
