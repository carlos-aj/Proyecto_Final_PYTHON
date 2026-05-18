from datetime import date


class ObjetivoAhorro:
    """Meta económica con fecha límite y seguimiento de progreso."""

    def __init__(
        self,
        usuario_id: int,
        nombre: str,
        cantidad_meta: float,
        fecha_limite: str,
        cantidad_actual: float = 0.0,
    ):
        """
        Método constructor para inicializar un objetivo de ahorro.
        Args:
            usuario_id (int): ID del usuario propietario del objetivo.
            nombre (str): Nombre descriptivo del objetivo.
            cantidad_meta (float): Cantidad total a alcanzar.
            fecha_limite (str): Fecha límite en formato 'YYYY-MM-DD'.
            cantidad_actual (float): Cantidad ahorrada hasta el momento (por defecto 0.0).
        Raises:
            ValueError: Si el nombre está vacío o la cantidad meta no es positiva.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if cantidad_meta <= 0:
            raise ValueError("La cantidad meta debe ser positiva.")

        self.__id: int | None = None
        self.__usuario_id = usuario_id
        self.__nombre = nombre.strip()
        self.__cantidad_meta = cantidad_meta
        self.__cantidad_actual = cantidad_actual
        self.__fecha_limite = fecha_limite

    @property
    def id(self) -> int | None:
        """
        Método getter para el ID del objetivo de ahorro.
        Returns:
            int | None: El ID del objetivo o None si no ha sido asignado.
        """
        return self.__id

    @id.setter
    def id(self, value: int):
        """
        Método setter para el ID del objetivo de ahorro.
        Args:
            value (int): El ID a asignar al objetivo.
        """
        self.__id = value

    @property
    def usuario_id(self) -> int:
        """
        Método getter para el ID del usuario propietario del objetivo.
        Returns:
            int: El ID del usuario.
        """
        return self.__usuario_id

    @property
    def nombre(self) -> str:
        """
        Método getter para el nombre del objetivo de ahorro.
        Returns:
            str: El nombre del objetivo.
        """
        return self.__nombre

    @property
    def cantidad_meta(self) -> float:
        """
        Método getter para la cantidad meta del objetivo de ahorro.
        Returns:
            float: La cantidad total a alcanzar.
        """
        return self.__cantidad_meta

    @property
    def cantidad_actual(self) -> float:
        """
        Método getter para la cantidad actual del objetivo de ahorro.
        Returns:
            float: La cantidad ahorrada hasta el momento.
        """
        return self.__cantidad_actual

    @property
    def fecha_limite(self) -> str:
        """
        Método getter para la fecha límite del objetivo de ahorro.
        Returns:
            str: La fecha límite en formato 'YYYY-MM-DD'.
        """
        return self.__fecha_limite

    def progreso(self) -> float:
        """
        Método que calcula el porcentaje de avance hacia la meta.
        Returns:
            float: Porcentaje de avance (0-100).
        """
        if self.__cantidad_meta == 0:
            return 100.0
        return round(min((self.__cantidad_actual / self.__cantidad_meta) * 100, 100.0), 1)

    def dias_restantes(self) -> int:
        """
        Método que calcula los días que quedan hasta la fecha límite.
        Returns:
            int: Número de días restantes (mínimo 0).
        """
        limite = date.fromisoformat(self.__fecha_limite)
        return max((limite - date.today()).days, 0)

    def esta_completado(self) -> bool:
        """
        Método que indica si el objetivo de ahorro ha sido completado.
        Returns:
            bool: True si la cantidad actual ha alcanzado o superado la meta.
        """
        return self.__cantidad_actual >= self.__cantidad_meta
