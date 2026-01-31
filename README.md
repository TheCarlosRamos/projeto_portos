# 🚢 Sistema de Gestão de Concessões Portuárias

Sistema completo para gestão e acompanhamento de concessões portuárias, desenvolvido com FastAPI (backend) e HTML/JS/CSS (frontend).

## 🎯 Funcionalidades

- ✅ Dashboard com visualização de projetos
- ✅ Mapa interativo com localização dos portos
- ✅ Gestão de cadastros, serviços e acompanhamentos
- ✅ API REST completa
- ✅ Busca e filtros
- ✅ Interface responsiva e moderna

## 🏗️ Arquitetura

```
projeto_portos/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── api/      # Endpoints
│   │   ├── models/   # Modelos SQLAlchemy
│   │   └── schemas/  # Schemas Pydantic
│   ├── main.py       # Aplicação principal
│   └── init_db.py    # Inicialização do banco
│
├── frontend/         # Interface web
│   ├── index.html    # Página principal
│   ├── app.js        # Lógica da aplicação
│   └── config.js     # Configuração
│
└── planilha_portos.json  # Dados iniciais
```

## 🚀 Deploy

### Opções de Deploy (100% Gratuitas)

#### Opção 1: Tudo no Vercel (Mais Fácil) ⭐
- **Backend**: Vercel Serverless
- **Frontend**: Vercel
- 📖 **Guia**: [DEPLOY_VERCEL_COMPLETO.md](./DEPLOY_VERCEL_COMPLETO.md)
- ⏱️ **Tempo**: ~10 minutos
- ✅ **Melhor para**: Protótipos, demos, MVPs

#### Opção 2: Render + Vercel (Recomendado para Produção)
- **Backend**: Render (com PostgreSQL)
- **Frontend**: Vercel
- 📖 **Guia**: [ALTERNATIVAS_GRATUITAS.md](./ALTERNATIVAS_GRATUITAS.md)
- ⏱️ **Tempo**: ~15 minutos
- ✅ **Melhor para**: Aplicações de produção

#### Opção 3: Railway + Vercel (Requer Trial)
- **Backend**: Railway
- **Frontend**: Vercel
- 📖 **Guia**: [GUIA_DEPLOY.md](./GUIA_DEPLOY.md)
- ⏱️ **Tempo**: ~20 minutos
- ⚠️ **Nota**: Railway requer trial (expirou)

### Desenvolvimento Local

#### Backend

```bash
cd backend
pip install -r requirements.txt
python init_db.py  # Primeira vez apenas
python main.py
```

Acesse: http://localhost:8000

#### Frontend

```bash
cd frontend
python -m http.server 3000
```

Acesse: http://localhost:3000

## 📚 Documentação da API

Após iniciar o backend, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints Principais

#### Projetos
- `GET /api/projects` - Lista todos os projetos
- `GET /api/projects/{id}` - Detalhes de um projeto
- `POST /api/projects` - Criar projeto
- `PUT /api/projects/{id}` - Atualizar projeto
- `DELETE /api/projects/{id}` - Deletar projeto

#### Serviços
- `GET /api/servicos` - Lista serviços
- `POST /api/servicos` - Criar serviço
- `PUT /api/servicos/{id}` - Atualizar serviço
- `DELETE /api/servicos/{id}` - Deletar serviço

#### Acompanhamento
- `GET /api/acompanhamento` - Lista acompanhamentos
- `POST /api/acompanhamento` - Criar acompanhamento
- `PUT /api/acompanhamento/{id}` - Atualizar acompanhamento
- `DELETE /api/acompanhamento/{id}` - Deletar acompanhamento

## 🔧 Tecnologias

### Backend
- FastAPI 0.104.1
- SQLAlchemy 2.0+
- Pydantic 2.5.0
- Uvicorn 0.24.0

### Frontend
- HTML5
- JavaScript (Vanilla)
- Tailwind CSS
- Leaflet (mapas)
- Chart.js (gráficos)

## 📝 Estrutura de Dados

### Projeto (Tabela 00 - Cadastro)
- Zona portuária
- UF
- Objeto de concessão
- Tipo (Concessão/Arrendamento/Autorização)
- CAPEX total e executado
- Data de assinatura
- Coordenadas (latitude/longitude)

### Serviço (Tabela 01 - Serviços)
- Tipo de serviço
- Fase
- Descrição
- Prazos e datas
- CAPEX do serviço

### Acompanhamento (Tabela 02 - Acompanhamento)
- Percentual executado
- Valor executado
- Responsável
- Riscos relacionados

## 🤝 Comparação com GENETIKS

Este projeto foi estruturado seguindo o padrão bem-sucedido do projeto GENETIKS:

| Aspecto | GENETIKS | Projeto Portos |
|---------|----------|----------------|
| Backend | FastAPI | FastAPI ✅ |
| ORM | SQLAlchemy | SQLAlchemy ✅ |
| Validação | Pydantic | Pydantic ✅ |
| CORS | Configurado | Configurado ✅ |
| Deploy Backend | Railway | Railway ✅ |
| Deploy Frontend | Vercel | Vercel ✅ |
| API REST | Completa | Completa ✅ |

## 📖 Guias

- [GUIA_DEPLOY.md](./GUIA_DEPLOY.md) - Instruções completas de deploy
- [backend/README.md](./backend/README.md) - Documentação do backend
- [frontend/README.md](./frontend/README.md) - Documentação do frontend

## 🐛 Solução de Problemas

### CORS Error
Verifique se `CORS_ORIGINS` no Railway inclui a URL do Vercel.

### Banco de Dados Vazio
Execute `python init_db.py` no Railway.

### Frontend não carrega dados
Verifique se `config.js` tem a URL correta do backend.

## 📄 Licença

Este projeto foi desenvolvido para gestão de concessões portuárias.

## 👥 Contato

Para dúvidas ou suporte, consulte a documentação ou abra uma issue.
