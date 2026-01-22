# Guia de Instalação

## Pré-requisitos

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

## 1. Configuração do Banco de Dados

```bash
# Criar banco de dados
createdb gestao_processos

# Ou via psql
psql -U postgres
CREATE DATABASE gestao_processos;
```

## 2. Configuração do Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas credenciais do banco

# Criar tabelas
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"

# Iniciar servidor
uvicorn main:app --reload
```

O backend estará disponível em: http://localhost:8000
Documentação da API: http://localhost:8000/docs

## 3. Configuração do Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start
```

O frontend estará disponível em: http://localhost:3000

## 4. Processamento de Planilhas (ETL)

```bash
cd etl

# Instalar dependências
pip install -r requirements.txt

# Processar planilha
python process_excel.py caminho/para/planilha.xlsx
```

## Estrutura de Dados

O sistema espera planilhas Excel com as seguintes características:

- Abas separadas por ano (ex: "2025", "2026", "2027")
- Colunas principais:
  - Nº PROCESSO / numero_processo
  - DATA DO PROTOCOLO / data_protocolo
  - LICENÇA / licenca
  - SITUAÇÃO GERAL / situacao_geral
  - Colunas de indicadores (financeiro, km, extensão, etc.)

## Troubleshooting

### Erro de conexão com banco

Verifique as credenciais no arquivo `.env` do backend.

### Erro ao processar planilha

Certifique-se de que as abas contêm dados e que os nomes das colunas estão corretos.

### Porta já em uso

Altere as portas padrão:
- Backend: `uvicorn main:app --port 8001`
- Frontend: Crie um arquivo `.env` com `PORT=3001`
