from fastapi import HTTPException
from app.database.database import (
    db_crear_objetivo,
    db_obtener_objetivos,
    db_obtener_objetivo,
    db_actualizar_aportacion,
    db_eliminar_objetivo,
    db_obtener_usuario,
)
from app.schemas.objetivo import ObjetivoCreate, AportacionCreate, ObjetivoResponse
from app.models.objetivo_ahorro import ObjetivoAhorro


def _enriquecer(row: dict) -> ObjetivoResponse:
    """
    Función auxiliar que construye un ObjetivoResponse enriquecido con cálculos del modelo.
    Args:
        row (dict): Diccionario con los datos del objetivo obtenido de la base de datos.
    Returns:
        ObjetivoResponse: Esquema del objetivo con progreso, días restantes y estado completado.
    """
    modelo = ObjetivoAhorro(
        usuario_id=row["usuario_id"],
        nombre=row["nombre"],
        cantidad_meta=row["cantidad_meta"],
        fecha_limite=row["fecha_limite"],
        cantidad_actual=row["cantidad_actual"],
    )
    modelo.id = row["id"]
    return ObjetivoResponse(
        id=row["id"],
        usuario_id=row["usuario_id"],
        nombre=row["nombre"],
        cantidad_meta=row["cantidad_meta"],
        cantidad_actual=row["cantidad_actual"],
        fecha_limite=row["fecha_limite"],
        progreso=round(modelo.progreso(), 1),
        dias_restantes=modelo.dias_restantes(),
        completado=modelo.esta_completado(),
    )


def service_crear_objetivo(datos: ObjetivoCreate) -> ObjetivoResponse:
    """
    Función para crear un nuevo objetivo de ahorro para un usuario.
    Args:
        datos (ObjetivoCreate): Esquema con los datos del objetivo a crear.
    Returns:
        ObjetivoResponse: El objetivo creado enriquecido con progreso y días restantes.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(datos.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    row = db_crear_objetivo(
        usuario_id=datos.usuario_id,
        nombre=datos.nombre,
        cantidad_meta=datos.cantidad_meta,
        fecha_limite=datos.fecha_limite,
    )
    return _enriquecer(row)


def service_obtener_objetivos(usuario_id: int) -> list[ObjetivoResponse]:
    """
    Función para obtener todos los objetivos de ahorro de un usuario.
    Args:
        usuario_id (int): ID del usuario del que se obtienen los objetivos.
    Returns:
        list[ObjetivoResponse]: Lista de objetivos enriquecidos con progreso y días restantes.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    rows = db_obtener_objetivos(usuario_id)
    return [_enriquecer(r) for r in rows]


def service_aportacion_objetivo(objetivo_id: int, datos: AportacionCreate) -> ObjetivoResponse:
    """
    Función para registrar una aportación a un objetivo de ahorro existente.
    Args:
        objetivo_id (int): ID del objetivo al que se añade la aportación.
        datos (AportacionCreate): Esquema con la cantidad a aportar.
    Returns:
        ObjetivoResponse: El objetivo actualizado enriquecido con el nuevo progreso.
    Raises:
        HTTPException: Con código 404 si el objetivo no se encontró.
    """
    row = db_obtener_objetivo(objetivo_id)
    if not row:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado.")
    nuevo_total = row["cantidad_actual"] + datos.cantidad
    updated = db_actualizar_aportacion(objetivo_id, nuevo_total)
    return _enriquecer(updated)


def service_eliminar_objetivo(objetivo_id: int) -> dict:
    """
    Función para eliminar un objetivo de ahorro por su ID.
    Args:
        objetivo_id (int): ID del objetivo a eliminar.
    Returns:
        dict: Mensaje de confirmación de eliminación.
    Raises:
        HTTPException: Con código 404 si el objetivo no se encontró.
    """
    eliminado = db_eliminar_objetivo(objetivo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado.")
    return {"mensaje": "Objetivo eliminado."}
