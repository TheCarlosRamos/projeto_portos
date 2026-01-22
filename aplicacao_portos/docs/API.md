# Documentação da API

## Endpoints

### Processos

#### Listar Processos
```
GET /api/processos/
```

Parâmetros de query:
- `skip` (int): Número de registros para pular (padrão: 0)
- `limit` (int): Número máximo de registros (padrão: 100, máx: 1000)
- `numero_processo` (string): Filtrar por número do processo
- `situacao_id` (int): Filtrar por situação

Exemplo:
```
GET /api/processos/?numero_processo=12345&situacao_id=1
```

#### Obter Processo
```
GET /api/processos/{id}
```

#### Criar Processo
```
POST /api/processos/
```

Body:
```json
{
  "numero_processo": "12345",
  "data_protocolo": "2025-01-15",
  "licenca": "LIC123",
  "situacao_geral_id": 1
}
```

#### Atualizar Processo
```
PUT /api/processos/{id}
```

#### Deletar Processo
```
DELETE /api/processos/{id}
```

### Metas

#### Listar Metas
```
GET /api/metas/
```

Parâmetros de query:
- `skip` (int)
- `limit` (int)
- `ano` (int): Filtrar por ano
- `processo_id` (int): Filtrar por processo

#### Obter Meta
```
GET /api/metas/{id}
```

#### Criar Meta
```
POST /api/metas/
```

Body:
```json
{
  "processo_id": 1,
  "ano": 2025
}
```

#### Atualizar Meta
```
PUT /api/metas/{id}
```

#### Deletar Meta
```
DELETE /api/metas/{id}
```

### Indicadores

#### Listar Indicadores
```
GET /api/indicadores/
```

Parâmetros de query:
- `skip` (int)
- `limit` (int)
- `meta_id` (int): Filtrar por meta
- `tipo_intervencao` (string): Filtrar por tipo

#### Obter Indicador
```
GET /api/indicadores/{id}
```

#### Criar Indicador
```
POST /api/indicadores/
```

Body:
```json
{
  "meta_id": 1,
  "tipo_intervencao": "Pavimentação",
  "financeiro_planejado": 1000000.00,
  "financeiro_executado": 500000.00,
  "km_planejado": 10.5,
  "km_executado": 5.0,
  "extensao_km": 10.5
}
```

#### Atualizar Indicador
```
PUT /api/indicadores/{id}
```

#### Deletar Indicador
```
DELETE /api/indicadores/{id}
```

### Situações

#### Listar Situações
```
GET /api/situacoes/
```

#### Obter Situação
```
GET /api/situacoes/{id}
```

#### Criar Situação
```
POST /api/situacoes/
```

Body:
```json
{
  "nome": "EM EXECUÇÃO"
}
```

#### Deletar Situação
```
DELETE /api/situacoes/{id}
```

## Códigos de Status

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `204 No Content`: Recurso deletado com sucesso
- `400 Bad Request`: Erro de validação
- `404 Not Found`: Recurso não encontrado

## Exemplos com curl

### Criar Processo
```bash
curl -X POST http://localhost:8000/api/processos/ \
  -H "Content-Type: application/json" \
  -d '{
    "numero_processo": "PROC001",
    "data_protocolo": "2025-01-15",
    "licenca": "LIC123"
  }'
```

### Listar Metas de 2025
```bash
curl http://localhost:8000/api/metas/?ano=2025
```
