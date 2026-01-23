from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Schemas para Domínios
class ZonaPortuariaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    uf: str = Field(..., min_length=2, max_length=2)

class ZonaPortuariaCreate(ZonaPortuariaBase):
    pass

class ZonaPortuaria(ZonaPortuariaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TipoServicoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)

class TipoServicoCreate(TipoServicoBase):
    pass

class TipoServico(TipoServicoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RiscoBase(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=50)
    descricao: Optional[str] = None

class RiscoCreate(RiscoBase):
    pass

class Risco(RiscoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para Concessão
class ConcessaoBase(BaseModel):
    zona_portuaria_id: int
    objeto_concessao: str = Field(..., min_length=1, max_length=200)
    tipo: str = Field(..., min_length=1, max_length=50)
    capex_total: Decimal = Field(..., gt=0)
    data_assinatura: Optional[date] = None
    descricao: Optional[str] = None
    coord_e: Optional[Decimal] = Field(None, ge=0)
    coord_s: Optional[Decimal] = Field(None, ge=0)
    fuso: Optional[int] = None

    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        if v not in ['Concessão', 'Arrendamento', 'Autorização']:
            raise ValueError('Tipo deve ser: Concessão, Arrendamento ou Autorização')
        return v

class ConcessaoCreate(ConcessaoBase):
    pass

class Concessao(ConcessaoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    zona_portuaria: ZonaPortuaria
    
    class Config:
        from_attributes = True

# Schemas para Serviço
class ServicoBase(BaseModel):
    concessao_id: int
    tipo_servico_id: int
    fase: str = Field(..., min_length=1, max_length=10)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    prazo_inicio_anos: Optional[int] = Field(None, ge=0)
    data_inicio: Optional[date] = None
    prazo_final_anos: Optional[int] = Field(None, ge=0)
    data_final: Optional[date] = None
    fonte_prazo: Optional[str] = Field(None, max_length=100)
    percentual_capex: Decimal = Field(..., ge=0, le=100)
    capex_servico: Decimal = Field(..., ge=0)
    fonte_percentual: Optional[str] = Field(None, max_length=100)

    @field_validator('data_final')
    @classmethod
    def validate_datas(cls, v, info):
        if v and 'data_inicio' in info.data and info.data['data_inicio']:
            if v <= info.data['data_inicio']:
                raise ValueError('Data final deve ser posterior à data inicial')
        return v

class ServicoCreate(ServicoBase):
    pass

class Servico(ServicoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    concessao: Concessao
    tipo_servico: TipoServico
    
    class Config:
        from_attributes = True

# Schemas para Acompanhamento
class AcompanhamentoBase(BaseModel):
    servico_id: int
    percentual_executado: Decimal = Field(..., ge=0, le=100)
    capex_reajustado: Decimal = Field(..., ge=0)
    valor_executado: Decimal = Field(..., ge=0)
    data_atualizacao: date
    responsavel: str = Field(..., min_length=1, max_length=100)
    cargo: str = Field(..., min_length=1, max_length=100)
    setor: str = Field(..., min_length=1, max_length=100)

    @field_validator('valor_executado')
    @classmethod
    def validate_valor_executado(cls, v, info):
        if 'capex_reajustado' in info.data:
            if v > info.data['capex_reajustado']:
                raise ValueError('Valor executado não pode ultrapassar CAPEX reajustado')
        return v

class AcompanhamentoCreate(AcompanhamentoBase):
    risco_ids: Optional[List[int]] = []

class Acompanhamento(AcompanhamentoBase):
    id: int
    created_at: datetime
    servico: Servico
    riscos: List[Risco] = []
    
    class Config:
        from_attributes = True

# Schemas para relatórios e consultas
class ConcessaoComServicos(Concessao):
    servicos: List[Servico] = []

class ServicoComAcompanhamentos(Servico):
    acompanhamentos: List[Acompanhamento] = []

# Schemas para filtros
class ConcessaoFilter(BaseModel):
    zona_portuaria_id: Optional[int] = None
    uf: Optional[str] = None
    tipo: Optional[str] = None

class ServicoFilter(BaseModel):
    concessao_id: Optional[int] = None
    tipo_servico_id: Optional[int] = None
    fase: Optional[str] = None

class AcompanhamentoFilter(BaseModel):
    servico_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
