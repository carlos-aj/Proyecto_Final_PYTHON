from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.services.categoria_service import (
    service_obtener_categorias,
    service_crear_categoria,
    service_eliminar_categoria,
)

router = APIRouter(tags=["categorias"])


@router.get("/categorias", response_model=list[CategoriaResponse])
def obtener_categorias(
    usuario_id: int = Query(..., description="ID del usuario"),
    tipo: Optional[str] = Query(None, description="'gasto' o 'ingreso'"),
):
    return service_obtener_categorias(usuario_id, tipo)


@router.post("/categorias", response_model=CategoriaResponse, status_code=201)
def crear_categoria(datos: CategoriaCreate):
    return service_crear_categoria(datos)


@router.delete("/categorias/{categoria_id}")
def eliminar_categoria(categoria_id: int, usuario_id: int = Query(..., description="ID del usuario")):
    return service_eliminar_categoria(categoria_id, usuario_id)
