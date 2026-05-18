from fastapi import APIRouter, Query, HTTPException
from app.schemas.recurrente import RecurrenteCreate, RecurrenteUpdate, RecurrenteResponse
from app.services.recurrente_service import (
    service_obtener_recurrentes,
    service_crear_recurrente,
    service_editar_recurrente,
    service_eliminar_recurrente,
)

router = APIRouter()


@router.get("/recurrentes", response_model=list[RecurrenteResponse], tags=["recurrentes"])
def obtener_recurrentes(usuario_id: int = Query(...)):
    """Devuelve los recurrentes del usuario y genera los movimientos pendientes."""
    return service_obtener_recurrentes(usuario_id)


@router.post("/recurrentes", response_model=RecurrenteResponse, status_code=201, tags=["recurrentes"])
def crear_recurrente(datos: RecurrenteCreate):
    """Crea un nuevo recurrente."""
    return service_crear_recurrente(datos)


@router.put("/recurrentes/{recurrente_id}", response_model=RecurrenteResponse, tags=["recurrentes"])
def editar_recurrente(recurrente_id: int, datos: RecurrenteUpdate):
    """Edita un recurrente existente."""
    result = service_editar_recurrente(recurrente_id, datos)
    if not result:
        raise HTTPException(status_code=404, detail="Recurrente no encontrado.")
    return result


@router.delete("/recurrentes/{recurrente_id}", status_code=204, tags=["recurrentes"])
def eliminar_recurrente(recurrente_id: int):
    """Elimina un recurrente. Los movimientos ya generados no se borran."""
    eliminado = service_eliminar_recurrente(recurrente_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Recurrente no encontrado.")
