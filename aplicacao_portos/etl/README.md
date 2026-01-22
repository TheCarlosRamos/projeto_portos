# Scripts ETL

Scripts para processar planilhas Excel e importar dados para o banco de dados.

## Uso

```bash
# Instalar dependências
pip install -r requirements.txt

# Processar planilha
python process_excel.py planilha.xlsx
```

## Funcionalidades

- Leitura de múltiplas abas (por ano)
- Normalização automática de colunas
- Normalização de valores de situação
- Criação automática de processos, metas e indicadores
- Tratamento de erros e duplicatas
