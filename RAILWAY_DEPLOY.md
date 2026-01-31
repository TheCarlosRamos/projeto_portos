# 🚀 Guia de Deploy no Railway

## Pré-requisitos
- Conta no Railway (https://railway.app)
- Git instalado
- Projeto Git configurado

## Passos para Deploy

### 1. Inicializar/Configurar Git (se ainda não estiver)
```bash
cd projeto_portos
git init
git add .
git commit -m "Initial commit"
```

### 2. Conectar ao Railway

#### Opção A: Via Dashboard (Recomendado)
1. Acesse https://railway.app
2. Faça login com GitHub
3. Clique em **"New Project"**
4. Selecione **"Deploy from GitHub"**
5. Escolha seu repositório
6. Clique em **"Deploy"**

#### Opção B: Via CLI Railway
```bash
# Instale o CLI do Railway (se não tiver)
npm install -g @railway/cli

# Faça login
railway login

# Crie um novo projeto
railway init

# Deploy
railway up
```

### 3. Configurar Variáveis de Ambiente no Railway
1. Vá para o painel do projeto
2. Clique em **"Variables"**
3. Adicione (se necessário):
   - `PORT` = `8080` (já está no railway.toml)
   - Outras variáveis conforme sua aplicação

### 4. Verificar Logs e Status
```bash
railway logs
```

## Estrutura do Deploy
- **railway.toml**: Configuração do Railway
- **Dockerfile**: Instrui como construir a imagem
- **Procfile**: Define o comando de inicialização
- **requirements.txt**: Dependências Python

## Verificação pós-deploy
- URL da aplicação aparecerá no dashboard do Railway
- Teste: `GET https://seu-app.railway.app/api/health`
- Deve retornar: `{"status": "healthy", "service": "API Portuária", "version": "1.0.0"}`

## Troubleshooting
- **Erro de porta**: Certifique-se que `PORT` é lido de variáveis de ambiente
- **Dependências faltando**: Verifique `requirements.txt`
- **Erro no build**: Verifique logs no dashboard do Railway
- **Banco de dados**: O arquivo `portos.db` será mantido no container

---
**Sua aplicação está pronta para o Railway! 🎉**
