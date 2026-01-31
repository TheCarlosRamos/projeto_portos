# 🚀 Guia Completo de Deploy - Sistema de Gestão Portuária

Este guia explica como fazer o deploy completo da aplicação no Railway (backend) e Vercel (frontend).

## 📋 Pré-requisitos

- Conta no [Railway](https://railway.app)
- Conta no [Vercel](https://vercel.com)
- Repositório Git (GitHub, GitLab ou Bitbucket)

## 🎯 Visão Geral da Arquitetura

```
Frontend (Vercel)  →  Backend (Railway)  →  SQLite Database
   HTML/JS/CSS          FastAPI              (Railway Volume)
```

## 📦 Parte 1: Deploy do Backend no Railway

### Passo 1: Preparar o Código

1. Certifique-se de que todos os arquivos do backend estão na pasta `backend/`
2. Verifique se o `railway.json` está presente
3. Commit e push para o GitHub:

```bash
git add .
git commit -m "Preparar backend para deploy"
git push origin main
```

### Passo 2: Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha seu repositório
5. Configure:
   - **Root Directory**: `backend`
   - Railway detectará automaticamente o `railway.json`

### Passo 3: Configurar Variáveis de Ambiente

No painel do Railway, vá em "Variables" e adicione:

```
PORT=8000
CORS_ORIGINS=https://seu-frontend.vercel.app
DATABASE_URL=sqlite:///./portos.db
```

**Importante**: Você atualizará `CORS_ORIGINS` depois que o frontend estiver no ar.

### Passo 4: Deploy

1. Railway iniciará o deploy automaticamente
2. Aguarde a conclusão (pode levar 2-5 minutos)
3. Clique em "Settings" → "Generate Domain" para obter a URL pública
4. Anote a URL (ex: `https://seu-backend.up.railway.app`)

### Passo 5: Inicializar o Banco de Dados

Após o primeiro deploy, você precisa popular o banco com os dados do JSON:

**Opção A: Via Railway CLI**
```bash
railway login
railway link
railway run python init_db.py
```

**Opção B: Adicionar ao startCommand (temporário)**

Edite `railway.json`:
```json
{
  "deploy": {
    "startCommand": "python init_db.py && python main.py"
  }
}
```

Após o primeiro deploy bem-sucedido, remova o `init_db.py &&` do comando.

### Passo 6: Testar a API

Acesse no navegador:
- `https://seu-backend.up.railway.app/` - Deve retornar informações da API
- `https://seu-backend.up.railway.app/health` - Deve retornar `{"status": "healthy"}`
- `https://seu-backend.up.railway.app/docs` - Documentação Swagger

## 🌐 Parte 2: Deploy do Frontend no Vercel

### Passo 1: Configurar a URL da API

Edite `frontend/config.js` e substitua a URL do backend:

```javascript
window.API_BASE = isLocal 
    ? 'http://localhost:8000' 
    : 'https://SEU-BACKEND.up.railway.app';  // ← Cole a URL do Railway aqui
```

Commit as alterações:
```bash
git add frontend/config.js
git commit -m "Configurar URL da API do Railway"
git push origin main
```

### Passo 2: Deploy no Vercel

**Opção A: Via Dashboard**

1. Acesse [vercel.com](https://vercel.com)
2. Clique em "New Project"
3. Importe seu repositório do GitHub
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)
5. Clique em "Deploy"

**Opção B: Via CLI**

```bash
cd frontend
npm i -g vercel
vercel
```

### Passo 3: Anotar URL do Frontend

Após o deploy, anote a URL do Vercel (ex: `https://seu-projeto.vercel.app`)

### Passo 4: Atualizar CORS no Backend

Volte ao Railway e atualize a variável `CORS_ORIGINS`:

```
CORS_ORIGINS=https://seu-projeto.vercel.app,https://seu-projeto-*.vercel.app
```

O Railway fará redeploy automaticamente.

## ✅ Verificação Final

### Checklist de Testes

- [ ] Backend responde em `/health`
- [ ] Backend retorna projetos em `/api/projects`
- [ ] Frontend carrega sem erros no console
- [ ] Frontend exibe os projetos corretamente
- [ ] Mapa carrega e mostra marcadores
- [ ] Modal de detalhes funciona
- [ ] Busca funciona corretamente

### Testar CORS

Abra o console do navegador (F12) no frontend e verifique:
- ✅ Sem erros de CORS
- ✅ Requisições para a API são bem-sucedidas

## 🔧 Solução de Problemas

### Erro: "Failed to fetch" no Frontend

**Causa**: CORS não configurado ou URL da API incorreta

**Solução**:
1. Verifique se `config.js` tem a URL correta do Railway
2. Verifique se `CORS_ORIGINS` no Railway inclui a URL do Vercel
3. Aguarde alguns minutos para o Railway atualizar

### Erro: "404 Not Found" na API

**Causa**: Rota não existe ou backend não está rodando

**Solução**:
1. Verifique os logs no Railway
2. Teste a URL base: `https://seu-backend.up.railway.app/`
3. Verifique se o deploy foi bem-sucedido

### Banco de Dados Vazio

**Causa**: `init_db.py` não foi executado

**Solução**:
```bash
railway run python init_db.py
```

### Frontend não atualiza após mudanças

**Causa**: Cache do Vercel

**Solução**:
1. Force redeploy no Vercel
2. Limpe o cache do navegador (Ctrl+Shift+R)

## 📊 Monitoramento

### Railway (Backend)
- **Logs**: Clique em "Deployments" → Selecione o deploy → "View Logs"
- **Métricas**: Veja CPU, memória e rede em tempo real
- **Alertas**: Configure notificações para falhas

### Vercel (Frontend)
- **Analytics**: Veja visitantes e performance
- **Logs**: Clique no deployment → "Function Logs"
- **Speed Insights**: Monitore a velocidade da página

## 🔄 Atualizações Futuras

Para atualizar a aplicação:

1. Faça as alterações no código
2. Commit e push para o GitHub
3. Railway e Vercel farão deploy automaticamente

```bash
git add .
git commit -m "Descrição das alterações"
git push origin main
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs no Railway e Vercel
2. Revise este guia
3. Consulte a documentação:
   - [Railway Docs](https://docs.railway.app)
   - [Vercel Docs](https://vercel.com/docs)
   - [FastAPI Docs](https://fastapi.tiangolo.com)

## 🎉 Pronto!

Sua aplicação está no ar! 🚀

- **Frontend**: https://seu-projeto.vercel.app
- **Backend**: https://seu-backend.up.railway.app
- **API Docs**: https://seu-backend.up.railway.app/docs
