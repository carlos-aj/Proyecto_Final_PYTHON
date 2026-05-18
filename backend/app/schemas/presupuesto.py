from pydantic import BaseModel, field_validator


class PresupuestoCreate(BaseModel):
    usuario_id: int
    categoria: str
    limite: float
    mes: str  # formato YYYY-MM

    @field_validator("categoria", "mes")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()

    @field_validator("limite")
    @classmethod
    def limite_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("El límite debe ser positivo.")
        return v


class PresupuestoResponse(BaseModel):
    id: int
    usuario_id: int
    categoria: str
    limite: float
    mes: str
