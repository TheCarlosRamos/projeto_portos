@echo off
REM Script para executar o frontend

echo ========================================
echo Iniciando Frontend (React)
echo ========================================
echo.

if not exist "frontend\node_modules" (
    echo [ERRO] Dependências não instaladas!
    echo [INFO] Execute setup.bat primeiro
    pause
    exit /b 1
)

cd frontend
echo [INFO] Frontend rodando em: http://localhost:3000
echo.
call npm start
