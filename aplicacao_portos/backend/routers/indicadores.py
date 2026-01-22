from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Indicador, Meta
from schemas import Indicador as IndicadorSchema, IndicadorCreate, IndicadorUpdate

router = APIRouter()

@router.get("/", response_model=List[IndicadorSchema])
def listar_indicadores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    meta_id: Optional[int] = None,
    tipo_intervencao: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os indicadores com filtros opcionais"""
    query = db.query(Indicador)
    
    if meta_id:
        query = query.filter(Indicador.meta_id == meta_id)
    
    if tipo_intervencao:
        query = query.filter(Indicador.tipo_intervencao.ilike(f"%{tipo_intervencao}%"))
    
    indicadores = query.offset(skip).limit(limit).all()
    return indicadores

@router.get("/{indicador_id}", response_model=IndicadorSchema)
def obter_indicador(indicador_id: int, db: Session = Depends(get_db)):
    """Obtém um indicador específico por ID"""
    indicador = db.query(Indicador).filter(Indicador.id == indicador_id).first()
    if not indicador:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")
    return indicador

@router.post("/", response_model=IndicadorSchema, status_code=201)
def criar_indicador(indicador: IndicadorCreate, db: Session = Depends(get_db)):
    """Cria um novo indicador"""
    # Verificar se a meta existe
    meta = db.query(Meta).filter(Meta.id == indicador.meta_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    novo_indicador = Indicador(**indicador.model_dump())
    db.add(novo_indicador)
    db.commit()
    db.refresh(novo_indicador)
    return novo_indicador

@router.put("/{indicador_id}", response_model=IndicadorSchema)
def atualizar_indicador(
    indicador_id: int,
    indicador: IndicadorUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um indicador existente"""
    indicador_db = db.query(Indicador).filter(Indicador.id == indicador_id).first()
    if not indicador_db:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")
    
    # Atualizar campos
    update_data = indicador.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(indicador_db, field, value)
    
    db.commit()
    db.refresh(indicador_db)
    return indicador_db

@router.delete("/{indicador_id}", status_code=204)
def deletar_indicador(indicador_id: int, db: Session = Depends(get_db)):
    """Deleta um indicador"""
    indicador = db.query(Indicador).filter(Indicador.id == indicador_id).first()
    if not indicador:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")
    
    db.delete(indicador)
    db.commit()
    return None
