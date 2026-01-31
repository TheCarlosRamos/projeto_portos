from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Monitoring
from app.schemas.monitoring import MonitoringCreate, MonitoringUpdate, MonitoringResponse

router = APIRouter(prefix="/api/acompanhamento", tags=["monitoring"])

@router.get("/", response_model=List[dict])
def get_all_monitoring(service_id: int = None, db: Session = Depends(get_db)):
    """Retorna todos os acompanhamentos, opcionalmente filtrados por serviço"""
    query = db.query(Monitoring)
    if service_id:
        query = query.filter(Monitoring.service_id == service_id)
    monitoring = query.all()
    return [mon.to_dict() for mon in monitoring]

@router.get("/{monitoring_id}", response_model=dict)
def get_monitoring(monitoring_id: int, db: Session = Depends(get_db)):
    """Retorna um acompanhamento específico"""
    monitoring = db.query(Monitoring).filter(Monitoring.id == monitoring_id).first()
    if not monitoring:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    return monitoring.to_dict()

@router.post("/", response_model=MonitoringResponse)
def create_monitoring(monitoring: MonitoringCreate, db: Session = Depends(get_db)):
    """Cria um novo acompanhamento"""
    db_monitoring = Monitoring(**monitoring.model_dump())
    db.add(db_monitoring)
    db.commit()
    db.refresh(db_monitoring)
    return db_monitoring

@router.put("/{monitoring_id}", response_model=MonitoringResponse)
def update_monitoring(monitoring_id: int, monitoring: MonitoringUpdate, db: Session = Depends(get_db)):
    """Atualiza um acompanhamento existente"""
    db_monitoring = db.query(Monitoring).filter(Monitoring.id == monitoring_id).first()
    if not db_monitoring:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    
    update_data = monitoring.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_monitoring, field, value)
    
    db.commit()
    db.refresh(db_monitoring)
    return db_monitoring

@router.delete("/{monitoring_id}")
def delete_monitoring(monitoring_id: int, db: Session = Depends(get_db)):
    """Deleta um acompanhamento"""
    db_monitoring = db.query(Monitoring).filter(Monitoring.id == monitoring_id).first()
    if not db_monitoring:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    
    db.delete(db_monitoring)
    db.commit()
    return {"message": "Acompanhamento deletado com sucesso"}
