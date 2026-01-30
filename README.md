# 🚢 Gestão de Concessões Portuárias

Sistema completo para gestão de concessões portuárias com dashboard interativo e API REST.

## 📋 Estrutura do Projeto

- **`app/present_tela/portos.html`** - Versão estática para apresentação (deploy no Vercel)
- **`app/present_tela/planilha_portos.json`** - Dados dos projetos
- **`app/`** - Backend completo com API Flask (deploy no Railway)
  - **`api.py`** - API REST para dados dos portos
  - **`app.py`** - Dashboard Streamlit completo
  - **`db.py`** - Configuração do banco SQLite

## 🚀 Deploy

### 1. Vercel (Versão Estática)

A versão estática será implantada no Vercel:

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Ou através do dashboard Vercel:
1. Conecte seu repositório GitHub
2. Configure o diretório raiz
3. Deploy automático

### 2. Railway (API Backend)

A API será implantada no Railway:

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login e deploy
railway login
railway init
railway up
```

Ou através do dashboard Railway:
1. Conecte seu repositório GitHub
2. Configure as variáveis de ambiente
3. Deploy automático

## 🔧 Configurações

### Variáveis de Ambiente (Railway)
- `PORT` - Porta do servidor (padrão: 8080)
- `FLASK_ENV` - Ambiente (production)

### Endpoints da API

- `GET /api/health` - Health check
- `GET /api/portos` - Lista todos os portos
- `GET /api/portos/summary` - Resumo estatístico

## 📁 Arquivos de Configuração

- **`vercel.json`** - Configuração do Vercel
- **`railway.toml`** - Configuração do Railway
- **`Procfile`** - Comando de execução no Railway

## 🌐 URLs de Produção

Após o deploy:

- **Vercel**: `https://seu-projeto.vercel.app`
- **Railway**: `https://seu-app.railway.app`

## 🔄 Integração

A versão estática no Vercel consome os dados diretamente do arquivo `planilha_portos.json`. Se precisar conectar com a API no Railway, atualize o `portos.html`:

```javascript
// Substitua o carregamento local por:
const response = await fetch('https://seu-app.railway.app/api/projects');
```

## 📊 Funcionalidades

- ✅ Dashboard interativo com mapas
- ✅ Cards de projetos com informações detalhadas
- ✅ Mapa com marcadores geográficos
- ✅ API REST completa
- ✅ Banco de dados SQLite
- ✅ Responsivo e moderno

## 🛠️ Tecnologias

- **Frontend**: HTML5, Tailwind CSS, Leaflet, Chart.js
- **Backend**: Flask, SQLite
- **Deploy**: Vercel, Railway
- **CI/CD**: GitHub Actions
