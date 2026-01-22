# Script PowerShell para instalação e execução
# Sistema de Gestão de Processos e Metas

Write-Host "========================================" -ForegroundColor Green
Write-Host "Sistema de Gestão de Processos e Metas" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python não encontrado. Por favor, instale Python 3.9+" -ForegroundColor Red
    exit 1
}

# Verificar Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Node.js não encontrado. Por favor, instale Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[1/4] Instalando dependências do backend..." -ForegroundColor Yellow

if (-not (Test-Path "backend\venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Cyan
    python -m venv backend\venv
}

& "backend\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip | Out-Null
pip install -r backend\requirements.txt
pip install -r etl\requirements.txt
Write-Host "[OK] Backend instalado" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Instalando dependências do frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..
Write-Host "[OK] Frontend instalado" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Configurando banco de dados..." -ForegroundColor Yellow
Write-Host "[INFO] Certifique-se de que o PostgreSQL está rodando" -ForegroundColor Cyan
Write-Host "[INFO] Configure o arquivo backend\.env com suas credenciais" -ForegroundColor Cyan

if (-not (Test-Path "backend\.env")) {
    Write-Host "[AVISO] Arquivo backend\.env não encontrado" -ForegroundColor Yellow
    Write-Host "[INFO] Copiando env.example para .env" -ForegroundColor Cyan
    Copy-Item "backend\env.example" "backend\.env"
    Write-Host "[INFO] Por favor, edite backend\.env com suas credenciais do banco" -ForegroundColor Yellow
}

python -c "import sys; sys.path.insert(0, 'backend'); from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
Write-Host "[OK] Banco de dados configurado" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Verificando instalação..." -ForegroundColor Yellow
if (Test-Path "backend\venv") {
    Write-Host "[OK] Backend: Instalado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Backend: Não instalado" -ForegroundColor Red
}

if (Test-Path "frontend\node_modules") {
    Write-Host "[OK] Frontend: Instalado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Frontend: Não instalado" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalação concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para executar o projeto:" -ForegroundColor Cyan
Write-Host "  1. Backend:  .\run-backend.bat" -ForegroundColor White
Write-Host "  2. Frontend: .\run-frontend.bat" -ForegroundColor White
Write-Host "  3. Ou use:   make run-backend  e  make run-frontend" -ForegroundColor White
Write-Host ""
