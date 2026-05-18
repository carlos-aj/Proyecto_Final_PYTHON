from fastapi import HTTPException
from app.database.database import (
    db_obtener_categorias,
    db_crear_categoria,
    db_eliminar_categoria,
    db_obtener_usuario,
)
from app.schemas.categoria import CategoriaCreate, CategoriaResponse


def service_obtener_categorias(usuario_id: int, tipo: str | None = None) -> list[CategoriaResponse]:
    """
    Función para obtener las categorías disponibles para un usuario.
    Args:
        usuario_id (int): ID del usuario del que se obtienen las categorías.
        tipo (str | None): Tipo de categoría para filtrar ('gasto' o 'ingreso') (opcional).
    Returns:
        list[CategoriaResponse]: Lista de categorías del sistema más las del usuario.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    rows = db_obtener_categorias(usuario_id, tipo)
    return [CategoriaResponse(id=r["id"], nombre=r["nombre"], es_default=bool(r["es_default"]), tipo=r["tipo"]) for r in rows]


def service_crear_categoria(datos: CategoriaCreate) -> CategoriaResponse:
    """
    Función para crear una nueva categoría personalizada para un usuario.
    Args:
        datos (CategoriaCreate): Esquema con los datos de la categoría a crear.
    Returns:
        CategoriaResponse: La categoría creada.
    Raises:
        HTTPException: Con código 404 si el usuario no existe, o 409 si ya existe una categoría con ese nombre.
    """
    if not db_obtener_usuario(datos.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    # Verificar duplicado dentro del mismo tipo (case-insensitive)
    existentes = db_obtener_categorias(datos.usuario_id, datos.tipo)
    if any(c["nombre"].lower() == datos.nombre.lower() for c in existentes):
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre.")
    row = db_crear_categoria(datos.nombre, datos.usuario_id, datos.tipo)
    return CategoriaResponse(id=row["id"], nombre=row["nombre"], es_default=False, tipo=row["tipo"])


def service_eliminar_categoria(categoria_id: int, usuario_id: int) -> dict:
    """
    Función para eliminar una categoría personalizada de un usuario.
    Args:
        categoria_id (int): ID de la categoría a eliminar.
        usuario_id (int): ID del usuario propietario de la categoría.
    Returns:
        dict: Mensaje de confirmación de eliminación.
    Raises:
        HTTPException: Con código 403 si la categoría no existe o es del sistema.
    """
    nombre = db_eliminar_categoria(categoria_id, usuario_id)
    if nombre is None:
        raise HTTPException(
            status_code=403,
            detail="No se puede eliminar: categoría no encontrada o es una categoría del sistema.",
        )
    return {"mensaje": f"Categoría '{nombre}' eliminada. Sus movimientos han sido reasignados a 'Otros'."}
