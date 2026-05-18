from pydantic import BaseModel, field_validator
from typing import Literal, Optional


class MovimientoCreate(BaseModel):
    usuario_id: int
    tipo: Literal["ingreso", "gasto"]
    descripcion: str
    cantidad: float
    fecha: str
    categoria: str
    recurrente: bool = False
    frecuencia: Optional[str] = None

    @field_validator("descripcion", "fecha", "categoria")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: float) -> float:
        if v < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        return v

    @field_validator("frecuencia")
    @classmethod
    def frecuencia_valida(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("semanal", "mensual"):
            raise ValueError("La frecuencia debe ser 'semanal' o 'mensual'.")
        return v


class MovimientoUpdate(BaseModel):
    tipo: Optional[Literal["ingreso", "gasto"]] = None
    descripcion: Optional[str] = None
    cantidad: Optional[float] = None
    fecha: Optional[str] = None
    categoria: Optional[str] = None
    recurrente: Optional[bool] = None
    frecuencia: Optional[str] = None


class MovimientoResponse(BaseModel):
    id: int
    usuario_id: int
    tipo: Literal["ingreso", "gasto"]
    descripcion: str
    cantidad: float
    fecha: str
    categoria: str
    recurrente: bool = False
    frecuencia: Optional[str] = None
