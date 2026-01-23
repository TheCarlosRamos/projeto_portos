from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import (
    processos, metas, indicadores, situacoes, etl,
    # Novas rotas portuárias
    concessoes, servicos, acompanhamentos, dominios, etl_portuarios
)
from models_portuarios import Base as BasePortuarios

# Criar tabelas
Base.metadata.create_all(bind=engine)
BasePortuarios.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Processos e Concessões Portuárias",
    description="API para gerenciamento de processos administrativos e concessões portuárias",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas antigas (manter para compatibilidade)
app.include_router(processos.router, prefix="/api/processos", tags=["Processos"])
app.include_router(metas.router, prefix="/api/metas", tags=["Metas"])
app.include_router(indicadores.router, prefix="/api/indicadores", tags=["Indicadores"])
app.include_router(situacoes.router, prefix="/api/situacoes", tags=["Situações"])
app.include_router(etl.router, prefix="/api/etl", tags=["ETL"])

# Novas rotas portuárias
app.include_router(dominios.router, prefix="/api/dominios", tags=["Domínios Portuários"])
app.include_router(concessoes.router, prefix="/api/concessoes", tags=["Concessões Portuárias"])
app.include_router(servicos.router, prefix="/api/servicos", tags=["Serviços Portuários"])
app.include_router(acompanhamentos.router, prefix="/api/acompanhamentos", tags=["Acompanhamentos Portuários"])
app.include_router(etl_portuarios.router, prefix="/api/etl", tags=["ETL Portuário"])

@app.get("/")
def root():
    return {
        "message": "Sistema de Gestão de Processos e Concessões Portuárias API",
        "version": "2.0.0",
        "modules": ["Processos Administrativos", "Concessões Portuárias"]
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
