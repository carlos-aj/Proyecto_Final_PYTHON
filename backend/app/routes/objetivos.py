from fastapi import APIRouter, Query
from app.schemas.objetivo import ObjetivoCreate, AportacionCreate, ObjetivoResponse
from app.services.objetivo_service import (
    service_crear_objetivo,
    service_obtener_objetivos,
    service_aportacion_objetivo,
    service_eliminar_objetivo,
)

router = APIRouter(tags=["objetivos"])


@router.get("/objetivos", response_model=list[ObjetivoResponse], tags=["objetivos"])
def obtener_objetivos(usuario_id: int = Query(..., description="ID del usuario")):
    return service_obtener_objetivos(usuario_id)


@router.post("/objetivos", response_model=ObjetivoResponse, status_code=201, tags=["objetivos"])
def crear_objetivo(datos: ObjetivoCreate):
    return service_crear_objetivo(datos)


@router.put("/objetivos/{objetivo_id}/aportacion", response_model=ObjetivoResponse, tags=["objetivos"])
def aportar_objetivo(objetivo_id: int, datos: AportacionCreate):
    return service_aportacion_objetivo(objetivo_id, datos)


@router.delete("/objetivos/{objetivo_id}", tags=["objetivos"])
def eliminar_objetivo(objetivo_id: int):
    return service_eliminar_objetivo(objetivo_id)
