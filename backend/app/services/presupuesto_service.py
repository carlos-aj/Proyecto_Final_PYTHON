from fastapi import HTTPException
from app.database.database import (
    db_crear_presupuesto,
    db_obtener_presupuestos,
    db_eliminar_presupuesto,
    db_obtener_usuario,
    db_obtener_movimientos,
)
from app.schemas.presupuesto import PresupuestoCreate, PresupuestoResponse
from app.models.presupuesto import Presupuesto


def service_crear_presupuesto(datos: PresupuestoCreate) -> PresupuestoResponse:
    """
    Función para crear un nuevo presupuesto mensual para un usuario.
    Args:
        datos (PresupuestoCreate): Esquema con los datos del presupuesto a crear.
    Returns:
        PresupuestoResponse: El presupuesto creado.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(datos.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    row = db_crear_presupuesto(
        usuario_id=datos.usuario_id,
        categoria=datos.categoria,
        limite=datos.limite,
        mes=datos.mes,
    )
    return PresupuestoResponse(**row)


def service_obtener_presupuestos(usuario_id: int, mes: str | None = None) -> list[dict]:
    """
    Función para obtener los presupuestos de un usuario enriquecidos con gasto real.
    Args:
        usuario_id (int): ID del usuario del que se obtienen los presupuestos.
        mes (str | None): Mes en formato 'YYYY-MM' para filtrar (opcional).
    Returns:
        list[dict]: Lista de presupuestos con campos adicionales: gastado, porcentaje y superado.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    presupuestos = db_obtener_presupuestos(usuario_id, mes)
    resultado = []
    for p in presupuestos:
        # Calcular el gasto real de esa categoría en ese mes
        todos_movimientos = db_obtener_movimientos(usuario_id=usuario_id)
        gastado = sum(
            m["cantidad"]
            for m in todos_movimientos
            if m["tipo"] == "gasto"
            and m["categoria"].lower() == p["categoria"].lower()
            and m["fecha"].startswith(p["mes"])
        )
        modelo = Presupuesto(p["usuario_id"], p["categoria"], p["limite"], p["mes"])
        modelo.id = p["id"]
        resultado.append({
            **PresupuestoResponse(**p).model_dump(),
            "gastado": round(gastado, 2),
            "porcentaje": round(modelo.porcentaje_consumido(gastado), 1),
            "superado": modelo.esta_superado(gastado),
        })
    return resultado


def service_eliminar_presupuesto(presupuesto_id: int) -> dict:
    """
    Función para eliminar un presupuesto por su ID.
    Args:
        presupuesto_id (int): ID del presupuesto a eliminar.
    Returns:
        dict: Mensaje de confirmación de eliminación.
    Raises:
        HTTPException: Con código 404 si el presupuesto no se encontró.
    """
    eliminado = db_eliminar_presupuesto(presupuesto_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado.")
    return {"mensaje": "Presupuesto eliminado."}
