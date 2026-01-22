@echo off
REM Script para processar planilhas Excel

echo ========================================
echo Processador ETL - Planilhas Excel
echo ========================================
echo.

if not exist "backend\venv" (
    echo [ERRO] Ambiente virtual não encontrado!
    echo [INFO] Execute setup.bat primeiro
    pause
    exit /b 1
)

if "%~1"=="" (
    echo [ERRO] Especifique o arquivo Excel
    echo.
    echo Uso: run-etl.bat caminho\para\planilha.xlsx
    echo.
    pause
    exit /b 1
)

if not exist "%~1" (
    echo [ERRO] Arquivo não encontrado: %~1
    pause
    exit /b 1
)

call backend\venv\Scripts\activate.bat
cd etl
echo [INFO] Processando: %~1
echo.
python process_excel.py %~1

pause
