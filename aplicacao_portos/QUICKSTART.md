# 🚀 Guia Rápido de Início

## Instalação Rápida (Windows)

### 1. Pré-requisitos

Certifique-se de ter instalado:
- ✅ Python 3.9+ ([Download](https://www.python.org/downloads/))
- ✅ Node.js 16+ ([Download](https://nodejs.org/))
- ✅ PostgreSQL 12+ ([Download](https://www.postgresql.org/download/))

### 2. Instalação Automatizada

Execute no PowerShell ou CMD:

```powershell
# Opção 1: PowerShell
.\setup.ps1

# Opção 2: Batch
setup.bat
```

Isso irá:
- ✅ Criar ambiente virtual Python
- ✅ Instalar dependências do backend
- ✅ Instalar dependências do frontend
- ✅ Instalar dependências do ETL
- ✅ Configurar banco de dados

### 3. Configurar Banco de Dados

1. Inicie o PostgreSQL
2. Crie o banco de dados:
   ```sql
   CREATE DATABASE gestao_processos;
   ```
3. Edite `backend\.env`:
   ```
   DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/gestao_processos
   ```

### 4. Executar o Projeto

#### Opção A: Scripts Batch (Recomendado)

**Terminal 1 - Backend:**
```batch
run-backend.bat
```

**Terminal 2 - Frontend:**
```batch
run-frontend.bat
```

#### Opção B: Makefile

Se você tiver `make` instalado (Git Bash, WSL, ou Chocolatey):

```bash
# Terminal 1
make run-backend

# Terminal 2
make run-frontend
```

### 5. Acessar o Sistema

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs

## Processar Planilhas Excel

```batch
run-etl.bat caminho\para\sua_planilha.xlsx
```

Ou com Makefile:
```bash
make run-etl ARQUIVO=caminho/planilha.xlsx
```

## Estrutura Esperada da Planilha

A planilha deve ter:
- Abas separadas por ano (ex: "2025", "2026", "2027")
- Colunas principais:
  - Nº PROCESSO / numero_processo
  - DATA DO PROTOCOLO / data_protocolo
  - LICENÇA / licenca
  - SITUAÇÃO GERAL / situacao_geral

## Troubleshooting

### Erro: "Python não encontrado"
- Certifique-se de que Python está no PATH
- Reinstale Python marcando "Add Python to PATH"

### Erro: "Node.js não encontrado"
- Instale Node.js e reinicie o terminal

### Erro de conexão com banco
- Verifique se o PostgreSQL está rodando
- Confira as credenciais em `backend\.env`

### Porta já em uso
- Backend: Altere a porta em `run-backend.bat` (linha com `--port 8001`)
- Frontend: Crie `frontend\.env` com `PORT=3001`

## Próximos Passos

1. ✅ Acesse http://localhost:3000
2. ✅ Cadastre alguns processos
3. ✅ Crie metas para os processos
4. ✅ Adicione indicadores às metas
5. ✅ Processe suas planilhas Excel

## Ajuda

Para ver todos os comandos disponíveis:
```bash
make help
```

Ou consulte a documentação completa em `docs/INSTALACAO.md`
