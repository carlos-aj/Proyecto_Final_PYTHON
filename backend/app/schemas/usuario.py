from pydantic import BaseModel, field_validator


class UsuarioCreate(BaseModel):
    """Esquema para la creación de un nuevo usuario.
    Atributos:
        nombre (str): El nombre del usuario, no puede estar vacío.
        email (str): El email del usuario, no puede estar vacío.
    Validaciones:
        - El nombre y el email no pueden estar vacíos.
    """
    nombre: str
    email: str

    @field_validator("nombre", "email")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        """Validador para asegurarse de que los campos no estén vacíos.
        Args:            
            v (str): El valor del campo a validar.
        Returns:
            str: El valor del campo si es válido.
        Raises:
            ValueError: Si el campo está vacío o solo contiene espacios.
        """
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()


class UsuarioResponse(BaseModel):
    """
    Esquema para la respuesta de un usuario.
    Atributos:
        id (int): El ID del usuario.
        nombre (str): El nombre del usuario.
        email (str): El email del usuario.
    """
    id: int
    nombre: str
    email: str
