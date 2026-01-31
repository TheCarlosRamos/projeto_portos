from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Project, Service, Monitoring
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/", response_model=List[dict])
def get_all_projects(db: Session = Depends(get_db)):
    """Retorna todos os projetos com informações agregadas"""
    projects = db.query(Project).all()
    return [project.to_dict() for project in projects]

@router.get("/{project_id}", response_model=dict)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Retorna um projeto específico com todos os detalhes"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Incluir serviços e acompanhamentos
    project_dict = project.to_dict()
    project_dict["services"] = [service.to_dict() for service in project.services]
    
    # Adicionar acompanhamentos de cada serviço
    for service_dict in project_dict["services"]:
        service = db.query(Service).filter(Service.id == service_dict["id"]).first()
        service_dict["monitoring"] = [mon.to_dict() for mon in service.monitoring]
    
    return project_dict

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Cria um novo projeto"""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """Atualiza um projeto existente"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Atualizar apenas campos fornecidos
    update_data = project.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Deleta um projeto"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Projeto deletado com sucesso"}
