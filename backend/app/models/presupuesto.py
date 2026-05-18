class Presupuesto:
    """Límite de gasto mensual para una categoría concreta."""

    def __init__(self, usuario_id: int, categoria: str, limite: float, mes: str):
        """
        Método constructor para inicializar un presupuesto mensual.
        Args:
            usuario_id (int): ID del usuario propietario del presupuesto.
            categoria (str): Categoría a la que aplica el presupuesto.
            limite (float): Importe máximo de gasto permitido en el mes.
            mes (str): Mes al que aplica el presupuesto en formato 'YYYY-MM'.
        """
        self.__id: int | None = None
        self.__usuario_id = usuario_id
        self.__categoria = categoria
        self.__limite = limite
        self.__mes = mes

    @property
    def id(self) -> int | None:
        """
        Método getter para el ID del presupuesto.
        Returns:
            int | None: El ID del presupuesto o None si no ha sido asignado.
        """
        return self.__id

    @id.setter
    def id(self, value: int):
        """
        Método setter para el ID del presupuesto.
        Args:
            value (int): El ID a asignar al presupuesto.
        """
        self.__id = value

    @property
    def usuario_id(self) -> int:
        """
        Método getter para el ID del usuario propietario del presupuesto.
        Returns:
            int: El ID del usuario.
        """
        return self.__usuario_id

    @property
    def categoria(self) -> str:
        """
        Método getter para la categoría del presupuesto.
        Returns:
            str: La categoría a la que aplica el presupuesto.
        """
        return self.__categoria

    @property
    def limite(self) -> float:
        """
        Método getter para el límite de gasto del presupuesto.
        Returns:
            float: El importe máximo de gasto permitido en el mes.
        """
        return self.__limite

    @property
    def mes(self) -> str:
        """
        Método getter para el mes del presupuesto.
        Returns:
            str: El mes al que aplica el presupuesto en formato 'YYYY-MM'.
        """
        return self.__mes

    def porcentaje_consumido(self, gastado: float) -> float:
        """
        Método que calcula el porcentaje del presupuesto ya utilizado.
        Args:
            gastado (float): Cantidad gastada en la categoría durante el mes.
        Returns:
            float: Porcentaje consumido (puede superar 100 si se excede el límite).
        """
        if self.__limite == 0:
            return 0.0
        return round((gastado / self.__limite) * 100, 1)

    def esta_superado(self, gastado: float) -> bool:
        """
        Método que indica si el gasto ha superado el límite del presupuesto.
        Args:
            gastado (float): Cantidad gastada en la categoría durante el mes.
        Returns:
            bool: True si el gasto supera el límite establecido.
        """
        return gastado > self.__limite
