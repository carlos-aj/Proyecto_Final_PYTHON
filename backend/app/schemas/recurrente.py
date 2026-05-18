from pydantic import BaseModel, field_validator
from typing import Optional


class RecurrenteCreate(BaseModel):
    usuario_id: int
    tipo: str
    descripcion: str
    cantidad: float
    categoria: str
    frecuencia: str
    proxima_fecha: str

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in ("ingreso", "gasto"):
            raise ValueError("El tipo debe ser 'ingreso' o 'gasto'.")
        return v

    @field_validator("frecuencia")
    @classmethod
    def frecuencia_valida(cls, v: str) -> str:
        if v not in ("semanal", "mensual"):
            raise ValueError("La frecuencia debe ser 'semanal' o 'mensual'.")
        return v


class RecurrenteUpdate(BaseModel):
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[float] = None
    categoria: Optional[str] = None
    frecuencia: Optional[str] = None
    proxima_fecha: Optional[str] = None


class RecurrenteResponse(BaseModel):
    id: int
    usuario_id: int
    tipo: str
    descripcion: str
    cantidad: float
    categoria: str
    frecuencia: str
    proxima_fecha: str
