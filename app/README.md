# Gestão de Concessões Portuárias – Docker + PostgreSQL

Este projeto sobe uma aplicação **Streamlit** com banco **PostgreSQL** via **Docker Compose** para gerenciar suas abas **Planilha/Tabela 00/01/02**.

## Subir o ambiente

1. Instale o **Docker Desktop** (ou Docker Engine + Compose).
2. No diretório do projeto, rode:
   ```bash
   docker compose up --build
   ```
3. Acesse **http://localhost:8501**.

> Banco de dados: `postgres:16`, usuário `app`, senha `app`, DB `portos`. A URL de conexão é `postgresql+psycopg2://app:app@db:5432/portos` (definida em `docker-compose.yml`).

## Fluxo de uso
- **Upload**: envie seu Excel (com abas `Tabela/Planilha 00/01/02`).
- **Importar Excel → Banco**: persiste no Postgres com validações e cálculos (datas/percentuais/Capex de serviço).
- **Carregar do Banco**: traz para a interface para edição.
- **Salvar no Banco**: valida e salva as edições de volta no Postgres (substitui o conteúdo atual por completo, com integridade referencial).
- **Exportar do Banco → Excel**: baixe o Excel montado a partir do que está no Postgres.
- **Exportar Excel (UI)**: exporta exatamente o que está nas tabelas da UI (independente do banco).

## Estrutura
- `app.py` – UI (Streamlit) com botões para Banco (carregar/salvar/importar/exportar).
- `db.py` – Esquema SQLAlchemy (tabelas `cadastro`, `servico`, `acompanhamento`) e funções de import/export.
- `services.py` – Regras de negócio (validações, normalizações, cálculos de datas e CAPEX de serviço).
- `io_utils.py` – Leitura/escrita de Excel com nomes de abas e colunas padronizados.
- `docker-compose.yml` – Orquestra Postgres e a aplicação.
- `Dockerfile` – Imagem da aplicação.
- `.env` – Exemplo de `DB_URL` (a Compose já injeta isso no container do app).
- `requirements.txt` – Dependências Python.

## Observações técnicas
- **Integridade**: chaves únicas e FKs garantem que Serviço depende de Cadastro e Acompanhamento depende de Serviço.
- **Percentuais**: armazenados normalizados (0..1). A interface aceita 0–1 ou 0–100 e normaliza antes de persistir.
- **Datas**: interpretadas no formato `DD/MM/AAAA` quando possível.
- **Salvar no Banco**: realiza limpeza e recarga (truncate lógico) na ordem correta para respeitar FKs (acompanhamento → serviço → cadastro).

## Personalizações
- Trocar Postgres por **Azure Database for PostgreSQL**: basta mudar `DB_URL`.
- Autenticação / perfis de acesso: pode-se integrar **Streamlit-Auth** ou colocar um **proxy** (Nginx + OIDC). 
- Logs/auditoria: adicionar tabelas de histórico e triggers.
