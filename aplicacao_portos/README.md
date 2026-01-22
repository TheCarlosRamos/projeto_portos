# Sistema Web de Gestão de Processos e Metas

Sistema web para cadastro, gerenciamento, acompanhamento e análise de processos administrativos e metas físicas/financeiras.

## 🏗️ Arquitetura

- **Backend**: FastAPI + PostgreSQL
- **Frontend**: React + TypeScript
- **ETL**: Python + Pandas

## 📁 Estrutura do Projeto

```
.
├── backend/          # API FastAPI
├── frontend/         # Aplicação React
├── etl/             # Scripts de processamento de planilhas
├── docs/            # Documentação
└── README.md
```

## 🚀 Instalação e Execução

### Instalação Automatizada (Recomendado)

#### Windows (PowerShell/Batch)

```powershell
# Opção 1: Script PowerShell
.\setup.ps1

# Opção 2: Script Batch
setup.bat
```

#### Linux/Mac ou Windows com Make

```bash
# Instalar todas as dependências
make install

# Ou instalar separadamente
make install-backend
make install-frontend
make install-etl
```

### Execução

#### Usando Makefile

```bash
# Iniciar backend
make run-backend

# Iniciar frontend (em outro terminal)
make run-frontend

# Processar planilha Excel
make run-etl ARQUIVO=caminho/planilha.xlsx

# Verificar instalação
make check

# Ver ajuda
make help
```

#### Usando Scripts Windows

```batch
# Iniciar backend
run-backend.bat

# Iniciar frontend (em outro terminal)
run-frontend.bat

# Processar planilha Excel
run-etl.bat caminho\planilha.xlsx
```

### Instalação Manual

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

#### Banco de Dados

1. Configure o PostgreSQL
2. Crie o banco: `createdb gestao_processos`
3. Configure `backend/.env` com suas credenciais:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/gestao_processos
   ```
4. Execute: `make setup-db` ou `python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"`

#### ETL

```bash
cd etl
pip install -r requirements.txt
python process_excel.py planilha.xlsx
```

## 📝 Documentação da API

Após iniciar o backend, acesse: http://localhost:8000/docs

## 🛠️ Comandos Úteis

### Makefile

- `make help` - Mostra todos os comandos disponíveis
- `make install` - Instala todas as dependências
- `make install-backend` - Instala apenas o backend
- `make install-frontend` - Instala apenas o frontend
- `make setup-db` - Cria as tabelas do banco de dados
- `make run-backend` - Inicia o servidor backend
- `make run-frontend` - Inicia o servidor frontend
- `make run-etl ARQUIVO=planilha.xlsx` - Processa planilha Excel
- `make check` - Verifica se tudo está instalado
- `make clean` - Remove arquivos gerados e cache

### Scripts Windows

- `setup.bat` ou `setup.ps1` - Instalação completa
- `run-backend.bat` - Executa o backend
- `run-frontend.bat` - Executa o frontend
- `run-etl.bat planilha.xlsx` - Processa planilha Excel
