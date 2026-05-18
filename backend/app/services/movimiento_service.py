from app.database.database import (
    db_obtener_movimientos,
    db_eliminar_movimiento,
    db_obtener_usuario,
    db_actualizar_movimiento,
)
from app.models.usuario import GestorFinanzas
from app.models.movimiento import MovimientoRecurrente
from app.schemas.movimiento import MovimientoCreate, MovimientoResponse, MovimientoUpdate
from fastapi import HTTPException


def service_crear_movimiento(datos: MovimientoCreate) -> MovimientoResponse:
    """
    Función para crear un nuevo movimiento usando el GestorFinanzas y polimorfismo.
    Args:
        datos (MovimientoCreate): Esquema con los datos del movimiento a crear.
    Returns:
        MovimientoResponse: El movimiento creado y persistido.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(datos.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    gestor = GestorFinanzas()
    gestor.cargar_datos(datos.usuario_id)
    usuario = gestor.obtener_usuario(datos.usuario_id)

    if datos.recurrente and datos.frecuencia:
        obj = MovimientoRecurrente(
            datos.descripcion, datos.cantidad, datos.fecha, datos.categoria,
            datos.tipo, datos.frecuencia
        )
        usuario.agregar_movimiento(obj)
    elif datos.tipo == "ingreso":
        obj = gestor.registrar_ingreso(
            usuario, datos.descripcion, datos.cantidad, datos.fecha, datos.categoria
        )
    else:
        obj = gestor.registrar_gasto(
            usuario, datos.descripcion, datos.cantidad, datos.fecha, datos.categoria
        )

    row = gestor.guardar_datos(datos.usuario_id, obj)
    return MovimientoResponse(**row)


def service_editar_movimiento(movimiento_id: int, datos: MovimientoUpdate) -> MovimientoResponse:
    """
    Función para editar los campos de un movimiento existente.
    Args:
        movimiento_id (int): ID del movimiento a editar.
        datos (MovimientoUpdate): Esquema con los campos a actualizar.
    Returns:
        MovimientoResponse: El movimiento actualizado.
    Raises:
        HTTPException: Con código 400 si no se proporcionaron campos, o 404 si no se encontró.
    """
    campos = datos.model_dump(exclude_none=True)
    if not campos:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar.")
    row = db_actualizar_movimiento(movimiento_id, campos)
    if not row:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado.")
    return MovimientoResponse(**row)


def service_obtener_movimientos(
    usuario_id: int | None = None,
    tipo: str | None = None,
    categoria: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    recurrente: bool | None = None,
) -> list[MovimientoResponse]:
    """
    Función para obtener movimientos con filtros opcionales.
    Args:
        usuario_id (int | None): ID del usuario para filtrar (opcional).
        tipo (str | None): Tipo de movimiento para filtrar (opcional).
        categoria (str | None): Categoría para filtrar (opcional).
        fecha_desde (str | None): Fecha mínima para filtrar en formato 'YYYY-MM-DD' (opcional).
        fecha_hasta (str | None): Fecha máxima para filtrar en formato 'YYYY-MM-DD' (opcional).
        recurrente (bool | None): Si True, filtra solo movimientos recurrentes (opcional).
    Returns:
        list[MovimientoResponse]: Lista de movimientos que cumplen los filtros.
    """
    rows = db_obtener_movimientos(usuario_id, tipo, categoria, fecha_desde, fecha_hasta, recurrente)
    return [MovimientoResponse(**row) for row in rows]


def service_eliminar_movimiento(movimiento_id: int) -> dict:
    """
    Función para eliminar un movimiento por su ID.
    Args:
        movimiento_id (int): ID del movimiento a eliminar.
    Returns:
        dict: Mensaje de confirmación de eliminación.
    Raises:
        HTTPException: Con código 404 si el movimiento no se encontró.
    """
    eliminado = db_eliminar_movimiento(movimiento_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado.")
    return {"detail": "Movimiento eliminado correctamente."}


def service_calcular_balance(usuario_id: int) -> dict:
    """
    Función para calcular el balance total de un usuario usando polimorfismo.
    Args:
        usuario_id (int): ID del usuario del que se calcula el balance.
    Returns:
        dict: Diccionario con usuario_id y balance total redondeado.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # GestorFinanzas carga el usuario con todos sus movimientos
    gestor = GestorFinanzas()
    gestor.cargar_datos(usuario_id)
    usuario = gestor.obtener_usuario(usuario_id)

    # Usuario.calcular_balance() aplica polimorfismo: llama calcular_impacto() en cada movimiento
    balance = usuario.calcular_balance()
    return {"usuario_id": usuario_id, "balance": round(balance, 2)}


def service_gastos_por_categoria(usuario_id: int) -> dict:
    """
    Función para obtener el total de gastos agrupados por categoría.
    Args:
        usuario_id (int): ID del usuario del que se calculan los gastos.
    Returns:
        dict: Diccionario con usuario_id y un mapa de categoría a total gastado.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # GestorFinanzas carga el usuario y delega a Usuario.obtener_gastos_por_categoria()
    gestor = GestorFinanzas()
    gestor.cargar_datos(usuario_id)
    usuario = gestor.obtener_usuario(usuario_id)

    categorias = {k: round(v, 2) for k, v in usuario.obtener_gastos_por_categoria().items()}
    return {"usuario_id": usuario_id, "categorias": categorias}
