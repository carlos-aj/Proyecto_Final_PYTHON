from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import init_db
from app.routes.movimientos import router as movimientos_router
from app.routes.estadisticas import router as estadisticas_router
from app.routes.json_io import router as json_router
from app.routes.presupuestos import router as presupuestos_router
from app.routes.objetivos import router as objetivos_router
from app.routes.categorias import router as categorias_router
from app.routes.recurrentes import router as recurrentes_router

app = FastAPI(
    title="Gestor de Gastos Personales",
    description="API REST para gestionar ingresos y gastos personales.",
    version="1.0.0",
)

# CORS — permite peticiones desde el frontend Vue.js en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# Routers
app.include_router(movimientos_router)
app.include_router(estadisticas_router)
app.include_router(json_router)
app.include_router(presupuestos_router)
app.include_router(objetivos_router)
app.include_router(categorias_router)
app.include_router(recurrentes_router)


@app.get("/", tags=["root"])
def root():
    return {"mensaje": "API Gestor de Gastos funcionando correctamente."}
