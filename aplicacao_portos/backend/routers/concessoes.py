from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models_portuarios import Concessao, ZonaPortuaria, Servico, TipoServico
from schemas_portuarios import Concessao as ConcessaoSchema, ConcessaoCreate as ConcessaoCreateSchema, ConcessaoFilter, ConcessaoComServicos

router = APIRouter()

@router.get("/", response_model=List[ConcessaoSchema])
def listar_concessoes(
    zona_portuaria_id: Optional[int] = Query(None),
    uf: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista todas as concessões com filtros opcionais"""
    query = db.query(Concessao).join(ZonaPortuaria)
    
    if zona_portuaria_id:
        query = query.filter(Concessao.zona_portuaria_id == zona_portuaria_id)
    if uf:
        query = query.filter(ZonaPortuaria.uf == uf)
    if tipo:
        query = query.filter(Concessao.tipo.ilike(f"%{tipo}%"))
    
    concessoes = query.offset(skip).limit(limit).all()
    return concessoes

@router.get("/{concessao_id}", response_model=ConcessaoComServicos)
def obter_concessao(concessao_id: int, db: Session = Depends(get_db)):
    """Obtém uma concessão específica com seus serviços"""
    concessao = db.query(Concessao).filter(Concessao.id == concessao_id).first()
    if not concessao:
        raise HTTPException(status_code=404, detail="Concessão não encontrada")
    return concessao

@router.post("/", response_model=ConcessaoSchema)
def criar_concessao(concessao: ConcessaoCreateSchema, db: Session = Depends(get_db)):
    """Cria uma nova concessão"""
    # Verificar se zona portuária existe
    zona = db.query(ZonaPortuaria).filter(ZonaPortuaria.id == concessao.zona_portuaria_id).first()
    if not zona:
        raise HTTPException(status_code=400, detail="Zona portuária não encontrada")
    
    # Verificar duplicação
    existente = db.query(Concessao).filter(
        Concessao.zona_portuaria_id == concessao.zona_portuaria_id,
        Concessao.objeto_concessao == concessao.objeto_concessao
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Já existe uma concessão para esta zona e objeto")
    
    db_concessao = Concessao(**concessao.dict())
    db.add(db_concessao)
    db.commit()
    db.refresh(db_concessao)
    return db_concessao

@router.put("/{concessao_id}", response_model=ConcessaoSchema)
def atualizar_concessao(
    concessao_id: int, 
    concessao: ConcessaoCreateSchema, 
    db: Session = Depends(get_db)
):
    """Atualiza uma concessão existente"""
    db_concessao = db.query(Concessao).filter(Concessao.id == concessao_id).first()
    if not db_concessao:
        raise HTTPException(status_code=404, detail="Concessão não encontrada")
    
    # Verificar se zona portuária existe
    zona = db.query(ZonaPortuaria).filter(ZonaPortuaria.id == concessao.zona_portuaria_id).first()
    if not zona:
        raise HTTPException(status_code=400, detail="Zona portuária não encontrada")
    
    # Verificar duplicação (excluindo a própria)
    existente = db.query(Concessao).filter(
        Concessao.zona_portuaria_id == concessao.zona_portuaria_id,
        Concessao.objeto_concessao == concessao.objeto_concessao,
        Concessao.id != concessao_id
    ).first()
    
    if existente:
        raise HTTPException(status_code=400, detail="Já existe uma concessão para esta zona e objeto")
    
    for key, value in concessao.dict().items():
        setattr(db_concessao, key, value)
    
    db.commit()
    db.refresh(db_concessao)
    return db_concessao

@router.delete("/{concessao_id}")
def deletar_concessao(concessao_id: int, db: Session = Depends(get_db)):
    """Remove uma concessão"""
    db_concessao = db.query(Concessao).filter(Concessao.id == concessao_id).first()
    if not db_concessao:
        raise HTTPException(status_code=404, detail="Concessão não encontrada")
    
    db.delete(db_concessao)
    db.commit()
    return {"message": "Concessão removida com sucesso"}

@router.get("/{concessao_id}/resumo-capex")
def resumo_capex_concessao(concessao_id: int, db: Session = Depends(get_db)):
    """Resumo financeiro da concessão"""
    concessao = db.query(Concessao).filter(Concessao.id == concessao_id).first()
    if not concessao:
        raise HTTPException(status_code=404, detail="Concessão não encontrada")
    
    servicos = db.query(Servico).filter(Servico.concessao_id == concessao_id).all()
    
    total_planejado = sum(s.capex_servico for s in servicos)
    total_executado = 0
    percentual_geral = 0
    
    for servico in servicos:
        for acompanhamento in servico.acompanhamentos:
            total_executado += acompanhamento.valor_executado
    
    if total_planejado > 0:
        percentual_geral = (total_executado / total_planejado) * 100
    
    return {
        "concessao_id": concessao_id,
        "capex_total": concessao.capex_total,
        "capex_planejado_servicos": total_planejado,
        "capex_executado": total_executado,
        "percentual_executado_geral": round(percentual_geral, 2),
        "total_servicos": len(servicos)
    }
