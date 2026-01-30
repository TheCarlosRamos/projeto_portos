# Deploy: Vercel + Railway

Este guia explica como publicar o **projeto portos** na web usando:
- **Vercel** → frontend estático (`index.html` + `data.js`)
- **Railway** → API Flask (`app/api.py`) que serve os dados dos portos

---

## 1. Pré-requisitos

- Conta no [Vercel](https://vercel.com) e no [Railway](https://railway.app)
- Projeto em um repositório **Git** (GitHub, GitLab ou Bitbucket)

---

## 2. Deploy do frontend na Vercel

### 2.1 Conectar o repositório

1. Acesse [vercel.com](https://vercel.com) e faça login.
2. Clique em **Add New** → **Project**.
3. Importe o repositório do `projeto_portos`.
4. Em **Root Directory**, deixe `.` (raiz do projeto).

### 2.2 Configuração do build

- **Framework Preset:** Other (ou “None”).
- **Build Command:** deixe vazio (o site é estático).
- **Output Directory:** deixe vazio ou `.`.
- **Install Command:** deixe vazio.

O `vercel.json` na raiz já está configurado para deploy estático.

### 2.3 Deploy

1. Clique em **Deploy**.
2. Após o deploy, você receberá uma URL como:  
   `https://projeto-portos-xxxx.vercel.app`

Guarde essa URL; você usará como origem CORS na API (Railway).

---

## 3. Deploy da API no Railway

### 3.1 Novo projeto

1. Acesse [railway.app](https://railway.app) e faça login.
2. **New Project** → **Deploy from GitHub repo**.
3. Selecione o repositório `projeto_portos`.

### 3.2 Configurar o serviço

1. Clique no serviço criado.
2. Aba **Settings**:
   - **Root Directory:** `app`  
     (tudo será executado a partir da pasta `app`).
   - **Build Command:**  
     `pip install -r requirements.txt`
   - **Start Command:**  
     `gunicorn -w 1 -b 0.0.0.0:$PORT api:app`  
     Ou use o **Procfile**: Railway detecta o `Procfile` em `app/` se o root for `app`.

Se estiver usando o **Procfile** em `app/`:
- **Start Command** pode ficar vazio; o Railway usará o Procfile.

### 3.3 Variáveis de ambiente

Na aba **Variables** do serviço, adicione:

| Variável       | Valor                         | Obrigatório |
|----------------|-------------------------------|-------------|
| `CORS_ORIGINS` | `https://sua-url.vercel.app`  | Sim*        |

\* Use a URL exata do app na Vercel (com `https://`). Se tiver mais de uma (ex.: preview), separe por vírgula:  
`https://app.vercel.app,https://outro-dominio.vercel.app`

### 3.4 Domínio público

1. Aba **Settings** → **Networking** → **Generate Domain**.
2. Anote a URL (ex.: `https://projeto-portos-api.up.railway.app`).

### 3.5 Banco SQLite (importante)

A API usa **SQLite** (`app/portos.db`). No Railway o disco é **efêmero**: em cada redeploy o sistema pode ser recriado e o arquivo do banco **será perdido**.

Opções:

- **Uso só de demonstração:** pode manter SQLite e aceitar que os dados são resetados a cada deploy.
- **Dados persistentes:** use **PostgreSQL** no Railway e altere a API para usar Postgres em vez de SQLite (requer mudanças em `db.py` e possivelmente migração dos dados).

---

## 4. Ligar frontend (Vercel) à API (Railway)

O `index.html` e o `data.js` atuais usam dados **fixos** em `data.js`. Eles **não** chamam a API.

Para o frontend passar a usar a API do Railway:

1. Defina a URL base da API (ex.: variável de ambiente na Vercel ou constante no código).
2. Substitua o uso de `dadosPortos` por chamadas `fetch` para:
   - `https://sua-api.railway.app/api/portos`
   - `https://sua-api.railway.app/api/portos/<id>`
   - `https://sua-api.railway.app/api/portos/summary`
3. Configure `CORS_ORIGINS` no Railway com a URL do frontend na Vercel (como em **3.3**).

Enquanto o frontend continuar só com `data.js`, o deploy na Vercel já funciona; a API no Railway fica pronta para quando você fizer essa integração.

---

## 5. Resumo rápido

| Etapa | Onde    | Ação |
|-------|---------|------|
| 1     | Vercel  | Conectar repo → deploy estático (raiz do projeto). |
| 2     | Vercel  | Anotar URL do frontend. |
| 3     | Railway | Conectar mesmo repo, **Root Directory** = `app`. |
| 4     | Railway | Build: `pip install -r requirements.txt`, Start: `gunicorn -w 1 -b 0.0.0.0:$PORT api:app` (ou Procfile). |
| 5     | Railway | Variável `CORS_ORIGINS` = URL do frontend na Vercel. |
| 6     | Railway | Gerar domínio público e anotar URL da API. |

---

## 6. Testar a API

Após o deploy no Railway:

```bash
curl https://SUA-API.railway.app/api/portos
curl https://SUA-API.railway.app/api/portos/summary
```

Se retornar JSON, a API está no ar. Depois disso, basta apontar o frontend para essa URL quando for usar a API em vez do `data.js`.
