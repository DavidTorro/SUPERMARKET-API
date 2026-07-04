"""
Punto de entrada de la aplicación
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router
from app.core.database import init_db

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# asynccontextmanager para inicializar la base de datos al arrancar la app
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # crea las tablas si no existen
    yield  # aquí la app queda sirviendo peticiones


app = FastAPI(
    title="Supermarket API",
    version="1.0.0",
    description=(
        "Complete product catalog (name, description, current estimated "
        "price and photo) from Mercadona, Consum and Masymas."
    ),
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/", tags=["health"])
def root() -> dict:
    return {
        "app": "Supermarket API",
        "docs": "/docs",
    }
