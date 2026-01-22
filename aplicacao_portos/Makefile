.PHONY: help install install-backend install-frontend install-etl setup-db run-backend run-frontend run-etl clean test check

# Detectar SO
ifeq ($(OS),Windows_NT)
    PYTHON = python
    PIP = pip
    VENV_BIN = backend/venv/Scripts
    VENV_ACTIVATE = $(VENV_BIN)/activate
    RM = rmdir /s /q
    MKDIR = if not exist
    PYTHON_CMD = $(VENV_BIN)\python
    PIP_CMD = $(VENV_BIN)\pip
    UVCORN_CMD = $(VENV_BIN)\uvicorn
else
    PYTHON = python3
    PIP = pip3
    VENV_BIN = backend/venv/bin
    VENV_ACTIVATE = $(VENV_BIN)/activate
    RM = rm -rf
    MKDIR = mkdir -p
    PYTHON_CMD = $(VENV_BIN)/python
    PIP_CMD = $(VENV_BIN)/pip
    UVCORN_CMD = $(VENV_BIN)/uvicorn
endif

BACKEND_DIR = backend
FRONTEND_DIR = frontend
ETL_DIR = etl

# Cores (funciona em Git Bash, WSL, Linux, Mac)
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)╔════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  Sistema de Gestão de Processos e Metas    ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: install-backend install-frontend install-etl ## Instala todas as dependências

install-backend: ## Instala dependências do backend
	@echo "$(GREEN)[1/3] Instalando dependências do backend...$(NC)"
ifeq ($(OS),Windows_NT)
	@if not exist "$(BACKEND_DIR)\venv" $(PYTHON) -m venv $(BACKEND_DIR)\venv
	@$(PYTHON_CMD) -m pip install --upgrade pip
	@$(PIP_CMD) install -r $(BACKEND_DIR)/requirements.txt
else
	@test -d $(BACKEND_DIR)/venv || $(PYTHON) -m venv $(BACKEND_DIR)/venv
	@$(PYTHON_CMD) -m pip install --upgrade pip
	@$(PIP_CMD) install -r $(BACKEND_DIR)/requirements.txt
endif
	@echo "$(GREEN)✓ Backend instalado$(NC)"

install-frontend: ## Instala dependências do frontend
	@echo "$(GREEN)[2/3] Instalando dependências do frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)✓ Frontend instalado$(NC)"

install-etl: ## Instala dependências do ETL
	@echo "$(GREEN)[3/3] Instalando dependências do ETL...$(NC)"
	@$(PIP_CMD) install -r $(ETL_DIR)/requirements.txt
	@echo "$(GREEN)✓ ETL instalado$(NC)"

setup-db: ## Cria as tabelas do banco de dados
	@echo "$(GREEN)Configurando banco de dados...$(NC)"
	@echo "$(YELLOW)Certifique-se de que o PostgreSQL está rodando$(NC)"
	@echo "$(YELLOW)Configure backend/.env com suas credenciais$(NC)"
ifeq ($(OS),Windows_NT)
	@$(PYTHON_CMD) -c "import sys; sys.path.insert(0, '$(BACKEND_DIR)'); from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
else
	@cd $(BACKEND_DIR) && $(PYTHON_CMD) -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
endif
	@echo "$(GREEN)✓ Banco de dados configurado$(NC)"

run-backend: ## Inicia o servidor backend
	@echo "$(GREEN)Iniciando backend em http://localhost:8000$(NC)"
	@echo "$(BLUE)Documentação: http://localhost:8000/docs$(NC)"
ifeq ($(OS),Windows_NT)
	@cd $(BACKEND_DIR) && $(UVCORN_CMD) main:app --reload --host 0.0.0.0 --port 8000
else
	@cd $(BACKEND_DIR) && $(UVCORN_CMD) main:app --reload --host 0.0.0.0 --port 8000
endif

run-frontend: ## Inicia o servidor frontend
	@echo "$(GREEN)Iniciando frontend em http://localhost:3000$(NC)"
	@cd $(FRONTEND_DIR) && npm start

run-etl: ## Processa planilha Excel (use: make run-etl ARQUIVO=caminho/planilha.xlsx)
	@if [ -z "$(ARQUIVO)" ]; then \
		echo "$(YELLOW)Erro: Especifique o arquivo com ARQUIVO=caminho/planilha.xlsx$(NC)"; \
		echo "Exemplo: make run-etl ARQUIVO=planilhas/dados.xlsx"; \
		exit 1; \
	fi
	@echo "$(GREEN)Processando planilha: $(ARQUIVO)...$(NC)"
ifeq ($(OS),Windows_NT)
	@cd $(ETL_DIR) && ..\$(PYTHON_CMD) process_excel.py $(ARQUIVO)
else
	@cd $(ETL_DIR) && ../$(PYTHON_CMD) process_excel.py $(ARQUIVO)
endif

clean: ## Remove arquivos gerados e cache
	@echo "$(YELLOW)Limpando arquivos...$(NC)"
ifeq ($(OS),Windows_NT)
	@if exist "$(BACKEND_DIR)\venv" $(RM) "$(BACKEND_DIR)\venv"
	@if exist "$(FRONTEND_DIR)\node_modules" $(RM) "$(FRONTEND_DIR)\node_modules"
	@if exist "$(FRONTEND_DIR)\build" $(RM) "$(FRONTEND_DIR)\build"
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" $(RM) "%%d"
	@del /s /q *.pyc 2>nul
else
	@$(RM) $(BACKEND_DIR)/venv
	@$(RM) $(FRONTEND_DIR)/node_modules
	@$(RM) $(FRONTEND_DIR)/build
	@find . -type d -name __pycache__ -exec $(RM) {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
endif
	@echo "$(GREEN)✓ Limpeza concluída$(NC)"

test: ## Executa testes (quando implementados)
	@echo "$(YELLOW)Testes ainda não implementados$(NC)"

check: ## Verifica se todas as dependências estão instaladas
	@echo "$(GREEN)Verificando instalação...$(NC)"
ifeq ($(OS),Windows_NT)
	@if exist "$(BACKEND_DIR)\venv" ( \
		echo "$(GREEN)✓ Backend instalado$(NC)" \
	) else ( \
		echo "$(YELLOW)✗ Backend não instalado. Execute: make install-backend$(NC)" \
	)
	@if exist "$(FRONTEND_DIR)\node_modules" ( \
		echo "$(GREEN)✓ Frontend instalado$(NC)" \
	) else ( \
		echo "$(YELLOW)✗ Frontend não instalado. Execute: make install-frontend$(NC)" \
	)
else
	@test -d $(BACKEND_DIR)/venv && echo "$(GREEN)✓ Backend instalado$(NC)" || echo "$(YELLOW)✗ Backend não instalado. Execute: make install-backend$(NC)"
	@test -d $(FRONTEND_DIR)/node_modules && echo "$(GREEN)✓ Frontend instalado$(NC)" || echo "$(YELLOW)✗ Frontend não instalado. Execute: make install-frontend$(NC)"
endif
	@echo "$(GREEN)Verificação concluída$(NC)"

dev: ## Inicia backend e frontend (requer terminal paralelo ou tmux)
	@echo "$(YELLOW)Use dois terminais separados:$(NC)"
	@echo "$(BLUE)Terminal 1: make run-backend$(NC)"
	@echo "$(BLUE)Terminal 2: make run-frontend$(NC)"
