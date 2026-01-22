@echo off
REM Script para executar o backend

echo ========================================
echo Iniciando Backend (FastAPI)
echo ========================================
echo.

if not exist "backend\venv" (
    echo [ERRO] Ambiente virtual não encontrado!
    echo [INFO] Execute setup.bat primeiro
    pause
    exit /b 1
)

if not exist "backend\.env" (
    echo [AVISO] Arquivo .env não encontrado
    echo [INFO] Criando .env a partir do exemplo...
    copy backend\env.example backend\.env
    echo [AVISO] Por favor, configure backend\.env com suas credenciais
    echo.
)

call backend\venv\Scripts\activate.bat
cd backend
echo [INFO] Backend rodando em: http://localhost:8000
echo [INFO] Documentação da API: http://localhost:8000/docs
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
