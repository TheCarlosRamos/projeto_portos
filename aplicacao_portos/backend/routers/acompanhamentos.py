from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models_portuarios import Acompanhamento, Servico, Risco, AcompanhamentoRisco
from schemas_portuarios import Acompanhamento as AcompanhamentoSchema, AcompanhamentoCreate as AcompanhamentoCreateSchema

router = APIRouter()

@router.get("/", response_model=List[AcompanhamentoSchema])
def listar_acompanhamentos(
    servico_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista todos os acompanhamentos com filtros opcionais"""
    query = db.query(Acompanhamento).join(Servico)
    
    if servico_id:
        query = query.filter(Acompanhamento.servico_id == servico_id)
    
    acompanhamentos = query.order_by(Acompanhamento.data_atualizacao.desc()).offset(skip).limit(limit).all()
    return acompanhamentos

@router.get("/{acompanhamento_id}", response_model=AcompanhamentoSchema)
def obter_acompanhamento(acompanhamento_id: int, db: Session = Depends(get_db)):
    """Obtém um acompanhamento específico"""
    acompanhamento = db.query(Acompanhamento).filter(Acompanhamento.id == acompanhamento_id).first()
    if not acompanhamento:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    return acompanhamento

@router.post("/", response_model=AcompanhamentoSchema)
def criar_acompanhamento(acompanhamento: AcompanhamentoCreateSchema, db: Session = Depends(get_db)):
    """Cria um novo acompanhamento"""
    # Verificar se serviço existe
    servico = db.query(Servico).filter(Servico.id == acompanhamento.servico_id).first()
    if not servico:
        raise HTTPException(status_code=400, detail="Serviço não encontrado")
    
    db_acompanhamento = Acompanhamento(**acompanhamento.dict(exclude={'risco_ids'}))
    db.add(db_acompanhamento)
    db.commit()
    db.refresh(db_acompanhamento)
    
    # Associar riscos se fornecidos
    if acompanhamento.risco_ids:
        for risco_id in acompanhamento.risco_ids:
            risco = db.query(Risco).filter(Risco.id == risco_id).first()
            if risco:
                associacao = AcompanhamentoRisco(
                    acompanhamento_id=db_acompanhamento.id,
                    risco_id=risco_id
                )
                db.add(associacao)
        
        db.commit()
        db.refresh(db_acompanhamento)
    
    return db_acompanhamento

@router.put("/{acompanhamento_id}", response_model=AcompanhamentoSchema)
def atualizar_acompanhamento(
    acompanhamento_id: int, 
    acompanhamento: AcompanhamentoCreateSchema, 
    db: Session = Depends(get_db)
):
    """Atualiza um acompanhamento existente"""
    db_acompanhamento = db.query(Acompanhamento).filter(Acompanhamento.id == acompanhamento_id).first()
    if not db_acompanhamento:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    
    # Verificar se serviço existe
    servico = db.query(Servico).filter(Servico.id == acompanhamento.servico_id).first()
    if not servico:
        raise HTTPException(status_code=400, detail="Serviço não encontrado")
    
    # Atualizar dados principais
    for key, value in acompanhamento.dict(exclude={'risco_ids'}).items():
        setattr(db_acompanhamento, key, value)
    
    db.commit()
    
    # Atualizar associações de riscos
    if acompanhamento.risco_ids is not None:
        # Remover associações existentes
        db.query(AcompanhamentoRisco).filter(
            AcompanhamentoRisco.acompanhamento_id == acompanhamento_id
        ).delete()
        
        # Adicionar novas associações
        for risco_id in acompanhamento.risco_ids:
            risco = db.query(Risco).filter(Risco.id == risco_id).first()
            if risco:
                associacao = AcompanhamentoRisco(
                    acompanhamento_id=acompanhamento_id,
                    risco_id=risco_id
                )
                db.add(associacao)
    
    db.commit()
    db.refresh(db_acompanhamento)
    return db_acompanhamento

@router.delete("/{acompanhamento_id}")
def deletar_acompanhamento(acompanhamento_id: int, db: Session = Depends(get_db)):
    """Remove um acompanhamento"""
    db_acompanhamento = db.query(Acompanhamento).filter(Acompanhamento.id == acompanhamento_id).first()
    if not db_acompanhamento:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    
    # Remover associações de riscos
    db.query(AcompanhamentoRisco).filter(
        AcompanhamentoRisco.acompanhamento_id == acompanhamento_id
    ).delete()
    
    db.delete(db_acompanhamento)
    db.commit()
    return {"message": "Acompanhamento removido com sucesso"}

@router.get("/servico/{servico_id}/historico")
def historico_acompanhamentos_servico(servico_id: int, db: Session = Depends(get_db)):
    """Histórico completo de acompanhamentos de um serviço"""
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    acompanhamentos = db.query(Acompanhamento).filter(
        Acompanhamento.servico_id == servico_id
    ).order_by(Acompanhamento.data_atualizacao.asc()).all()
    
    historico = []
    for acomp in acompanhamentos:
        riscos = [risco for risco in acomp.riscos]
        historico.append({
            "id": acomp.id,
            "data_atualizacao": acomp.data_atualizacao,
            "percentual_executado": float(acomp.percentual_executado),
            "valor_executado": float(acomp.valor_executado),
            "capex_reajustado": float(acomp.capex_reajustado),
            "responsavel": acomp.responsavel,
            "cargo": acomp.cargo,
            "setor": acomp.setor,
            "riscos": [{"id": r.id, "tipo": r.tipo, "descricao": r.descricao} for r in riscos]
        })
    
    return {
        "servico_id": servico_id,
        "servico_nome": servico.nome,
        "total_acompanhamentos": len(historico),
        "historico": historico
    }
