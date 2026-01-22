from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from database import get_db
from models import Processo, Situacao
from schemas import Processo as ProcessoSchema, ProcessoCreate, ProcessoUpdate

router = APIRouter()

@router.get("/", response_model=List[ProcessoSchema])
def listar_processos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    numero_processo: Optional[str] = None,
    situacao_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os processos com filtros opcionais"""
    query = db.query(Processo)
    
    if numero_processo:
        query = query.filter(Processo.numero_processo.ilike(f"%{numero_processo}%"))
    
    if situacao_id:
        query = query.filter(Processo.situacao_geral_id == situacao_id)
    
    processos = query.offset(skip).limit(limit).all()
    return processos

@router.get("/{processo_id}", response_model=ProcessoSchema)
def obter_processo(processo_id: int, db: Session = Depends(get_db)):
    """Obtém um processo específico por ID"""
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return processo

@router.post("/", response_model=ProcessoSchema, status_code=201)
def criar_processo(processo: ProcessoCreate, db: Session = Depends(get_db)):
    """Cria um novo processo"""
    # Verificar se já existe processo com o mesmo número
    existente = db.query(Processo).filter(
        Processo.numero_processo == processo.numero_processo
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um processo com este número"
        )
    
    # Validar situação se informada
    if processo.situacao_geral_id:
        situacao = db.query(Situacao).filter(
            Situacao.id == processo.situacao_geral_id
        ).first()
        if not situacao:
            raise HTTPException(status_code=400, detail="Situação não encontrada")
    
    novo_processo = Processo(**processo.model_dump())
    db.add(novo_processo)
    db.commit()
    db.refresh(novo_processo)
    return novo_processo

@router.put("/{processo_id}", response_model=ProcessoSchema)
def atualizar_processo(
    processo_id: int,
    processo: ProcessoUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um processo existente"""
    processo_db = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo_db:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Validar número único se for alterado
    if processo.numero_processo and processo.numero_processo != processo_db.numero_processo:
        existente = db.query(Processo).filter(
            Processo.numero_processo == processo.numero_processo,
            Processo.id != processo_id
        ).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail="Já existe outro processo com este número"
            )
    
    # Validar situação se informada
    if processo.situacao_geral_id:
        situacao = db.query(Situacao).filter(
            Situacao.id == processo.situacao_geral_id
        ).first()
        if not situacao:
            raise HTTPException(status_code=400, detail="Situação não encontrada")
    
    # Atualizar campos
    update_data = processo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(processo_db, field, value)
    
    db.commit()
    db.refresh(processo_db)
    return processo_db

@router.delete("/{processo_id}", status_code=204)
def deletar_processo(processo_id: int, db: Session = Depends(get_db)):
    """Deleta um processo (cascata para metas e indicadores)"""
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    db.delete(processo)
    db.commit()
    return None
