from pydantic import BaseModel
from typing import Optional
from datetime import date

class ServiceBase(BaseModel):
    project_id: int
    tipo_servico: Optional[str] = None
    fase: Optional[str] = None
    servico: str
    descricao_servico: Optional[str] = None
    prazo_inicio_anos: Optional[int] = None
    data_inicio: Optional[date] = None
    prazo_final_anos: Optional[float] = None
    data_final: Optional[date] = None
    fonte_prazo: Optional[str] = None
    perc_capex: Optional[float] = None
    capex_servico_total: Optional[float] = None
    capex_servico_exec: Optional[float] = None
    perc_capex_exec: Optional[float] = None
    fonte_perc_capex: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    project_id: Optional[int] = None
    servico: Optional[str] = None

class ServiceResponse(ServiceBase):
    id: int
    
    class Config:
        from_attributes = True
