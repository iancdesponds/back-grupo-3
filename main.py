from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api.endpoints.router import include_routes

app = FastAPI()

# Incluindo todas as rotas ao app
include_routes(app)

# Permitir acesso ao frontend (React) rodando na porta 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://front-grupo-3-6gxf.vercel.app/"],  # URL do React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
