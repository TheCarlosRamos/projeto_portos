# Backend - Sistema de Gestão de Concessões Portuárias

API REST construída com FastAPI para gerenciamento de concessões portuárias.

## Estrutura

```
backend/
├── app/
│   ├── api/          # Endpoints da API
│   ├── models/       # Modelos SQLAlchemy
│   ├── schemas/      # Schemas Pydantic
│   └── database.py   # Configuração do banco
├── main.py           # Aplicação principal
├── init_db.py        # Script de inicialização
└── requirements.txt  # Dependências
```

## Instalação Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados (primeira vez)
python init_db.py

# Executar servidor
python main.py
```

A API estará disponível em `http://localhost:8000`

## Endpoints

### Projetos
- `GET /api/projects` - Lista todos os projetos
- `GET /api/projects/{id}` - Detalhes de um projeto
- `POST /api/projects` - Criar novo projeto
- `PUT /api/projects/{id}` - Atualizar projeto
- `DELETE /api/projects/{id}` - Deletar projeto

### Serviços
- `GET /api/servicos` - Lista todos os serviços
- `GET /api/servicos/{id}` - Detalhes de um serviço
- `POST /api/servicos` - Criar novo serviço
- `PUT /api/servicos/{id}` - Atualizar serviço
- `DELETE /api/servicos/{id}` - Deletar serviço

### Acompanhamento
- `GET /api/acompanhamento` - Lista todos os acompanhamentos
- `GET /api/acompanhamento/{id}` - Detalhes de um acompanhamento
- `POST /api/acompanhamento` - Criar novo acompanhamento
- `PUT /api/acompanhamento/{id}` - Atualizar acompanhamento
- `DELETE /api/acompanhamento/{id}` - Deletar acompanhamento

## Deploy no Railway

1. Crie um novo projeto no Railway
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente:
   - `PORT` (Railway define automaticamente)
   - `CORS_ORIGINS` (URL do frontend no Vercel)
4. O Railway detectará automaticamente o `railway.json` e fará o deploy

## Documentação da API

Após iniciar o servidor, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
