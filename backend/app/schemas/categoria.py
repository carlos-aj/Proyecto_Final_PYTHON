from pydantic import BaseModel, field_validator


class CategoriaCreate(BaseModel):
    usuario_id: int
    nombre: str
    tipo: str

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 50:
            raise ValueError("El nombre no puede superar 50 caracteres.")
        return v

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in ("gasto", "ingreso"):
            raise ValueError("El tipo debe ser 'gasto' o 'ingreso'.")
        return v


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    es_default: bool
    tipo: str
