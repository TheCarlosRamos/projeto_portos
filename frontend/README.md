# Frontend - Sistema de Gestão de Concessões Portuárias

Interface web para visualização e gestão de concessões portuárias.

## Estrutura

```
frontend/
├── index.html    # Página principal
├── app.js        # Lógica da aplicação
├── config.js     # Configuração da API
└── vercel.json   # Configuração do Vercel
```

## Configuração

Antes de fazer o deploy, edite o arquivo `config.js` e substitua a URL da API:

```javascript
window.API_BASE = isLocal 
    ? 'http://localhost:8000' 
    : 'https://SEU-BACKEND.up.railway.app';  // Substituir pela URL real
```

## Desenvolvimento Local

Abra o arquivo `index.html` diretamente no navegador ou use um servidor local:

```bash
# Usando Python
python -m http.server 3000

# Usando Node.js
npx serve .
```

Acesse `http://localhost:3000`

## Deploy no Vercel

### Opção 1: Via CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer deploy
vercel
```

### Opção 2: Via GitHub

1. Faça push do código para o GitHub
2. Importe o projeto no Vercel
3. Configure o diretório raiz como `frontend`
4. O Vercel detectará automaticamente o `vercel.json`

### Opção 3: Via Dashboard do Vercel

1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Selecione o repositório
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)
5. Clique em "Deploy"

## Após o Deploy

1. Anote a URL do frontend no Vercel (ex: `https://seu-projeto.vercel.app`)
2. Configure o CORS no backend Railway com essa URL
3. Atualize o `config.js` com a URL do backend Railway

## Funcionalidades

- ✅ Visualização de projetos em cards
- ✅ Mapa interativo com marcadores
- ✅ Busca e filtros
- ✅ Detalhes completos de cada projeto
- ✅ Visualização de serviços e acompanhamentos
- ✅ Design responsivo
