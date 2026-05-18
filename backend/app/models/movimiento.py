from abc import ABC, abstractmethod
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class Movimiento(ABC):
    """Clase abstracta que representa un movimiento financiero genérico."""

    def __init__(self, descripcion: str, cantidad: float, fecha: str, categoria: str):
        """
        Metodo constructor para inicializar un movimiento.
        Args:
            descripcion (str): Descripción del movimiento.
            cantidad (float): Cantidad del movimiento (positiva para ingresos, negativa para gastos).
            fecha (str): Fecha del movimiento en formato 'YYYY-MM-DD'.
            categoria (str): Categoría del movimiento (ej. 'comida', 'transporte', 'salario').
        Raises:
            ValueError: Si la descripción, fecha o categoría están vacías, o si la cantidad es negativa.
        """
        if not descripcion or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía.")
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        if not fecha or not fecha.strip():
            raise ValueError("La fecha no puede estar vacía.")
        if not categoria or not categoria.strip():
            raise ValueError("La categoría no puede estar vacía.")

        self.__id: int | None = None
        self.__descripcion: str = descripcion.strip()
        self.__cantidad: float = cantidad
        self.__fecha: str = fecha.strip()
        self.__categoria: str = categoria.strip()

    # ------------------------------------------------------------------ #
    # Propiedades                                                          #
    # ------------------------------------------------------------------ #

    @property
    def id(self) -> int | None:
        """
        Método getter para el ID del movimiento.
        Returns:
            int | None: El ID del movimiento o None si no ha sido asignado.
        """
        return self.__id

    @id.setter
    def id(self, value: int):
        """Método setter para el ID del movimiento.
        Args:            
        value (int): El ID a asignar al movimiento.
        Raises:            
            ValueError: Si el ID es negativo.
        """
        if value < 0:
            raise ValueError("El ID no puede ser negativo.")
        self.__id = value

    @property
    def descripcion(self) -> str:
        """
        Método getter para la descripción del movimiento.
        Returns:
            str: La descripción del movimiento.
        """
        return self.__descripcion

    @property
    def cantidad(self) -> float:
        """
        Método getter para la cantidad del movimiento.
        Returns:
            float: La cantidad del movimiento.
        """
        return self.__cantidad

    @property
    def fecha(self) -> str:
        """
        Método getter para la fecha del movimiento.
        Returns:
            str: La fecha del movimiento en formato 'YYYY-MM-DD'.
        """
        return self.__fecha

    @property
    def categoria(self) -> str:
        """
        Método getter para la categoría del movimiento.
        Returns:
            str: La categoría del movimiento.
        """
        return self.__categoria

    # ------------------------------------------------------------------ #
    # Método abstracto                                                     #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def calcular_impacto(self) -> float:
        """Devuelve el impacto del movimiento sobre el balance."""

    # ------------------------------------------------------------------ #
    # Utilidades                                                           #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """
        Método para convertir el movimiento a un diccionario, útil para respuestas API.
        Returns:
            dict: Diccionario con los datos del movimiento.
        """
        return {
            "id": self.id,
            "tipo": self.__class__.__name__.lower(),
            "descripcion": self.descripcion,
            "cantidad": self.cantidad,
            "fecha": self.fecha,
            "categoria": self.categoria,
        }

    def __repr__(self) -> str:
        """
        Método para representar el movimiento como una cadena, útil para depuración.
        Returns:
            str: Representación en cadena del movimiento.
        """
        return (
            f"{self.__class__.__name__}(id={self.id}, descripcion='{self.descripcion}', "
            f"cantidad={self.cantidad}, fecha='{self.fecha}', categoria='{self.categoria}')"
        )


# --------------------------------------------------------------------------- #
# Clases concretas                                                             #
# --------------------------------------------------------------------------- #

class Ingreso(Movimiento):
    """Representa un ingreso económico."""

    def calcular_impacto(self) -> float:
        """
        Método que devuelve el impacto positivo del ingreso sobre el balance.
        Returns:
            float: El impacto del ingreso (igual a su cantidad).
        """
        return self.cantidad


class Gasto(Movimiento):
    """Representa un gasto económico."""

    def calcular_impacto(self) -> float:
        """
        Método que devuelve el impacto negativo del gasto sobre el balance.
        Returns:
            float: El impacto del gasto (negativo de su cantidad).
        """
        return -self.cantidad


class MovimientoRecurrente(Movimiento):
    """Movimiento que se repite con una frecuencia determinada (semanal o mensual)."""

    FRECUENCIAS = ("semanal", "mensual")

    def __init__(
        self,
        descripcion: str,
        cantidad: float,
        fecha: str,
        categoria: str,
        tipo: str,
        frecuencia: str,
    ):
        """
        Método constructor para inicializar un movimiento recurrente.
        Args:
            descripcion (str): Descripción del movimiento recurrente.
            cantidad (float): Cantidad del movimiento (positiva).
            fecha (str): Fecha del movimiento en formato 'YYYY-MM-DD'.
            categoria (str): Categoría del movimiento.
            tipo (str): Tipo del movimiento ('ingreso' o 'gasto').
            frecuencia (str): Frecuencia de repetición ('semanal' o 'mensual').
        Raises:
            ValueError: Si la frecuencia no es válida o el tipo no es 'ingreso' o 'gasto'.
        """
        super().__init__(descripcion, cantidad, fecha, categoria)
        if frecuencia not in self.FRECUENCIAS:
            raise ValueError(f"Frecuencia debe ser una de: {self.FRECUENCIAS}")
        if tipo not in ("ingreso", "gasto"):
            raise ValueError("Tipo debe ser 'ingreso' o 'gasto'.")
        self.__tipo = tipo
        self.__frecuencia = frecuencia
        self.__activo = True

    @property
    def tipo(self) -> str:
        """
        Método getter para el tipo del movimiento recurrente.
        Returns:
            str: El tipo del movimiento recurrente ('ingreso' o 'gasto').
        """
        return self.__tipo

    @property
    def frecuencia(self) -> str:
        """
        Método getter para la frecuencia del movimiento recurrente.
        Returns:
            str: La frecuencia del movimiento recurrente ('semanal' o 'mensual').
        """
        return self.__frecuencia

    @property
    def activo(self) -> bool:
        """
        Método getter para el estado activo del movimiento recurrente.
        Returns:
            bool: True si el movimiento recurrente está activo, False en caso contrario.
        """
        return self.__activo

    def calcular_impacto(self) -> float:
        """
        Método que devuelve el impacto del movimiento recurrente sobre el balance.
        Returns:
            float: El impacto positivo si es ingreso, negativo si es gasto.
        """
        return self.cantidad if self.__tipo == "ingreso" else -self.cantidad

    def generar_siguiente_fecha(self) -> str:
        """Calcula la próxima fecha a partir de la última fecha registrada."""
        base = date.fromisoformat(self.fecha)
        if self.__frecuencia == "semanal":
            siguiente = base + timedelta(weeks=1)
        else:
            siguiente = base + relativedelta(months=1)
        return siguiente.isoformat()
