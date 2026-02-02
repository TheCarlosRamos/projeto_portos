# 🚢 Gestão de Concessões Portuárias

Sistema completo para gestão e acompanhamento de concessões portuárias no Brasil, desenvolvido para visualização e análise de projetos de arrendamento de terminais portuários.

## 🎯 O que é esta Aplicação

Esta é uma plataforma web que gerencia e visualiza dados de concessões portuárias brasileiras, oferecendo:

- **Dashboard Interativo**: Visualização completa de todos os projetos portuários com mapas, gráficos e estatísticas
- **Gestão de Dados**: Sistema completo para cadastro e acompanhamento de projetos de concessão
- **Análise Geográfica**: Mapas interativos com localização exata dos portos e terminais
- **Relatórios Dinâmicos**: Geração automática de relatórios e indicadores de progresso

## 📋 Estrutura do Projeto

### Frontend Principal
- **`index.html`** - Aplicação web principal com dashboard interativo, mapas e visualizações
- **`data.js`** - Dados dos projetos portuários convertidos para JavaScript
- **`dados_completos.json`** - Base de dados completa com informações detalhadas dos projetos

### Backend Completo
- **`app/`** - Sistema backend completo com API REST e dashboard administrativo
  - **`api.py`** - API RESTful para gerenciamento dos dados portuários
  - **`app.py`** - Dashboard administrativo em Streamlit para gestão completa
  - **`db.py`** - Configuração e gerenciamento do banco de dados SQLite

## 🚀 Deploy

### 1. GitHub Pages (Versão Principal)

A versão principal está configurada para GitHub Pages:

1. **Ativação Manual (necessária apenas uma vez):**
   - Vá para Settings > Pages do repositório
   - Source: Deploy from a branch
   - Branch: gh-pages
   - Folder: / (root)
   - Salve as configurações

2. **Deploy Automático:**
   - O workflow `.github/workflows/github-pages.yml` é acionado automaticamente
   - Cada push para `main` atualiza o site

### 2. Vercel (Versão Estática)

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

### 3. Railway (API Backend)

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




## � O que a Aplicação Faz

### Funcionalidades Principais
- **Visualização de Projetos**: Exibe todos os projetos de concessão portuária com informações detalhadas como investimento, progresso e etapa atual
- **Mapas Interativos**: Localização geográfica precisa dos portos e terminais com marcadores clicáveis
- **Análise de Dados**: Gráficos e estatísticas sobre investimentos, progresso das obras e distribuição regional
- **Gestão Administrativa**: Interface completa para cadastro, edição e acompanhamento dos projetos
- **Relatórios Automáticos**: Geração de relatórios de progresso e indicadores de desempenho

### Fluxo de Dados
1. **Dados Base**: Informações dos projetos são armazenadas em formato JSON
2. **Frontend**: Carrega os dados e exibe visualizações interativas
3. **Backend**: API REST para operações CRUD e dashboard administrativo
4. **Banco de Dados**: SQLite para persistência dos dados no backend

## 🛠️ Tecnologias Utilizadas

### Frontend
- **HTML5 & CSS3**: Estrutura e estilo semântico
- **Tailwind CSS**: Framework CSS para design responsivo e moderno
- **JavaScript**: Lógica de interação e manipulação de dados
- **Leaflet.js**: Biblioteca para mapas interativos
- **Chart.js**: Visualização de dados com gráficos dinâmicos
- **Font Awesome**: Ícones e elementos visuais

### Backend
- **Flask**: Framework web Python para API REST
- **Streamlit**: Dashboard interativo para gestão administrativa
- **SQLite**: Banco de dados leve e portátil
- **Python 3.9+**: Linguagem principal do backend


