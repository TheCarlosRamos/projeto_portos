from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import processos, metas, indicadores, situacoes, etl

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Processos e Metas",
    description="API para gerenciamento de processos administrativos e metas",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(processos.router, prefix="/api/processos", tags=["Processos"])
app.include_router(metas.router, prefix="/api/metas", tags=["Metas"])
app.include_router(indicadores.router, prefix="/api/indicadores", tags=["Indicadores"])
app.include_router(situacoes.router, prefix="/api/situacoes", tags=["Situações"])
app.include_router(etl.router, prefix="/api/etl", tags=["ETL"])

@app.get("/")
def root():
    return {"message": "Sistema de Gestão de Processos e Metas API"}

@app.get("/api/health")
def health():
    return {"status": "ok"}
