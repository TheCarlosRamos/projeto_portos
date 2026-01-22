from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Meta, Processo
from schemas import Meta as MetaSchema, MetaCreate, MetaUpdate

router = APIRouter()

@router.get("/", response_model=List[MetaSchema])
def listar_metas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ano: Optional[int] = None,
    processo_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as metas com filtros opcionais"""
    query = db.query(Meta)
    
    if ano:
        query = query.filter(Meta.ano == ano)
    
    if processo_id:
        query = query.filter(Meta.processo_id == processo_id)
    
    metas = query.offset(skip).limit(limit).all()
    return metas

@router.get("/{meta_id}", response_model=MetaSchema)
def obter_meta(meta_id: int, db: Session = Depends(get_db)):
    """Obtém uma meta específica por ID"""
    meta = db.query(Meta).filter(Meta.id == meta_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return meta

@router.post("/", response_model=MetaSchema, status_code=201)
def criar_meta(meta: MetaCreate, db: Session = Depends(get_db)):
    """Cria uma nova meta"""
    # Verificar se o processo existe
    processo = db.query(Processo).filter(Processo.id == meta.processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Validar se já existe meta para este processo no mesmo ano
    meta_existente = db.query(Meta).filter(
        Meta.processo_id == meta.processo_id,
        Meta.ano == meta.ano
    ).first()
    
    if meta_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma meta para este processo no ano {meta.ano}"
        )
    
    nova_meta = Meta(**meta.model_dump())
    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)
    return nova_meta

@router.put("/{meta_id}", response_model=MetaSchema)
def atualizar_meta(
    meta_id: int,
    meta: MetaUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma meta existente"""
    meta_db = db.query(Meta).filter(Meta.id == meta_id).first()
    if not meta_db:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    # Validar ano único se for alterado
    if meta.ano and meta.ano != meta_db.ano:
        meta_existente = db.query(Meta).filter(
            Meta.processo_id == meta_db.processo_id,
            Meta.ano == meta.ano,
            Meta.id != meta_id
        ).first()
        if meta_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma meta para este processo no ano {meta.ano}"
            )
    
    # Atualizar campos
    update_data = meta.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meta_db, field, value)
    
    db.commit()
    db.refresh(meta_db)
    return meta_db

@router.delete("/{meta_id}", status_code=204)
def deletar_meta(meta_id: int, db: Session = Depends(get_db)):
    """Deleta uma meta (cascata para indicadores)"""
    meta = db.query(Meta).filter(Meta.id == meta_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    db.delete(meta)
    db.commit()
    return None
