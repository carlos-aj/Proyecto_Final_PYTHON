from fastapi import APIRouter, Query
from app.services.movimiento_service import (
    service_calcular_balance,
    service_gastos_por_categoria,
)

router = APIRouter(prefix="/estadisticas", tags=["estadísticas"])


@router.get("/balance")
def balance(usuario_id: int = Query(..., description="ID del usuario")):
    """
    Calcula el balance total del usuario.
    Args:
        usuario_id (int): El ID del usuario para el cual se calculará el balance.
    Returns:
        float: El balance total del usuario.
    """
    return service_calcular_balance(usuario_id)


@router.get("/categorias")
def categorias(usuario_id: int = Query(..., description="ID del usuario")):
    """
    Obtiene los gastos del usuario por categoría.
    Args:
        usuario_id (int): El ID del usuario para el cual se obtendrán los gastos por categoría.
    Returns:
        dict: Diccionario con las categorías y los montos de gastos correspondientes.
    """
    return service_gastos_por_categoria(usuario_id)
