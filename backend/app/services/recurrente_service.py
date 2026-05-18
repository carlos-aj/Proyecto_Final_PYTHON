from app.database.database import (
    db_obtener_recurrentes,
    db_crear_recurrente,
    db_editar_recurrente,
    db_eliminar_recurrente,
    db_generar_movimientos_recurrentes,
)
from app.schemas.recurrente import RecurrenteCreate, RecurrenteUpdate


def service_obtener_recurrentes(usuario_id: int) -> list[dict]:
    """
    Función para obtener todos los movimientos recurrentes de un usuario.
    Args:
        usuario_id (int): ID del usuario del que se obtienen los recurrentes.
    Returns:
        list[dict]: Lista de movimientos recurrentes, generando previamente los pendientes.
    """
    db_generar_movimientos_recurrentes(usuario_id)
    return db_obtener_recurrentes(usuario_id)


def service_crear_recurrente(data: RecurrenteCreate) -> dict:
    """
    Función para crear un nuevo movimiento recurrente.
    Args:
        data (RecurrenteCreate): Esquema con los datos del recurrente a crear.
    Returns:
        dict: Diccionario con los datos del movimiento recurrente creado.
    """
    return db_crear_recurrente(
        data.usuario_id, data.tipo, data.descripcion,
        data.cantidad, data.categoria, data.frecuencia, data.proxima_fecha,
    )


def service_editar_recurrente(recurrente_id: int, data: RecurrenteUpdate) -> dict | None:
    """
    Función para editar los campos de un movimiento recurrente existente.
    Args:
        recurrente_id (int): ID del movimiento recurrente a editar.
        data (RecurrenteUpdate): Esquema con los campos a actualizar.
    Returns:
        dict | None: Diccionario con los datos actualizados o None si no se encontró.
    """
    campos = data.model_dump(exclude_unset=True)
    return db_editar_recurrente(recurrente_id, campos)


def service_eliminar_recurrente(recurrente_id: int) -> bool:
    """
    Función para eliminar un movimiento recurrente por su ID.
    Args:
        recurrente_id (int): ID del movimiento recurrente a eliminar.
    Returns:
        bool: True si el recurrente fue eliminado, False si no se encontró.
    """
    return db_eliminar_recurrente(recurrente_id)
