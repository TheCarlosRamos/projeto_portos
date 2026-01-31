from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import projects, services, monitoring
import os

# Cria tabelas no banco de dados (apenas se não existirem)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Nota: {e}")

app = FastAPI(
    title="Sistema de Gestão de Concessões Portuárias",
    description="Sistema completo para gestão e acompanhamento de concessões portuárias",
    version="1.0.0"
)

# Configuração do CORS
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    cors_origins = cors_origins_env.split(",")
else:
    # Em desenvolvimento permite todas, em produção configure CORS_ORIGINS
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Registra rotas
app.include_router(projects.router)
app.include_router(services.router)
app.include_router(monitoring.router)

@app.get("/")
def root():
    # Inicializar banco na primeira requisição (para Vercel)
    try:
        from app.database import SessionLocal
        from app.init_data import init_from_json
        db = SessionLocal()
        init_from_json(db)
        db.close()
    except Exception as e:
        print(f"Nota ao inicializar: {e}")
    
    return {
        "message": "Sistema de Gestão de Concessões Portuárias API",
        "version": "1.0.0",
        "endpoints": {
            "projects": "/api/projects",
            "services": "/api/servicos",
            "monitoring": "/api/acompanhamento"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Para desenvolvimento local
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Para Vercel Serverless
app = app
