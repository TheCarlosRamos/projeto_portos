# Estrutura do Banco de Dados

## Diagrama ER

```
┌─────────────┐
│  SITUACAO   │
│─────────────│
│ id (PK)     │
│ nome (UK)   │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────┴──────┐
│  PROCESSO   │
│─────────────│
│ id (PK)     │
│ numero_     │
│   processo  │
│   (UK)      │
│ data_       │
│   protocolo │
│ licenca     │
│ situacao_   │
│   geral_id  │
│   (FK)      │
│ created_at  │
│ updated_at  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────┴──────┐
│    META     │
│─────────────│
│ id (PK)     │
│ processo_id │
│   (FK)      │
│ ano         │
│ created_at  │
│ updated_at  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────┴──────────┐
│   INDICADOR     │
│─────────────────│
│ id (PK)         │
│ meta_id (FK)    │
│ tipo_           │
│   intervencao   │
│ financeiro_     │
│   planejado     │
│ financeiro_     │
│   executado     │
│ km_planejado    │
│ km_executado    │
│ extensao_km     │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Tabelas

### situacao

Tabela de domínio para situações dos processos.

| Campo      | Tipo       | Constraints           |
|------------|------------|-----------------------|
| id         | SERIAL     | PRIMARY KEY           |
| nome       | VARCHAR(50)| UNIQUE, NOT NULL      |
| created_at | TIMESTAMP  | DEFAULT NOW()         |

### processo

Tabela principal de processos administrativos.

| Campo            | Tipo        | Constraints           |
|------------------|-------------|-----------------------|
| id               | SERIAL      | PRIMARY KEY           |
| numero_processo  | VARCHAR(50) | UNIQUE, NOT NULL      |
| data_protocolo   | DATE        |                       |
| licenca          | VARCHAR(100)|                       |
| situacao_geral_id| INTEGER     | FOREIGN KEY → situacao|
| created_at       | TIMESTAMP   | DEFAULT NOW()         |
| updated_at       | TIMESTAMP   | DEFAULT NOW()         |

### meta

Metas por processo e ano.

| Campo      | Tipo    | Constraints                    |
|------------|---------|--------------------------------|
| id         | SERIAL  | PRIMARY KEY                    |
| processo_id| INTEGER | FOREIGN KEY → processo, NOT NULL|
| ano        | INTEGER | NOT NULL                       |
| created_at | TIMESTAMP | DEFAULT NOW()                 |
| updated_at | TIMESTAMP | DEFAULT NOW()                 |

**Constraint Única:** (processo_id, ano)

### indicador

Indicadores físicos e financeiros das metas.

| Campo                | Tipo          | Constraints           |
|----------------------|---------------|-----------------------|
| id                   | SERIAL        | PRIMARY KEY           |
| meta_id              | INTEGER       | FOREIGN KEY → meta    |
| tipo_intervencao     | VARCHAR(50)   | NOT NULL              |
| financeiro_planejado | NUMERIC(15,2) | DEFAULT 0, >= 0       |
| financeiro_executado | NUMERIC(15,2) | DEFAULT 0, >= 0       |
| km_planejado         | NUMERIC(10,2) | DEFAULT 0, >= 0       |
| km_executado         | NUMERIC(10,2) | DEFAULT 0, >= 0       |
| extensao_km          | NUMERIC(10,2) | DEFAULT 0, >= 0       |
| created_at           | TIMESTAMP     | DEFAULT NOW()         |
| updated_at           | TIMESTAMP     | DEFAULT NOW()         |

## Regras de Negócio

1. Um processo pode ter várias metas (uma por ano)
2. Uma meta pode ter vários indicadores
3. Situação deve pertencer a um conjunto controlado
4. Valores executados não podem ser negativos
5. Ano da meta deve ser único por processo

## Índices

- `processo.numero_processo` (UNIQUE)
- `processo.situacao_geral_id` (INDEX)
- `meta.processo_id` (INDEX)
- `meta.ano` (INDEX)
- `indicador.meta_id` (INDEX)
- `indicador.tipo_intervencao` (INDEX)
