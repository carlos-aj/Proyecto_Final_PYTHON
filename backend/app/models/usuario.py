from app.models.movimiento import Movimiento, Ingreso, Gasto, MovimientoRecurrente


class Usuario:
    """Representa al usuario propietario de los movimientos."""

    def __init__(self, nombre: str, email: str):
        """
        Método constructor para la clase Usuario.
        Args:
            nombre (str): El nombre del usuario.
            email (str): El correo electrónico del usuario.
        Raises:
            ValueError: Si el nombre o el email son vacíos o no válidos.
        """
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        if not email:
            raise ValueError("El email no puede estar vacío.")
        self.__id: int | None = None
        self.__nombre: str = nombre
        self.__email: str = email
        self.__movimientos: list[Movimiento] = []

    # ------------------------------------------------------------------ #
    # Propiedades                                                          #
    # ------------------------------------------------------------------ #

    @property
    def id(self) -> int | None:
        """
        Método getter para el ID del usuario.
        Returns:
            int | None: El ID del usuario o None si no ha sido asignado.
        """
        return self.__id

    @id.setter
    def id(self, value: int):
        """
        Método setter para el ID del usuario.
        Args:
            value (int): El ID a asignar al usuario.
        Raises:
            ValueError: Si el ID es negativo.
        """
        if value < 0:
            raise ValueError("El ID no puede ser negativo.")
        self.__id = value

    @property
    def nombre(self) -> str:
        """
        Método getter para el nombre del usuario.
        Returns:
            str: El nombre del usuario.
        """
        return self.__nombre

    @property
    def email(self) -> str:
        """
        Método getter para el email del usuario.
        Returns:
            str: El email del usuario.
        """
        return self.__email

    @property
    def movimientos(self) -> list[Movimiento]:
        """
        Método getter para los movimientos del usuario.
        Returns:
            list[Movimiento]: Lista de movimientos del usuario.
        """
        return list(self.__movimientos)

    # ------------------------------------------------------------------ #
    # Métodos                                                              #
    # ------------------------------------------------------------------ #

    def agregar_movimiento(self, movimiento: Movimiento) -> None:
        """
        Agrega un movimiento a la lista de movimientos del usuario.
        Args:
            movimiento (Movimiento): El movimiento a agregar.
        Raises:
            ValueError: Si el objeto proporcionado no es una instancia válida de Movimiento.
        """
        if not isinstance(movimiento, Movimiento):
            raise ValueError("El objeto proporcionado no es una instancia válida de Movimiento.")
        self.__movimientos.append(movimiento)

    def calcular_balance(self) -> float:
        """
        Metodo que calcula el balance total usando polimorfismo.
        Returns:
            float: El balance total del usuario.
        """
        return sum(m.calcular_impacto() for m in self.__movimientos)

    def obtener_gastos_por_categoria(self) -> dict[str, float]:
        """
        Metodo que agrupa los gastos por categoría.
        Returns:
            dict[str, float]: Diccionario con las categorías y sus gastos totales.
        """
        resultado: dict[str, float] = {}
        for m in self.__movimientos:
            if isinstance(m, Gasto):
                resultado[m.categoria] = resultado.get(m.categoria, 0.0) + m.cantidad
        return resultado

    def to_dict(self) -> dict:
        """
        Método para convertir el usuario a un diccionario, útil para respuestas API.
        Returns:
            dict: Diccionario con los datos del usuario.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
        }

    def __repr__(self) -> str:
        """
        Método para representar el usuario como una cadena, útil para depuración.
        Returns:
            str: Representación en cadena del usuario.
        """
        return f"Usuario(id={self.id}, nombre='{self.nombre}', email='{self.email}')"


# --------------------------------------------------------------------------- #

class GestorFinanzas:
    """Coordina las operaciones principales del sistema."""

    def __init__(self):
        """Método constructor para la clase GestorFinanzas. Inicializa la lista de usuarios vacía."""
        self.__usuarios: list[Usuario] = []

    @property
    def usuarios(self) -> list[Usuario]:
        """
        Método getter para la lista de usuarios.
        Returns:
            list[Usuario]: Lista de usuarios registrados en el sistema.
        """
        return list(self.__usuarios)

    def crear_usuario(self, nombre: str, email: str) -> Usuario:
        """
        Método para crear un nuevo usuario y agregarlo a la lista de usuarios.
        Args:
            nombre (str): El nombre del nuevo usuario.
            email (str): El correo electrónico del nuevo usuario.
        Returns:
            Usuario: El usuario creado.
        Raises:
            ValueError: Si el nombre o el email son vacíos o no válidos.
        """
        usuario = Usuario(nombre, email)
        self.__usuarios.append(usuario)
        return usuario

    def obtener_usuario(self, usuario_id: int) -> Usuario | None:
        """Método para obtener un usuario por su ID.
        Args:
            usuario_id (int): El ID del usuario a obtener.
        Returns:
            Usuario | None: El usuario encontrado o None si no se encuentra.
        """
        return next((u for u in self.__usuarios if u.id == usuario_id), None)

    def registrar_ingreso(
        self,
        usuario: Usuario,
        descripcion: str,
        cantidad: float,
        fecha: str,
        categoria: str,
    ) -> Ingreso:
        """
        Método para registrar un ingreso y añadirlo al usuario.
        Args:
            usuario (Usuario): El usuario al que se asocia el ingreso.
            descripcion (str): Descripción del ingreso.
            cantidad (float): Cantidad del ingreso.
            fecha (str): Fecha del ingreso en formato 'YYYY-MM-DD'.
            categoria (str): Categoría del ingreso.
        Returns:
            Ingreso: El objeto Ingreso creado y registrado.
        """
        ingreso = Ingreso(descripcion, cantidad, fecha, categoria)
        usuario.agregar_movimiento(ingreso)
        return ingreso

    def registrar_gasto(
        self,
        usuario: Usuario,
        descripcion: str,
        cantidad: float,
        fecha: str,
        categoria: str,
    ) -> Gasto:
        """
        Método para registrar un gasto y añadirlo al usuario.
        Args:
            usuario (Usuario): El usuario al que se asocia el gasto.
            descripcion (str): Descripción del gasto.
            cantidad (float): Cantidad del gasto.
            fecha (str): Fecha del gasto en formato 'YYYY-MM-DD'.
            categoria (str): Categoría del gasto.
        Returns:
            Gasto: El objeto Gasto creado y registrado.
        """
        gasto = Gasto(descripcion, cantidad, fecha, categoria)
        usuario.agregar_movimiento(gasto)
        return gasto

    def cargar_datos(self, usuario_id: int) -> None:
        """Carga un usuario y sus movimientos desde la base de datos.
        Args:
            usuario_id (int): El ID del usuario a cargar.
        """
        from app.database.database import db_obtener_usuario, db_obtener_movimientos
        row = db_obtener_usuario(usuario_id)
        if not row:
            return
        u = Usuario(row["nombre"], row["email"])
        u.id = row["id"]
        for m in db_obtener_movimientos(usuario_id=usuario_id):
            recurrente = bool(m.get("recurrente", 0))
            frecuencia = m.get("frecuencia")
            if recurrente and frecuencia:
                obj = MovimientoRecurrente(
                    m["descripcion"], m["cantidad"], m["fecha"], m["categoria"],
                    m["tipo"], frecuencia
                )
            else:
                cls = Ingreso if m["tipo"] == "ingreso" else Gasto
                obj = cls(m["descripcion"], m["cantidad"], m["fecha"], m["categoria"])
            obj.id = m["id"]
            u.agregar_movimiento(obj)
        self.__usuarios.append(u)

    def guardar_datos(self, usuario_id: int, movimiento: Movimiento) -> dict:
        """Persiste el movimiento registrado en la base de datos.
        Args:
            usuario_id (int): El ID del usuario al que pertenece el movimiento.
            movimiento (Movimiento): El movimiento a guardar.
        Returns:
            dict: Resultado de la operación de guardado en la base de datos.
        """
        from app.database.database import db_crear_movimiento
        if isinstance(movimiento, MovimientoRecurrente):
            tipo = movimiento.tipo
            recurrente = True
            frecuencia = movimiento.frecuencia
        else:
            tipo = "ingreso" if isinstance(movimiento, Ingreso) else "gasto"
            recurrente = False
            frecuencia = None
        return db_crear_movimiento(
            usuario_id=usuario_id,
            tipo=tipo,
            descripcion=movimiento.descripcion,
            cantidad=movimiento.cantidad,
            fecha=movimiento.fecha,
            categoria=movimiento.categoria,
            recurrente=recurrente,
            frecuencia=frecuencia,
        )
