from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
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
    
    print(f"[BACKEND] Requisição recebida para importar Excel")
    print(f"[BACKEND] Arquivo: {file.filename}")
    print(f"[BACKEND] Content-Type: {file.content_type}")
    
    try:
        # Validar tipo do arquivo
        if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
            print(f"[BACKEND] Erro: Arquivo inválido - {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Arquivo deve ser Excel (.xlsx ou .xls)"
            )
        
        print(f"[BACKEND] Validação OK, processando arquivo...")
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            try:
                # Escrever conteúdo do arquivo
                content = await file.read()
                print(f"[BACKEND] Tamanho do arquivo: {len(content)} bytes")
                temp_file.write(content)
                temp_file.flush()
                
                print(f"[BACKEND] Arquivo temporário criado: {temp_file.name}")
                
                # Processar planilha
                db = SessionLocal()
                try:
                    print("[BACKEND] Iniciando processamento da planilha...")
                    print(f"[BACKEND] Arquivo temporário: {temp_file.name}")
                    
                    # Verificar se o arquivo existe
                    if not os.path.exists(temp_file.name):
                        print(f"[BACKEND] ERRO: Arquivo temporário não encontrado: {temp_file.name}")
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Arquivo temporário não encontrado"
                        )
                    
                    result = processar_planilha(temp_file.name, db)
                    print(f"[BACKEND] Processamento concluído: {result}")
                    
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "message": "Planilha portuária importada com sucesso!",
                            "filename": file.filename,
                            "type": "concessoes_portuarias",
                            "result": result
                        }
                    )
                finally:
                    db.close()
                    
            except Exception as e:
                print(f"[BACKEND] Erro no processamento da planilha: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail=f"Erro ao processar planilha portuária: {str(e)}"
                )
            finally:
                # Remover arquivo temporário
                try:
                    os.unlink(temp_file.name)
                    print(f"[BACKEND] Arquivo temporário removido: {temp_file.name}")
                except:
                    pass
                    
    except HTTPException:
        # Re-lançar exceções HTTP já tratadas
        raise
    except Exception as e:
        print(f"[BACKEND] Erro geral no endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )
