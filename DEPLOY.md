# Deploy: Vercel + Railway (present_tela)

Este guia cobre o deploy do **present_tela** (portos.html, cadastro, planilhas), que funciona localmente com o Flask em `app/present_tela/`.

- **Vercel** → frontend estático (portos.html, cadastro.html, planilhas.html)
- **Railway** → API Flask do present_tela (`/api/projects`, `/api/upload`, etc.)

---

## 1. Pré-requisitos

- Conta no [Vercel](https://vercel.com) e no [Railway](https://railway.app)
- Repositório **Git** do projeto (GitHub, GitLab ou Bitbucket)

---

## 2. Deploy da API (present_tela) no Railway

### 2.1 Projeto e serviço

1. Acesse [railway.app](https://railway.app) e faça login.
2. **New Project** → **Deploy from GitHub repo** → escolha o repositório do projeto.
3. Clique no serviço criado.

### 2.2 Configuração

Na aba **Settings**:

- **Root Directory:** `app/present_tela`
- **Build Command:** `pip install -r requirements.txt` (ou deixe o Railway detectar)
- **Start Command:** deixe vazio para usar o **Procfile** (`gunicorn -w 1 -b 0.0.0.0:$PORT app:app`)

### 2.3 Variáveis de ambiente

Em **Variables**:

| Variável       | Valor                          |
|----------------|--------------------------------|
| `CORS_ORIGINS` | `https://sua-url.vercel.app`   |

Use a URL **exata** do frontend na Vercel (sem barra no final). Se tiver mais de uma (ex.: preview), separe por vírgula.

### 2.4 Domínio

- **Settings** → **Networking** → **Generate Domain**.
- Anote a URL (ex.: `https://projetoportos-production.up.railway.app`).

### 2.5 API e banco

A API expõe rotas como:

- `GET /` → JSON com links
- `GET /api/projects` → lista de projetos
- `GET /api/project/<id>` → detalhe do projeto
- `POST /api/projects` → criar projeto
- `PUT /api/projects/<id>` → atualizar projeto
- `POST /api/upload` → upload de planilha
- etc.

O **SQLite** (`portos.db`) no Railway é **efêmero**: os dados podem ser perdidos em redeploys. Para persistência, use PostgreSQL e adapte o código.

---

## 3. Deploy do frontend (present_tela) na Vercel

### 3.1 Conectar o repositório

1. Acesse [vercel.com](https://vercel.com) e faça login.
2. **Add New** → **Project** → importe o repositório do projeto.
3. Em **Root Directory**, defina: **`app/present_tela`**.

### 3.2 Build

- **Framework Preset:** Other (ou None).
- **Build Command:** vazio.
- **Output Directory:** vazio.

O `vercel.json` em `app/present_tela` define os **rewrites**:

- `/` → `portos.html`
- `/cadastro` → `cadastro.html`
- `/planilhas` → `planilhas.html`

### 3.3 Deploy

1. Clique em **Deploy**.
2. Anote a URL (ex.: `https://projeto-portos-xxx.vercel.app`).
3. Use essa URL em `CORS_ORIGINS` no Railway (secção 2.3).

---

## 4. config.js e API_BASE

O frontend usa `config.js` para saber de onde chamar a API:

- **localhost:** `API_BASE = ''` (mesma origem, Flask local).
- **Vercel (produção):** `API_BASE = 'https://projetoportos-production.up.railway.app'` (ou a URL do seu projeto no Railway).

Se a URL da API no Railway for outra, edite `app/present_tela/config.js` e altere o valor de `window.API_BASE` para essa URL.

---

## 5. Resumo

| Onde    | Ação |
|---------|------|
| Railway | Root = `app/present_tela`, build/start via `requirements.txt` + Procfile. Variável `CORS_ORIGINS` = URL do frontend na Vercel. Gerar domínio. |
| Vercel  | Root = `app/present_tela`, deploy estático. Rewrites em `vercel.json` para `/`, `/cadastro`, `/planilhas`. |
| config.js | Conferir `API_BASE` com a URL da API no Railway. |

---

## 6. Testar

**API (Railway):**

```bash
curl https://projetoportos-production.up.railway.app/
curl https://projetoportos-production.up.railway.app/api/projects
```

**Frontend (Vercel):** abra a URL do deploy. O dashboard (portos), cadastro e planilhas devem carregar e falar com a API no Railway.

---

## 7. Rodar localmente (present_tela)

Na pasta `app/present_tela`:

```bash
pip install -r requirements.txt
python app.py
```

Depois acesse `http://localhost:5000`. O `config.js` usa `API_BASE = ''` em localhost, então as requisições vão para o Flask local.
