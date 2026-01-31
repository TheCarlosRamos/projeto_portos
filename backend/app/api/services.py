from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/api/servicos", tags=["services"])

@router.get("/", response_model=List[dict])
def get_all_services(project_id: int = None, db: Session = Depends(get_db)):
    """Retorna todos os serviços, opcionalmente filtrados por projeto"""
    query = db.query(Service)
    if project_id:
        query = query.filter(Service.project_id == project_id)
    services = query.all()
    return [service.to_dict() for service in services]

@router.get("/{service_id}", response_model=dict)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Retorna um serviço específico com acompanhamentos"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    service_dict = service.to_dict()
    service_dict["monitoring"] = [mon.to_dict() for mon in service.monitoring]
    return service_dict

@router.post("/", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """Cria um novo serviço"""
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service: ServiceUpdate, db: Session = Depends(get_db)):
    """Atualiza um serviço existente"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    update_data = service.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Deleta um serviço"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    db.delete(db_service)
    db.commit()
    return {"message": "Serviço deletado com sucesso"}
