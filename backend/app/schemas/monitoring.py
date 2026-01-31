from pydantic import BaseModel
from typing import Optional
from datetime import date

class MonitoringBase(BaseModel):
    service_id: int
    descricao: Optional[str] = None
    perc_executada: Optional[float] = None
    valor_executado: Optional[float] = None
    data_atualizacao: Optional[date] = None
    responsavel: Optional[str] = None
    cargo: Optional[str] = None
    setor: Optional[str] = None
    risco_tipo: Optional[str] = None
    risco_descricao: Optional[str] = None

class MonitoringCreate(MonitoringBase):
    pass

class MonitoringUpdate(MonitoringBase):
    service_id: Optional[int] = None

class MonitoringResponse(MonitoringBase):
    id: int
    
    class Config:
        from_attributes = True
