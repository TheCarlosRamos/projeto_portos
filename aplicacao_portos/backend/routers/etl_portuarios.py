from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
import sys

# Adicionar diretório ETL ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "etl"))

from sqlalchemy.orm import Session
from database import SessionLocal
from process_excel_portuarios import processar_planilha

router = APIRouter()

@router.post("/importar-excel-portuarios")
async def importar_excel_portuarios(file: UploadFile = File(...)):
    """Importa dados de uma planilha Excel de concessões portuárias"""
    
    # Validar tipo do arquivo
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Arquivo deve ser Excel (.xlsx ou .xls)")
    
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        try:
            # Escrever conteúdo do arquivo
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Processar planilha
            db = SessionLocal()
            try:
                processar_planilha(temp_file.name, db)
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Planilha portuária importada com sucesso!",
                        "filename": file.filename,
                        "type": "concessoes_portuarias"
                    }
                )
            finally:
                db.close()
                
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao processar planilha portuária: {str(e)}"
            )
        finally:
            # Remover arquivo temporário
            try:
                os.unlink(temp_file.name)
            except:
                pass
