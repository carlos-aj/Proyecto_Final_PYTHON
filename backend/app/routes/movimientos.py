from fastapi import APIRouter, Query
from app.schemas.movimiento import MovimientoCreate, MovimientoResponse, MovimientoUpdate
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services.movimiento_service import (
    service_crear_movimiento,
    service_obtener_movimientos,
    service_eliminar_movimiento,
    service_editar_movimiento,
)
from app.database.database import (
    db_crear_usuario,
    db_obtener_usuarios,
    db_obtener_usuario,
    db_eliminar_usuario,
)
from fastapi import HTTPException

router = APIRouter()


# --------------------------------------------------------------------------- #
# Usuarios                                                                     #
# --------------------------------------------------------------------------- #

@router.get("/usuarios", response_model=list[UsuarioResponse], tags=["usuarios"])
def obtener_usuarios():
    """
    Obtiene la lista de todos los usuarios registrados en el sistema.
    Returns:
        list[UsuarioResponse]: Lista de usuarios registrados en el sistema.
    """
    return db_obtener_usuarios()


@router.post("/usuarios", response_model=UsuarioResponse, status_code=201, tags=["usuarios"])
def crear_usuario(datos: UsuarioCreate):
    """
    Crea un nuevo usuario en el sistema.
    Args:
        datos (UsuarioCreate): Datos del usuario a crear.
    Returns:
        UsuarioResponse: Información del usuario creado.
    """
    return db_crear_usuario(datos.nombre, datos.email)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse, tags=["usuarios"])
def obtener_usuario(usuario_id: int):
    """
    Obtiene la información de un usuario específico.
    Args:
        usuario_id (int): El ID del usuario a obtener.
    Returns:
        UsuarioResponse: Información del usuario solicitado.
    """
    usuario = db_obtener_usuario(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario


@router.delete("/usuarios/{usuario_id}", tags=["usuarios"])
def eliminar_usuario(usuario_id: int):
    """
    Elimina un usuario específico.
    Args:
        usuario_id (int): El ID del usuario a eliminar.
    Returns:
        dict: Un diccionario con el resultado de la operación de eliminación.
    """
    eliminado = db_eliminar_usuario(usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"detail": "Usuario eliminado correctamente."}


# --------------------------------------------------------------------------- #
# Movimientos (genérico)                                                       #
# --------------------------------------------------------------------------- #

@router.get("/movimientos", response_model=list[MovimientoResponse], tags=["movimientos"])
def obtener_movimientos(
    usuario_id: int | None = Query(default=None),
    categoria: str | None = Query(default=None),
    fecha_desde: str | None = Query(default=None),
    fecha_hasta: str | None = Query(default=None),
    recurrente: bool | None = Query(default=None),
):
    """
    Obtiene la lista de movimientos según los filtros proporcionados.
    """
    return service_obtener_movimientos(
        usuario_id=usuario_id,
        categoria=categoria,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        recurrente=recurrente,
    )


@router.post("/movimientos", response_model=MovimientoResponse, status_code=201, tags=["movimientos"])
def crear_movimiento(datos: MovimientoCreate):
    """
    Crea un nuevo movimiento en el sistema.
    Args:
        datos (MovimientoCreate): Datos del movimiento a crear.
    Returns:
        MovimientoResponse: Información del movimiento creado.
    """
    return service_crear_movimiento(datos)


@router.delete("/movimientos/{movimiento_id}", tags=["movimientos"])
def eliminar_movimiento(movimiento_id: int):
    return service_eliminar_movimiento(movimiento_id)


@router.put("/movimientos/{movimiento_id}", response_model=MovimientoResponse, tags=["movimientos"])
def editar_movimiento(movimiento_id: int, datos: MovimientoUpdate):
    return service_editar_movimiento(movimiento_id, datos)


# --------------------------------------------------------------------------- #
# Ingresos                                                                     #
# --------------------------------------------------------------------------- #

@router.get("/ingresos", response_model=list[MovimientoResponse], tags=["ingresos"])
def obtener_ingresos(usuario_id: int | None = Query(default=None)):
    """
    Obtiene la lista de ingresos según los filtros proporcionados.
    Args:
        usuario_id (int | None): El ID del usuario para filtrar los ingresos.
    Returns:
        list[MovimientoResponse]: Lista de ingresos que cumplen con los filtros.
    """
    return service_obtener_movimientos(usuario_id=usuario_id, tipo="ingreso")


@router.post("/ingresos", response_model=MovimientoResponse, status_code=201, tags=["ingresos"])
def crear_ingreso(datos: MovimientoCreate):
    """
    Crea un nuevo ingreso en el sistema.
    Args:
        datos (MovimientoCreate): Datos del ingreso a crear.
    Returns:
        MovimientoResponse: Información del ingreso creado.
    """ 
    datos.tipo = "ingreso"  # type: ignore[assignment]
    return service_crear_movimiento(datos)


# --------------------------------------------------------------------------- #
# Gastos                                                                       #
# --------------------------------------------------------------------------- #

@router.get("/gastos", response_model=list[MovimientoResponse], tags=["gastos"])
def obtener_gastos(usuario_id: int | None = Query(default=None)):
    """
    Obtiene la lista de gastos según los filtros proporcionados.
    Args:
        usuario_id (int | None): El ID del usuario para filtrar los gastos.
    Returns:
        list[MovimientoResponse]: Lista de gastos que cumplen con los filtros.
    """
    return service_obtener_movimientos(usuario_id=usuario_id, tipo="gasto")


@router.post("/gastos", response_model=MovimientoResponse, status_code=201, tags=["gastos"])
def crear_gasto(datos: MovimientoCreate):
    """
    Crea un nuevo gasto en el sistema.
    Args:
        datos (MovimientoCreate): Datos del gasto a crear.
    Returns:
        MovimientoResponse: Información del gasto creado."""
    datos.tipo = "gasto"  # type: ignore[assignment]
    return service_crear_movimiento(datos)
