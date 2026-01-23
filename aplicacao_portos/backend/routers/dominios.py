from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models_portuarios import ZonaPortuaria, TipoServico, Risco
from schemas_portuarios import (
    ZonaPortuaria as ZonaPortuariaSchema, 
    ZonaPortuariaCreate as ZonaPortuariaCreateSchema,
    TipoServico as TipoServicoSchema,
    TipoServicoCreate as TipoServicoCreateSchema,
    Risco as RiscoSchema,
    RiscoCreate as RiscoCreateSchema
)

router = APIRouter()

# Zonas Portuárias
@router.get("/zonas-portuarias/", response_model=List[ZonaPortuariaSchema])
def listar_zonas_portuarias(db: Session = Depends(get_db)):
    """Lista todas as zonas portuárias"""
    return db.query(ZonaPortuaria).order_by(ZonaPortuaria.nome).all()

@router.post("/zonas-portuarias/", response_model=ZonaPortuariaSchema)
def criar_zona_portuaria(zona: ZonaPortuariaCreateSchema, db: Session = Depends(get_db)):
    """Cria uma nova zona portuária"""
    # Verificar duplicação
    existente = db.query(ZonaPortuaria).filter(
        ZonaPortuaria.nome == zona.nome
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Zona portuária já existe")
    
    db_zona = ZonaPortuaria(**zona.dict())
    db.add(db_zona)
    db.commit()
    db.refresh(db_zona)
    return db_zona

@router.get("/zonas-portuarias/{zona_id}", response_model=ZonaPortuariaSchema)
def obter_zona_portuaria(zona_id: int, db: Session = Depends(get_db)):
    """Obtém uma zona portuária específica"""
    zona = db.query(ZonaPortuaria).filter(ZonaPortuaria.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona portuária não encontrada")
    return zona

# Tipos de Serviço
@router.get("/tipos-servico/", response_model=List[TipoServicoSchema])
def listar_tipos_servico(db: Session = Depends(get_db)):
    """Lista todos os tipos de serviço"""
    return db.query(TipoServico).order_by(TipoServico.nome).all()

@router.post("/tipos-servico/", response_model=TipoServicoSchema)
def criar_tipo_servico(tipo: TipoServicoCreateSchema, db: Session = Depends(get_db)):
    """Cria um novo tipo de serviço"""
    # Verificar duplicação
    existente = db.query(TipoServico).filter(
        TipoServico.nome == tipo.nome
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Tipo de serviço já existe")
    
    db_tipo = TipoServico(**tipo.dict())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

# Riscos
@router.get("/riscos/", response_model=List[RiscoSchema])
def listar_riscos(db: Session = Depends(get_db)):
    """Lista todos os riscos"""
    return db.query(Risco).order_by(Risco.tipo).all()

@router.post("/riscos/", response_model=RiscoSchema)
def criar_risco(risco: RiscoCreateSchema, db: Session = Depends(get_db)):
    """Cria um novo risco"""
    # Verificar duplicação
    existente = db.query(Risco).filter(
        Risco.tipo == risco.tipo
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Tipo de risco já existe")
    
    db_risco = Risco(**risco.dict())
    db.add(db_risco)
    db.commit()
    db.refresh(db_risco)
    return db_risco

@router.get("/riscos/{risco_id}", response_model=RiscoSchema)
def obter_risco(risco_id: int, db: Session = Depends(get_db)):
    """Obtém um risco específico"""
    risco = db.query(Risco).filter(Risco.id == risco_id).first()
    if not risco:
        raise HTTPException(status_code=404, detail="Risco não encontrado")
    return risco
