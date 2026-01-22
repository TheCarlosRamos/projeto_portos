from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import List, Optional

# Situação
class SituacaoBase(BaseModel):
    nome: str

class SituacaoCreate(SituacaoBase):
    pass

class Situacao(SituacaoBase):
    id: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# Indicador
class IndicadorBase(BaseModel):
    tipo_intervencao: str
    financeiro_planejado: Decimal = Field(default=0, ge=0)
    financeiro_executado: Decimal = Field(default=0, ge=0)
    km_planejado: Decimal = Field(default=0, ge=0)
    km_executado: Decimal = Field(default=0, ge=0)
    extensao_km: Decimal = Field(default=0, ge=0)

class IndicadorCreate(IndicadorBase):
    meta_id: int

class IndicadorUpdate(IndicadorBase):
    pass

class Indicador(IndicadorBase):
    id: int
    meta_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# Meta
class MetaBase(BaseModel):
    ano: int = Field(..., ge=2020, le=2100)

class MetaCreate(MetaBase):
    processo_id: int

class MetaUpdate(MetaBase):
    pass

class Meta(MetaBase):
    id: int
    processo_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    indicadores: List[Indicador] = []
    
    class Config:
        from_attributes = True

# Processo
class ProcessoBase(BaseModel):
    numero_processo: str
    data_protocolo: Optional[date] = None
    licenca: Optional[str] = None
    situacao_geral_id: Optional[int] = None

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoUpdate(ProcessoBase):
    numero_processo: Optional[str] = None

class Processo(ProcessoBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    situacao: Optional[Situacao] = None
    metas: List[Meta] = []
    
    class Config:
        from_attributes = True
