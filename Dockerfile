FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia toda a estrutura de app
COPY app/ .

# Expõe a porta
EXPOSE 8080

# Comando para iniciar com gunicorn apontando para api.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "120", "api:app"]
