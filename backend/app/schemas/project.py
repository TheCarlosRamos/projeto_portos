from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProjectBase(BaseModel):
    zona_portuaria: str
    uf: Optional[str] = None
    obj_concessao: str
    tipo: Optional[str] = None
    capex_total: Optional[float] = None
    capex_executado: Optional[float] = None
    perc_capex_executado: Optional[float] = None
    data_assinatura: Optional[date] = None
    descricao: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    zona_portuaria: Optional[str] = None
    obj_concessao: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    
    class Config:
        from_attributes = True
