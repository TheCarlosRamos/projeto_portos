# ✅ Checklist de Deploy - Passo a Passo

Use este checklist para garantir que tudo seja configurado corretamente.

## 📦 ANTES DE COMEÇAR

### ☐ 1. Preparar o Repositório Git

```bash
# Na pasta projeto_portos/
git add .
git commit -m "Estrutura completa backend + frontend"
git push origin main
```

**Importante**: Certifique-se de que o código está no GitHub, GitLab ou Bitbucket.

---

## 🚂 PARTE 1: RAILWAY (Backend)

### ☐ 2. Criar Conta no Railway
- Acesse: https://railway.app
- Faça login com GitHub

### ☐ 3. Criar Novo Projeto
1. Clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório **projeto_portos**
4. ⚠️ **IMPORTANTE**: Configure **Root Directory** = `backend`
   - Clique em **"Settings"** (ícone de engrenagem)
   - Em **"Service"** → **"Root Directory"** → Digite: `backend`
   - Clique em **"Update"**

### ☐ 4. Aguardar Primeiro Deploy
- Railway começará a fazer o build automaticamente
- Aguarde 2-5 minutos
- Verifique se o status está **"Active"** (verde)

### ☐ 5. Gerar Domínio Público
1. Vá em **"Settings"**
2. Role até **"Networking"**
3. Clique em **"Generate Domain"**
4. **📝 ANOTE A URL**: `https://seu-projeto-production.up.railway.app`

### ☐ 6. Configurar Variáveis de Ambiente
1. Clique na aba **"Variables"**
2. Adicione as seguintes variáveis:

```
PORT=8000
DATABASE_URL=sqlite:///./portos.db
CORS_ORIGINS=*
```

**Nota**: Você atualizará `CORS_ORIGINS` depois com a URL do Vercel.

### ☐ 7. Inicializar o Banco de Dados

**Opção A: Via Railway CLI (Recomendado)**

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Fazer login
railway login

# Conectar ao projeto
railway link

# Executar script de inicialização
railway run python init_db.py
```

**Opção B: Via Comando de Start (Temporário)**

1. Vá em **"Settings"** → **"Deploy"**
2. Em **"Custom Start Command"**, adicione:
   ```
   python init_db.py && python main.py
   ```
3. Clique em **"Deploy"** para forçar novo deploy
4. Após o deploy bem-sucedido, **REMOVA** o `python init_db.py &&` e deixe apenas:
   ```
   python main.py
   ```

### ☐ 8. Testar a API

Abra no navegador (substitua pela sua URL):

- ✅ `https://seu-projeto.up.railway.app/` → Deve mostrar informações da API
- ✅ `https://seu-projeto.up.railway.app/health` → Deve retornar `{"status": "healthy"}`
- ✅ `https://seu-projeto.up.railway.app/api/projects` → Deve retornar lista de projetos
- ✅ `https://seu-projeto.up.railway.app/docs` → Documentação Swagger

**Se algum teste falhar:**
- Verifique os logs: **"Deployments"** → Último deploy → **"View Logs"**
- Certifique-se de que executou o `init_db.py`

---

## 🌐 PARTE 2: VERCEL (Frontend)

### ☐ 9. Atualizar URL da API no Frontend

**ANTES de fazer deploy no Vercel**, edite o arquivo:

`frontend/config.js`

```javascript
window.API_BASE = isLocal 
    ? 'http://localhost:8000' 
    : 'https://SEU-PROJETO.up.railway.app';  // ← Cole a URL do Railway aqui
```

**Commit a mudança:**
```bash
git add frontend/config.js
git commit -m "Configurar URL da API do Railway"
git push origin main
```

### ☐ 10. Criar Conta no Vercel
- Acesse: https://vercel.com
- Faça login com GitHub

### ☐ 11. Criar Novo Projeto
1. Clique em **"Add New..."** → **"Project"**
2. Clique em **"Import"** no repositório **projeto_portos**
3. ⚠️ **IMPORTANTE**: Configure:
   - **Framework Preset**: `Other`
   - **Root Directory**: Clique em **"Edit"** → Digite: `frontend`
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)
   - **Install Command**: (deixe vazio)
4. Clique em **"Deploy"**

### ☐ 12. Aguardar Deploy
- Vercel fará o deploy automaticamente
- Aguarde 1-2 minutos
- Deve mostrar **"Congratulations!"** quando concluir

### ☐ 13. Anotar URL do Frontend
- **📝 ANOTE A URL**: `https://seu-projeto.vercel.app`
- Clique em **"Visit"** para abrir o site

### ☐ 14. Testar o Frontend

No navegador:
- ✅ Página carrega sem erros
- ✅ Abra o Console (F12) → Não deve ter erros de CORS
- ✅ Os projetos aparecem nos cards
- ✅ O mapa carrega
- ✅ Ao clicar em um projeto, o modal abre

**Se houver erro de CORS:**
- Continue para o próximo passo

---

## 🔗 PARTE 3: CONECTAR FRONTEND E BACKEND

### ☐ 15. Atualizar CORS no Railway

1. Volte ao projeto no **Railway**
2. Clique na aba **"Variables"**
3. Edite a variável `CORS_ORIGINS`:

```
CORS_ORIGINS=https://seu-projeto.vercel.app,https://seu-projeto-*.vercel.app
```

**Importante**: Substitua `seu-projeto` pela URL real do Vercel.

4. Railway fará **redeploy automaticamente**
5. Aguarde 1-2 minutos

### ☐ 16. Testar Novamente

1. Abra o frontend no Vercel
2. Pressione **Ctrl+Shift+R** (limpar cache)
3. Abra o Console (F12)
4. Recarregue a página
5. ✅ Não deve haver erros de CORS
6. ✅ Os projetos devem aparecer

---

## ✅ VERIFICAÇÃO FINAL

### ☐ 17. Checklist de Funcionalidades

Teste todas as funcionalidades:

- [ ] Dashboard carrega
- [ ] Cards de projetos aparecem
- [ ] Mapa mostra marcadores
- [ ] Busca funciona
- [ ] Clicar em "Ver Detalhes" abre o modal
- [ ] Modal mostra informações completas
- [ ] Serviços aparecem no modal
- [ ] Fechar modal funciona

### ☐ 18. Verificar Logs

**Railway:**
- Vá em **"Deployments"** → Último deploy → **"View Logs"**
- ✅ Não deve ter erros críticos

**Vercel:**
- Vá em **"Deployments"** → Último deploy
- ✅ Status deve estar **"Ready"**

---

## 🎉 PRONTO!

Se todos os itens estão marcados, sua aplicação está funcionando perfeitamente!

### 📝 URLs Finais

Anote suas URLs:

- **Frontend**: `https://_____________________.vercel.app`
- **Backend**: `https://_____________________.up.railway.app`
- **API Docs**: `https://_____________________.up.railway.app/docs`

---

## 🆘 PROBLEMAS COMUNS

### ❌ Erro: "Failed to fetch" no Frontend

**Causa**: URL da API incorreta ou CORS não configurado

**Solução**:
1. Verifique `frontend/config.js` → URL está correta?
2. Verifique `CORS_ORIGINS` no Railway → Inclui a URL do Vercel?
3. Aguarde 2-3 minutos para o Railway atualizar
4. Limpe o cache do navegador (Ctrl+Shift+R)

### ❌ Erro: "Application failed to respond" no Railway

**Causa**: Erro no código ou dependências não instaladas

**Solução**:
1. Veja os logs no Railway
2. Verifique se `requirements.txt` está correto
3. Certifique-se de que `Root Directory` está como `backend`

### ❌ Projetos não aparecem no Frontend

**Causa**: Banco de dados não foi inicializado

**Solução**:
```bash
railway run python init_db.py
```

### ❌ Erro 404 no Vercel

**Causa**: Root Directory não configurado

**Solução**:
1. Vá em **"Settings"** → **"General"**
2. Em **"Root Directory"**, defina: `frontend`
3. Clique em **"Save"**
4. Vá em **"Deployments"** → Último deploy → **"Redeploy"**

---

## 📞 Precisa de Ajuda?

1. Verifique os logs (Railway e Vercel)
2. Revise este checklist
3. Consulte o `GUIA_DEPLOY.md` para mais detalhes
4. Teste as URLs manualmente no navegador

---

## 🔄 Atualizações Futuras

Para atualizar a aplicação no futuro:

```bash
# Faça suas alterações no código
git add .
git commit -m "Descrição das alterações"
git push origin main
```

✅ Railway e Vercel farão **deploy automaticamente**!
