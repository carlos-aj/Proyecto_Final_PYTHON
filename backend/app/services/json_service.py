import json
from pathlib import Path
from fastapi import HTTPException
from app.database.database import (
    db_obtener_usuario,
    db_obtener_movimientos,
)
from app.models.usuario import GestorFinanzas


def service_exportar_json(usuario_id: int) -> dict:
    """
    Función para exportar los movimientos de un usuario en formato JSON.
    Args:
        usuario_id (int): ID del usuario cuyos datos se exportan.
    Returns:
        dict: Diccionario con el nombre del usuario y la lista de movimientos.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    usuario = db_obtener_usuario(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    movimientos = db_obtener_movimientos(usuario_id=usuario_id)
    return {
        "usuario": usuario["nombre"],
        "movimientos": [
            {
                "tipo": m["tipo"],
                "descripcion": m["descripcion"],
                "cantidad": m["cantidad"],
                "fecha": m["fecha"],
                "categoria": m["categoria"],
            }
            for m in movimientos
        ],
    }


def service_importar_json(usuario_id: int, datos: dict) -> dict:
    """
    Función para importar movimientos desde un diccionario JSON para un usuario.
    Args:
        usuario_id (int): ID del usuario al que se importan los movimientos.
        datos (dict): Diccionario con la clave 'movimientos' conteniendo una lista de movimientos.
    Returns:
        dict: Diccionario con los contadores 'importados' y 'errores'.
    Raises:
        HTTPException: Con código 404 si el usuario no existe, o 400 si el formato es inválido.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    movimientos = datos.get("movimientos", [])
    if not isinstance(movimientos, list):
        raise HTTPException(status_code=400, detail="El campo 'movimientos' debe ser una lista.")

    # GestorFinanzas orquesta el registro y persistencia de cada movimiento
    gestor = GestorFinanzas()
    gestor.cargar_datos(usuario_id)
    usuario = gestor.obtener_usuario(usuario_id)

    importados = 0
    errores = []

    for i, m in enumerate(movimientos):
        try:
            tipo = m.get("tipo", "").lower()
            if tipo not in ("ingreso", "gasto"):
                raise ValueError(f"Tipo inválido: '{tipo}'")

            if tipo == "ingreso":
                obj = gestor.registrar_ingreso(
                    usuario,
                    descripcion=m.get("descripcion", ""),
                    cantidad=float(m.get("cantidad", -1)),
                    fecha=m.get("fecha", ""),
                    categoria=m.get("categoria", ""),
                )
            else:
                obj = gestor.registrar_gasto(
                    usuario,
                    descripcion=m.get("descripcion", ""),
                    cantidad=float(m.get("cantidad", -1)),
                    fecha=m.get("fecha", ""),
                    categoria=m.get("categoria", ""),
                )
            gestor.guardar_datos(usuario_id, obj)
            importados += 1
        except (ValueError, KeyError, TypeError) as exc:
            errores.append({"indice": i, "error": str(exc)})

    return {"importados": importados, "errores": errores}


def service_exportar_csv(usuario_id: int) -> str:
    """
    Función para exportar los movimientos de un usuario en formato CSV.
    Args:
        usuario_id (int): ID del usuario cuyos datos se exportan.
    Returns:
        str: Texto CSV con cabecera y una fila por movimiento.
    Raises:
        HTTPException: Con código 404 si el usuario no existe.
    """
    if not db_obtener_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    movimientos = db_obtener_movimientos(usuario_id=usuario_id)
    lineas = ["tipo,descripcion,cantidad,fecha,categoria,recurrente,frecuencia"]
    for m in movimientos:
        recurrente = "1" if m.get("recurrente") else "0"
        frecuencia = m.get("frecuencia") or ""
        desc = str(m["descripcion"]).replace(",", ";")
        cat = str(m["categoria"]).replace(",", ";")
        lineas.append(
            f"{m['tipo']},{desc},{m['cantidad']},{m['fecha']},{cat},{recurrente},{frecuencia}"
        )
    return "\n".join(lineas)
