FROM python:3.11-slim

WORKDIR /app

# Copia requirements primeiro para cache do Docker
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY app/ .

# Expõe a porta
EXPOSE 8080

# Comando para iniciar (já está em /app)
CMD ["python", "api.py"]
