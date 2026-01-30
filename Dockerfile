FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia toda a estrutura de app
COPY app/ .

# Vai para o diretório da aplicação principal
WORKDIR /app/present_tela

# Copia os módulos compartilhados (se estiverem em ../db.py, etc)
RUN cp ../db.py . 2>/dev/null || true && \
    cp ../io_utils.py . 2>/dev/null || true && \
    cp ../services.py . 2>/dev/null || true

# Expõe a porta
EXPOSE 8080

# Comando para iniciar com gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "120", "app:app"]
