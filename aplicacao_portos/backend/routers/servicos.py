from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database import get_db
from models_portuarios import Servico, Concessao, TipoServico, Acompanhamento
from schemas_portuarios import Servico as ServicoSchema, ServicoCreate as ServicoCreateSchema, ServicoFilter, ServicoComAcompanhamentos

router = APIRouter()

@router.get("/", response_model=List[ServicoSchema])
def listar_servicos(
    concessao_id: Optional[int] = Query(None),
    tipo_servico_id: Optional[int] = Query(None),
    fase: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista todos os serviços com filtros opcionais"""
    query = db.query(Servico).join(Concessao).join(TipoServico)
    
    if concessao_id:
        query = query.filter(Servico.concessao_id == concessao_id)
    if tipo_servico_id:
        query = query.filter(Servico.tipo_servico_id == tipo_servico_id)
    if fase:
        query = query.filter(Servico.fase == fase)
    
    servicos = query.offset(skip).limit(limit).all()
    return servicos

@router.get("/{servico_id}", response_model=ServicoComAcompanhamentos)
def obter_servico(servico_id: int, db: Session = Depends(get_db)):
    """Obtém um serviço específico com seus acompanhamentos"""
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return servico

@router.post("/", response_model=ServicoSchema)
def criar_servico(servico: ServicoCreateSchema, db: Session = Depends(get_db)):
    """Cria um novo serviço"""
    # Verificar se concessão existe
    concessao = db.query(Concessao).filter(Concessao.id == servico.concessao_id).first()
    if not concessao:
        raise HTTPException(status_code=400, detail="Concessão não encontrada")
    
    # Verificar se tipo de serviço existe
    tipo_servico = db.query(TipoServico).filter(TipoServico.id == servico.tipo_servico_id).first()
    if not tipo_servico:
        raise HTTPException(status_code=400, detail="Tipo de serviço não encontrado")
    
    # Verificar soma dos percentuais de CAPEX por concessão
    soma_percentuais = db.query(func.sum(Servico.percentual_capex)).filter(
        Servico.concessao_id == servico.concessao_id
    ).scalar() or 0
    
    if soma_percentuais + float(servico.percentual_capex) > 100:
        raise HTTPException(
            status_code=400, 
            detail=f"Soma dos percentuais de CAPEX ultrapassaria 100%. Atual: {soma_percentuais}%, Novo: {servico.percentual_capex}%"
        )
    
    db_servico = Servico(**servico.dict())
    db.add(db_servico)
    db.commit()
    db.refresh(db_servico)
    return db_servico

@router.put("/{servico_id}", response_model=ServicoSchema)
def atualizar_servico(
    servico_id: int, 
    servico: ServicoCreateSchema, 
    db: Session = Depends(get_db)
):
    """Atualiza um serviço existente"""
    db_servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not db_servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    # Verificar se concessão existe
    concessao = db.query(Concessao).filter(Concessao.id == servico.concessao_id).first()
    if not concessao:
        raise HTTPException(status_code=400, detail="Concessão não encontrada")
    
    # Verificar soma dos percentuais de CAPEX por concessão (excluindo o próprio)
    soma_percentuais = db.query(func.sum(Servico.percentual_capex)).filter(
        Servico.concessao_id == servico.concessao_id,
        Servico.id != servico_id
    ).scalar() or 0
    
    if soma_percentuais + float(servico.percentual_capex) > 100:
        raise HTTPException(
            status_code=400, 
            detail=f"Soma dos percentuais de CAPEX ultrapassaria 100%. Atual: {soma_percentuais}%, Novo: {servico.percentual_capex}%"
        )
    
    for key, value in servico.dict().items():
        setattr(db_servico, key, value)
    
    db.commit()
    db.refresh(db_servico)
    return db_servico

@router.delete("/{servico_id}")
def deletar_servico(servico_id: int, db: Session = Depends(get_db)):
    """Remove um serviço"""
    db_servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not db_servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    db.delete(db_servico)
    db.commit()
    return {"message": "Serviço removido com sucesso"}

@router.get("/{servico_id}/status-execucao")
def status_execucao_servico(servico_id: int, db: Session = Depends(get_db)):
    """Status detalhado de execução do serviço"""
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    acompanhamentos = db.query(Acompanhamento).filter(
        Acompanhamento.servico_id == servico_id
    ).order_by(Acompanhamento.data_atualizacao.desc()).all()
    
    if not acompanhamentos:
        return {
            "servico_id": servico_id,
            "percentual_executado": 0,
            "valor_executado": 0,
            "capex_reajustado": servico.capex_servico,
            "total_acompanhamentos": 0,
            "ultima_atualizacao": None
        }
    
    ultimo = acompanhamentos[0]
    total_executado = sum(a.valor_executado for a in acompanhamentos)
    
    return {
        "servico_id": servico_id,
        "percentual_executado": float(ultimo.percentual_executado),
        "valor_executado": total_executado,
        "capex_reajustado": float(ultimo.capex_reajustado),
        "total_acompanhamentos": len(acompanhamentos),
        "ultima_atualizacao": ultimo.data_atualizacao,
        "responsavel_atual": ultimo.responsavel,
        "setor_atual": ultimo.setor
    }
