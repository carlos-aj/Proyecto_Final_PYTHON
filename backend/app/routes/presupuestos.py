from fastapi import APIRouter, Query
from app.schemas.presupuesto import PresupuestoCreate, PresupuestoResponse
from app.services.presupuesto_service import (
    service_crear_presupuesto,
    service_obtener_presupuestos,
    service_eliminar_presupuesto,
)

router = APIRouter(tags=["presupuestos"])


@router.get("/presupuestos", tags=["presupuestos"])
def obtener_presupuestos(
    usuario_id: int = Query(..., description="ID del usuario"),
    mes: str | None = Query(default=None, description="Filtrar por mes (YYYY-MM)"),
):
    return service_obtener_presupuestos(usuario_id, mes)


@router.post("/presupuestos", response_model=PresupuestoResponse, status_code=201, tags=["presupuestos"])
def crear_presupuesto(datos: PresupuestoCreate):
    return service_crear_presupuesto(datos)


@router.delete("/presupuestos/{presupuesto_id}", tags=["presupuestos"])
def eliminar_presupuesto(presupuesto_id: int):
    return service_eliminar_presupuesto(presupuesto_id)
