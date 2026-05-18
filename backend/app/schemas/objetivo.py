from pydantic import BaseModel, field_validator


class ObjetivoCreate(BaseModel):
    usuario_id: int
    nombre: str
    cantidad_meta: float
    fecha_limite: str  # YYYY-MM-DD

    @field_validator("nombre", "fecha_limite")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()

    @field_validator("cantidad_meta")
    @classmethod
    def meta_positiva(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("La cantidad meta debe ser positiva.")
        return v


class AportacionCreate(BaseModel):
    cantidad: float

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("La aportación debe ser positiva.")
        return v


class ObjetivoResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    cantidad_meta: float
    cantidad_actual: float
    fecha_limite: str
    progreso: float = 0.0
    dias_restantes: int = 0
    completado: bool = False
