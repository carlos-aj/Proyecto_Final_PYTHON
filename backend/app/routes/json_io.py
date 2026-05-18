from fastapi import APIRouter, Query
from fastapi.responses import Response
from app.services.json_service import service_exportar_json, service_importar_json, service_exportar_csv

router = APIRouter(tags=["json"])


@router.get("/exportar-json")
def exportar_json(usuario_id: int = Query(..., description="ID del usuario")):
    """Exporta los datos del usuario y sus movimientos en formato JSON.
    Args:
        usuario_id (int): El ID del usuario cuyos datos se exportarán.
    Returns:
        dict: Un diccionario con los datos del usuario y sus movimientos.
    """
    return service_exportar_json(usuario_id)


@router.post("/importar-json")
def importar_json(
    datos: dict,
    usuario_id: int = Query(..., description="ID del usuario"),
):
    """
    Importa los datos del usuario y sus movimientos desde un diccionario JSON.
    Args:
        datos (dict): Un diccionario con los datos del usuario y sus movimientos a importar.
        usuario_id (int): El ID del usuario al que se asociarán los datos importados.
    Returns:
        dict: Un diccionario con el resultado de la operación de importación.
    """
    return service_importar_json(usuario_id, datos)


@router.get("/exportar-csv")
def exportar_csv(usuario_id: int = Query(..., description="ID del usuario")):
    """Exporta los movimientos del usuario en formato CSV."""
    csv_content = service_exportar_csv(usuario_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=movimientos_{usuario_id}.csv"},
    )
