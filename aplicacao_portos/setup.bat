@echo off
REM Script de instalação e execução para Windows
REM Sistema de Gestão de Processos e Metas

setlocal enabledelayedexpansion

echo ========================================
echo Sistema de Gestão de Processos e Metas
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Por favor, instale Python 3.9+
    pause
    exit /b 1
)

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js não encontrado. Por favor, instale Node.js 16+
    pause
    exit /b 1
)

echo [1/4] Instalando dependências do backend...
if not exist "backend\venv" (
    python -m venv backend\venv
)
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install -r etl\requirements.txt
echo [OK] Backend instalado
echo.

echo [2/4] Instalando dependências do frontend...
cd frontend
call npm install
cd ..
echo [OK] Frontend instalado
echo.

echo [3/4] Configurando banco de dados...
echo [INFO] Certifique-se de que o PostgreSQL está rodando
echo [INFO] Configure o arquivo backend\.env com suas credenciais
if not exist "backend\.env" (
    echo [AVISO] Arquivo backend\.env não encontrado
    echo [INFO] Copiando env.example para .env
    copy backend\env.example backend\.env
    echo [INFO] Por favor, edite backend\.env com suas credenciais do banco
)
python -c "import sys; sys.path.insert(0, 'backend'); from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
echo [OK] Banco de dados configurado
echo.

echo [4/4] Verificando instalação...
if exist "backend\venv" (
    echo [OK] Backend: Instalado
) else (
    echo [ERRO] Backend: Não instalado
)

if exist "frontend\node_modules" (
    echo [OK] Frontend: Instalado
) else (
    echo [ERRO] Frontend: Não instalado
)

echo.
echo ========================================
echo Instalação concluída!
echo ========================================
echo.
echo Para executar o projeto:
echo   1. Backend:  run-backend.bat
echo   2. Frontend: run-frontend.bat
echo   3. Ou use:    make run-backend  e  make run-frontend
echo.
pause
