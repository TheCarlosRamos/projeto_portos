from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Situacao
from schemas import Situacao as SituacaoSchema, SituacaoCreate

router = APIRouter()

@router.get("/", response_model=List[SituacaoSchema])
def listar_situacoes(db: Session = Depends(get_db)):
    """Lista todas as situações"""
    situacoes = db.query(Situacao).all()
    return situacoes

@router.get("/{situacao_id}", response_model=SituacaoSchema)
def obter_situacao(situacao_id: int, db: Session = Depends(get_db)):
    """Obtém uma situação específica por ID"""
    situacao = db.query(Situacao).filter(Situacao.id == situacao_id).first()
    if not situacao:
        raise HTTPException(status_code=404, detail="Situação não encontrada")
    return situacao

@router.post("/", response_model=SituacaoSchema, status_code=201)
def criar_situacao(situacao: SituacaoCreate, db: Session = Depends(get_db)):
    """Cria uma nova situação"""
    # Verificar se já existe
    existente = db.query(Situacao).filter(
        Situacao.nome == situacao.nome
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma situação com este nome"
        )
    
    nova_situacao = Situacao(**situacao.model_dump())
    db.add(nova_situacao)
    db.commit()
    db.refresh(nova_situacao)
    return nova_situacao

@router.delete("/{situacao_id}", status_code=204)
def deletar_situacao(situacao_id: int, db: Session = Depends(get_db)):
    """Deleta uma situação (apenas se não estiver em uso)"""
    situacao = db.query(Situacao).filter(Situacao.id == situacao_id).first()
    if not situacao:
        raise HTTPException(status_code=404, detail="Situação não encontrada")
    
    # Verificar se está em uso
    if situacao.processos:
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar situação em uso por processos"
        )
    
    db.delete(situacao)
    db.commit()
    return None
