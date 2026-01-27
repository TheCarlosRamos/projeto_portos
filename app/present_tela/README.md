# Sistema de Gestão de Concessões Portuárias

Aplicação completa que integra banco de dados SQLite, API Flask e frontend HTML para gestão de projetos de concessões portuárias.

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Flask     │    │  Banco SQLite   │
│   (HTML/JS)     │◄──►│   (Python)      │◄──►│   (Dados)       │
│                 │    │                 │    │                 │
│ • Maps          │    │ • CRUD APIs     │    │ • Projetos      │
│ • Dashboard     │    │ • Data Import   │    │ • Serviços      │
│ • Search        │    │ • JSON Export   │    │ • Acompanhamento│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar Aplicação
```bash
python start.py
```

### 3. Acessar
- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/api/projects
- **Importação**: http://localhost:5000/api/import (POST)

## 📁 Estrutura de Arquivos

```
├── app.py                 # API Flask principal
├── start.py              # Script de inicialização
├── requirements.txt      # Dependências Python
├── portos.html          # Frontend HTML/JavaScript
├── planilha_portos.json  # Dados de exemplo
├── portos.db            # Banco SQLite (criado automaticamente)
└── README.md            # Este arquivo
```

## 🗄️ Banco de Dados

### Tabelas Principais

#### `projetos`
- Cadastro principal de projetos
- Coordenadas (UTM e Lat/Lon)
- Informações básicas e CAPEX

#### `servicos`
- Serviços por projeto
- Fases e prazos
- Orçamentos por serviço

#### `acompanhamento`
- Progresso das obras
- Atualizações de status
- Riscos e responsáveis

## 🔌 API Endpoints

### GET `/api/projects`
Retorna todos os projetos com dados completos.

**Response:**
```json
[
  {
    "id": "projeto-1",
    "nome": "Porto Organizado de Santos - TECON 10",
    "zona": "Porto Organizado de Santos",
    "uf": "SP",
    "tipo": "Arrendamento",
    "capexTotal": 6454903000,
    "descricao": "Terminal destinado à movimentação...",
    "progresso": 0,
    "etapa": "Planejamento",
    "coordenadasLatLon": {"lat": -23.926132, "lon": -46.34027},
    "mapaEmbed": "<iframe>...</iframe>",
    "servicos": [...],
    "acompanhamentos": [...]
  }
]
```

### POST `/api/import`
Importa dados do `planilha_portos.json` para o banco.

### PUT `/api/projects/<id>`
Atualiza dados de um projeto específico.

### POST `/api/servicos`
Cria novo serviço para um projeto.

### POST `/api/acompanhamento`
Adiciona acompanhamento a um projeto.

## 🌐 Frontend Features

### 📍 Mapas Interativos
- Suporte duplo: Lat/Lon direto ou UTM
- OpenStreetMap integration
- Coordenadas precisas com 6 casas decimais

### 📊 Dashboard
- Cards de projetos com progresso
- Filtros por busca
- Modal com detalhes completos

### 🔄 Atualização em Tempo Real
- Botão "Recarregar Dados"
- Cache-busting automático
- Fallback para JSON estático

## 📝 Scripts Python Disponíveis

### `excel_to_json.py`
Converte planilhas Excel para JSON:
```bash
python excel_to_json.py planilha.xlsx -o dados.json
```

### `excel_to_json2.py`
Conversão avançada com estrutura aninhada:
```bash
python excel_to_json2.py "Planilha portos.xlsx"
```

## 🛠️ Desenvolvimento

### Modo Debug
```bash
python app.py
```

### Logs da Aplicação
- Console do navegador: F12 → Network/Console
- Logs do servidor: Terminal Python

### Testes
```bash
# Testar API
curl http://localhost:5000/api/projects

# Testar importação
curl -X POST http://localhost:5000/api/import
```

## 🔄 Fluxo de Dados

1. **Importação**: Excel → JSON → Banco SQLite
2. **API**: Banco → JSON → Frontend
3. **Frontend**: JSON → Maps + Dashboard
4. **Atualizações**: Frontend → API → Banco

## 📊 Formatos Suportados

### Coordenadas
- **Latitude/Longitude**: `-23.926132, -46.34027`
- **UTM**: `E:363506.31, S:7353284.66, Fuso:23`

### Dados
- **Excel**: `.xlsx` (via scripts Python)
- **JSON**: Estrutura aninhada
- **SQLite**: Banco relacional

## 🚨 Troubleshooting

### API não responde
```bash
# Verifique se o servidor está rodando
curl http://localhost:5000/api/projects
```

### Mapas não funcionam
- Verifique coordenadas no console (F12)
- Confira formato Lat/Lon ou UTM
- Teste conversão com `test_utm_conversion.html`

### Banco de dados vazio
```bash
# Importe dados do JSON
curl -X POST http://localhost:5000/api/import
```

## 📈 Próximos Passos

- [ ] Autenticação de usuários
- [ ] Upload de arquivos
- [ ] Exportação para Excel
- [ ] Dashboard analytics
- [ ] Notificações em tempo real

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do console
2. Confirme se o servidor está rodando
3. Teste os endpoints da API
4. Verifique o formato dos dados
