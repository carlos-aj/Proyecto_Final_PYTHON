import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"


def get_connection() -> sqlite3.Connection:
    """
    Función auxiliar para obtener una conexión a la base de datos SQLite.

    Returns:
        sqlite3.Connection: Conexión a la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Función para crear las tablas de la base de datos si no existen.
    Raises:
        sqlite3.OperationalError: Si ocurre un error al ejecutar los scripts SQL.
    """
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS movimientos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                tipo       TEXT    NOT NULL,
                descripcion TEXT   NOT NULL,
                cantidad   REAL    NOT NULL,
                fecha      TEXT    NOT NULL,
                categoria  TEXT    NOT NULL,
                recurrente INTEGER NOT NULL DEFAULT 0,
                frecuencia TEXT,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS presupuestos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                categoria  TEXT    NOT NULL,
                limite     REAL    NOT NULL,
                mes        TEXT    NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS objetivos_ahorro (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id      INTEGER NOT NULL,
                nombre          TEXT    NOT NULL,
                cantidad_meta   REAL    NOT NULL,
                cantidad_actual REAL    NOT NULL DEFAULT 0,
                fecha_limite    TEXT    NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS categorias (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre     TEXT    NOT NULL,
                usuario_id INTEGER NOT NULL DEFAULT 0,
                es_default INTEGER NOT NULL DEFAULT 0,
                tipo       TEXT    NOT NULL DEFAULT 'gasto',
                UNIQUE(nombre, usuario_id, tipo)
            );

            CREATE TABLE IF NOT EXISTS recurrentes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id    INTEGER NOT NULL,
                tipo          TEXT    NOT NULL,
                descripcion   TEXT    NOT NULL,
                cantidad      REAL    NOT NULL,
                categoria     TEXT    NOT NULL,
                frecuencia    TEXT    NOT NULL,
                proxima_fecha TEXT    NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );
        """)
        # Migrar BD existente: añadir columnas si no existen
        for col, definition in [
            ("recurrente",     "INTEGER NOT NULL DEFAULT 0"),
            ("frecuencia",     "TEXT"),
            ("fecha_creacion", "TEXT"),
        ]:
            try:
                conn.execute(f"ALTER TABLE movimientos ADD COLUMN {col} {definition}")
                conn.commit()
            except Exception:
                pass

        # Migrar BD existente: crear tabla recurrentes si no existe
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recurrentes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id    INTEGER NOT NULL,
                tipo          TEXT    NOT NULL,
                descripcion   TEXT    NOT NULL,
                cantidad      REAL    NOT NULL,
                categoria     TEXT    NOT NULL,
                frecuencia    TEXT    NOT NULL,
                proxima_fecha TEXT    NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        """)
        conn.commit()

        # Migrar categorias: añadir tipo + actualizar UNIQUE si falta
        pragma_rows = conn.execute("PRAGMA table_info(categorias)").fetchall()
        if not any(row['name'] == 'tipo' for row in pragma_rows):
            conn.executescript("""
                CREATE TABLE categorias_new (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre     TEXT    NOT NULL,
                    usuario_id INTEGER NOT NULL DEFAULT 0,
                    es_default INTEGER NOT NULL DEFAULT 0,
                    tipo       TEXT    NOT NULL DEFAULT 'gasto',
                    UNIQUE(nombre, usuario_id, tipo)
                );
                INSERT OR IGNORE INTO categorias_new (id, nombre, usuario_id, es_default, tipo)
                    SELECT id, nombre, usuario_id, es_default, 'gasto' FROM categorias;
                DROP TABLE categorias;
                ALTER TABLE categorias_new RENAME TO categorias;
            """)

        # Seed categorías por defecto (idempotente gracias a INSERT OR IGNORE)
        defaults_gasto   = ['Comida', 'Transporte', 'Vivienda', 'Salud', 'Ocio',
                             'Ropa', 'Educación', 'Tecnología', 'Suscripciones', 'Otros']
        defaults_ingreso = ['Salario', 'Freelance', 'Inversiones', 'Alquiler',
                             'Venta', 'Regalo', 'Reembolso', 'Otros']
        with get_connection() as conn2:
            for nombre in defaults_gasto:
                conn2.execute(
                    "INSERT OR IGNORE INTO categorias (nombre, usuario_id, es_default, tipo) VALUES (?, 0, 1, 'gasto')",
                    (nombre,))
            for nombre in defaults_ingreso:
                conn2.execute(
                    "INSERT OR IGNORE INTO categorias (nombre, usuario_id, es_default, tipo) VALUES (?, 0, 1, 'ingreso')",
                    (nombre,))
            conn2.commit()

        # Reasignar categorías huérfanas (no existen en la tabla categorias) a 'Otros'
        conn.execute("""
            UPDATE movimientos
            SET categoria = 'Otros'
            WHERE categoria NOT IN (
                SELECT nombre FROM categorias WHERE usuario_id = 0
                UNION
                SELECT nombre FROM categorias WHERE usuario_id = movimientos.usuario_id
            )
        """)
        conn.commit()

    _seed_demo_data()


def _seed_demo_data() -> None:
    """Inserta datos de demostración para usuario_id=1 si no existen todavía."""
    with get_connection() as conn:
        # Crear usuario demo si no existe
        if not conn.execute("SELECT 1 FROM usuarios WHERE id = 1").fetchone():
            conn.execute(
                "INSERT INTO usuarios (nombre, email) VALUES (?, ?)",
                ("Carlos", "carlos@example.com"),
            )
            conn.commit()

        # Idempotente: solo insertar si no hay movimientos del usuario 1
        if conn.execute("SELECT COUNT(*) FROM movimientos WHERE usuario_id = 1").fetchone()[0] > 0:
            return

        movimientos = [
            # ── Ingresos ──────────────────────────────────────────────────
            (1, 'ingreso', 'Nómina marzo',              2200.00, '2026-03-01', 'Salario',       1, 'mensual'),
            (1, 'ingreso', 'Nómina abril',              2200.00, '2026-04-01', 'Salario',       1, 'mensual'),
            (1, 'ingreso', 'Nómina mayo',               2200.00, '2026-05-01', 'Salario',       1, 'mensual'),
            (1, 'ingreso', 'Proyecto freelance web',     450.00, '2026-04-15', 'Freelance',     0, None),
            (1, 'ingreso', 'Dividendos ETF',              85.00, '2026-03-20', 'Inversiones',   0, None),
            (1, 'ingreso', 'Venta portátil viejo',       320.00, '2026-04-05', 'Venta',         0, None),
            (1, 'ingreso', 'Reembolso seguro médico',    120.00, '2026-05-10', 'Reembolso',     0, None),
            (1, 'ingreso', 'Regalo cumpleaños',          150.00, '2026-03-28', 'Regalo',        0, None),
            # ── Gastos: Vivienda ──────────────────────────────────────────
            (1, 'gasto',   'Alquiler marzo',             750.00, '2026-03-02', 'Vivienda',      1, 'mensual'),
            (1, 'gasto',   'Alquiler abril',             750.00, '2026-04-02', 'Vivienda',      1, 'mensual'),
            (1, 'gasto',   'Alquiler mayo',              750.00, '2026-05-02', 'Vivienda',      1, 'mensual'),
            (1, 'gasto',   'Electricidad marzo',          62.40, '2026-03-15', 'Vivienda',      0, None),
            (1, 'gasto',   'Electricidad abril',          58.90, '2026-04-15', 'Vivienda',      0, None),
            # ── Gastos: Comida ────────────────────────────────────────────
            (1, 'gasto',   'Mercadona',                  102.30, '2026-03-05', 'Comida',        0, None),
            (1, 'gasto',   'Carrefour',                   74.20, '2026-03-18', 'Comida',        0, None),
            (1, 'gasto',   'Mercadona',                   88.10, '2026-04-08', 'Comida',        0, None),
            (1, 'gasto',   'Lidl',                        55.60, '2026-04-22', 'Comida',        0, None),
            (1, 'gasto',   'Mercadona',                   95.40, '2026-05-03', 'Comida',        0, None),
            (1, 'gasto',   'Carrefour',                   67.80, '2026-05-10', 'Comida',        0, None),
            # ── Gastos: Transporte ────────────────────────────────────────
            (1, 'gasto',   'Abono transporte marzo',      54.60, '2026-03-01', 'Transporte',    1, 'mensual'),
            (1, 'gasto',   'Abono transporte abril',      54.60, '2026-04-01', 'Transporte',    1, 'mensual'),
            (1, 'gasto',   'Abono transporte mayo',       54.60, '2026-05-01', 'Transporte',    1, 'mensual'),
            (1, 'gasto',   'Gasolina',                    58.00, '2026-03-09', 'Transporte',    0, None),
            (1, 'gasto',   'Gasolina',                    55.00, '2026-04-12', 'Transporte',    0, None),
            (1, 'gasto',   'Gasolina',                    60.00, '2026-05-06', 'Transporte',    0, None),
            # ── Gastos: Suscripciones ─────────────────────────────────────
            (1, 'gasto',   'Netflix',                     15.99, '2026-03-05', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'Netflix',                     15.99, '2026-04-05', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'Netflix',                     15.99, '2026-05-05', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'Spotify',                      9.99, '2026-03-08', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'Spotify',                      9.99, '2026-04-08', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'Spotify',                      9.99, '2026-05-08', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'iCloud 50 GB',                 0.99, '2026-03-12', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'iCloud 50 GB',                 0.99, '2026-04-12', 'Suscripciones', 1, 'mensual'),
            (1, 'gasto',   'iCloud 50 GB',                 0.99, '2026-05-12', 'Suscripciones', 1, 'mensual'),
            # ── Gastos: Ocio ──────────────────────────────────────────────
            (1, 'gasto',   'Concierto',                   35.00, '2026-03-15', 'Ocio',          0, None),
            (1, 'gasto',   'Cena cumpleaños',             45.00, '2026-04-20', 'Ocio',          0, None),
            (1, 'gasto',   'Escape room',                 22.00, '2026-04-27', 'Ocio',          0, None),
            (1, 'gasto',   'Cine',                        12.00, '2026-05-09', 'Ocio',          0, None),
            (1, 'gasto',   'Bar con amigos',              28.50, '2026-05-14', 'Ocio',          0, None),
            # ── Gastos: Salud ─────────────────────────────────────────────
            (1, 'gasto',   'Revisión médica',             80.00, '2026-04-10', 'Salud',         0, None),
            (1, 'gasto',   'Farmacia',                    23.50, '2026-05-12', 'Salud',         0, None),
            (1, 'gasto',   'Gafas nuevas',               180.00, '2026-03-25', 'Salud',         0, None),
            # ── Gastos: Ropa ──────────────────────────────────────────────
            (1, 'gasto',   'Zapatillas running',          79.99, '2026-04-18', 'Ropa',          0, None),
            (1, 'gasto',   'Chaqueta',                    49.99, '2026-03-22', 'Ropa',          0, None),
            # ── Gastos: Educación ─────────────────────────────────────────
            (1, 'gasto',   'Curso de Python',             29.99, '2026-03-10', 'Educación',     1, 'mensual'),
            (1, 'gasto',   'Curso de Python',             29.99, '2026-04-10', 'Educación',     1, 'mensual'),
            (1, 'gasto',   'Curso de Python',             29.99, '2026-05-10', 'Educación',     1, 'mensual'),
            (1, 'gasto',   'Libro Clean Code',            28.00, '2026-03-30', 'Educación',     0, None),
            # ── Gastos: Tecnología ────────────────────────────────────────
            (1, 'gasto',   'Teclado mecánico',            89.00, '2026-04-25', 'Tecnología',    0, None),
            (1, 'gasto',   'Cable HDMI',                  12.00, '2026-03-18', 'Tecnología',    0, None),
            (1, 'gasto',   'Ratón inalámbrico',           35.00, '2026-05-07', 'Tecnología',    0, None),
        ]
        conn.executemany(
            """INSERT INTO movimientos
               (usuario_id, tipo, descripcion, cantidad, fecha, categoria, recurrente, frecuencia)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            movimientos,
        )

        objetivos = [
            (1, 'Vacaciones de verano',  1500.00,  650.00, '2026-07-01'),
            (1, 'Fondo de emergencia',   5000.00, 2300.00, '2026-12-31'),
            (1, 'Nuevo ordenador',       1200.00,  480.00, '2026-09-30'),
        ]
        conn.executemany(
            """INSERT INTO objetivos_ahorro (usuario_id, nombre, cantidad_meta, cantidad_actual, fecha_limite)
               VALUES (?, ?, ?, ?, ?)""",
            objetivos,
        )

        presupuestos = [
            (1, 'Comida',        300.00, '2026-05'),
            (1, 'Transporte',    150.00, '2026-05'),
            (1, 'Ocio',           80.00, '2026-05'),
            (1, 'Suscripciones',  45.00, '2026-05'),
            (1, 'Salud',         150.00, '2026-05'),
            (1, 'Educación',      60.00, '2026-05'),
        ]
        conn.executemany(
            "INSERT INTO presupuestos (usuario_id, categoria, limite, mes) VALUES (?, ?, ?, ?)",
            presupuestos,
        )

        recurrentes_seed = [
            (1, 'ingreso', 'Nómina',            2200.00, 'Salario',       'mensual', '2026-06-01'),
            (1, 'gasto',   'Alquiler',            750.00, 'Vivienda',      'mensual', '2026-06-02'),
            (1, 'gasto',   'Netflix',              15.99, 'Suscripciones', 'mensual', '2026-06-05'),
            (1, 'gasto',   'Spotify',               9.99, 'Suscripciones', 'mensual', '2026-06-08'),
            (1, 'gasto',   'iCloud 50 GB',           0.99, 'Suscripciones', 'mensual', '2026-06-12'),
            (1, 'gasto',   'Abono transporte',      54.60, 'Transporte',    'mensual', '2026-06-01'),
            (1, 'gasto',   'Curso de Python',       29.99, 'Educación',     'mensual', '2026-06-10'),
        ]
        conn.executemany(
            """INSERT INTO recurrentes
               (usuario_id, tipo, descripcion, cantidad, categoria, frecuencia, proxima_fecha)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            recurrentes_seed,
        )
        conn.commit()


# --------------------------------------------------------------------------- #
# Usuarios                                                                     #
# --------------------------------------------------------------------------- #

def db_crear_usuario(nombre: str, email: str) -> dict:
    """
    Función para crear un nuevo usuario en la base de datos.
    Args:
        nombre (str): Nombre del usuario.
        email (str): Correo electrónico del usuario.
    Returns:
        dict: Diccionario con los datos del usuario creado.
    
    Raises:
        sqlite3.IntegrityError: Si ocurre un error de integridad en la base de datos.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (?, ?)",
            (nombre, email),
        )
        conn.commit()
        return {"id": cursor.lastrowid, "nombre": nombre, "email": email}


def db_obtener_usuarios() -> list[dict]:
    """
    Función para obtener todos los usuarios de la base de datos.
    Returns:
        list[dict]: Lista de diccionarios con los datos de cada usuario.
    """
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM usuarios").fetchall()
    return [dict(row) for row in rows]


def db_obtener_usuario(usuario_id: int) -> dict | None:
    """
    Función para obtener un usuario por su ID.
    Args:        
        usuario_id (int): ID del usuario a obtener.
    Returns:
        dict | None: Diccionario con los datos del usuario o None si no se encuentra.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    return dict(row) if row else None


def db_eliminar_usuario(usuario_id: int) -> bool:
    """
    Función para eliminar un usuario por su ID.
    Args:
        usuario_id (int): ID del usuario a eliminar.
    Returns:
        bool: True si el usuario fue eliminado, False si no se encontró.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
    return cursor.rowcount > 0


# --------------------------------------------------------------------------- #
# Movimientos                                                                  #
# --------------------------------------------------------------------------- #

def db_crear_movimiento(
    usuario_id: int,
    tipo: str,
    descripcion: str,
    cantidad: float,
    fecha: str,
    categoria: str,
    recurrente: bool = False,
    frecuencia: str | None = None,
) -> dict:
    """
    Función para crear un nuevo movimiento en la base de datos.
    Args:
        usuario_id (int): ID del usuario al que pertenece el movimiento.
        tipo (str): Tipo del movimiento ('ingreso' o 'gasto').
        descripcion (str): Descripción del movimiento.
        cantidad (float): Cantidad del movimiento.
        fecha (str): Fecha del movimiento en formato 'YYYY-MM-DD'.
        categoria (str): Categoría del movimiento.
        recurrente (bool): True si el movimiento es recurrente (por defecto False).
        frecuencia (str | None): Frecuencia de repetición si es recurrente (opcional).
    Returns:
        dict: Diccionario con los datos del movimiento creado.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO movimientos
               (usuario_id, tipo, descripcion, cantidad, fecha, categoria, recurrente, frecuencia, fecha_creacion)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (usuario_id, tipo, descripcion, cantidad, fecha, categoria, int(recurrente), frecuencia,
             datetime.now().isoformat(timespec='seconds')),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "usuario_id": usuario_id,
            "tipo": tipo,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "fecha": fecha,
            "categoria": categoria,
            "recurrente": recurrente,
            "frecuencia": frecuencia,
        }


def db_obtener_movimientos(
    usuario_id: int | None = None,
    tipo: str | None = None,
    categoria: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    recurrente: bool | None = None,
) -> list[dict]:
    """
    Función para obtener movimientos de la base de datos con filtros opcionales.
    Args:
        usuario_id (int | None): ID del usuario para filtrar movimientos (opcional).
        tipo (str | None): Tipo de movimiento para filtrar (ingreso o gasto) (opcional).
        categoria (str | None): Categoría para filtrar movimientos (opcional).
        fecha_desde (str | None): Fecha mínima para filtrar movimientos (opcional).
        fecha_hasta (str | None): Fecha máxima para filtrar movimientos (opcional).
        recurrente (bool | None): Si es True, solo devuelve movimientos recurrentes (opcional).
    Returns:
        list[dict]: Lista de diccionarios con los datos de cada movimiento que cumple los filtros.
    """
    query = "SELECT * FROM movimientos WHERE 1=1"
    params: list = []

    if usuario_id is not None:
        query += " AND usuario_id = ?"
        params.append(usuario_id)
    if tipo is not None:
        query += " AND tipo = ?"
        params.append(tipo)
    if categoria is not None:
        query += " AND categoria LIKE ?"
        params.append(f"%{categoria}%")
    if fecha_desde is not None:
        query += " AND fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta is not None:
        query += " AND fecha <= ?"
        params.append(fecha_hasta)
    if recurrente is not None:
        query += " AND recurrente = ?"
        params.append(1 if recurrente else 0)

    query += " ORDER BY fecha_creacion DESC, id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def db_obtener_movimiento(movimiento_id: int) -> dict | None:
    """
    Función para obtener un movimiento por su ID.
    Args:
        movimiento_id (int): ID del movimiento a obtener.
    Returns:
        dict | None: Diccionario con los datos del movimiento o None si no se encuentra.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM movimientos WHERE id = ?", (movimiento_id,)
        ).fetchone()
    return dict(row) if row else None


def db_eliminar_movimiento(movimiento_id: int) -> bool:
    """
    Función para eliminar un movimiento por su ID.
    Args:
        movimiento_id (int): ID del movimiento a eliminar.
    Returns:
        bool: True si el movimiento fue eliminado, False si no se encontró.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM movimientos WHERE id = ?", (movimiento_id,))
        conn.commit()
    return cursor.rowcount > 0


def db_actualizar_movimiento(movimiento_id: int, campos: dict) -> dict | None:
    """
    Función para actualizar los campos de un movimiento en la base de datos.
    Args:
        movimiento_id (int): ID del movimiento a actualizar.
        campos (dict): Diccionario con los campos y valores a actualizar.
    Returns:
        dict | None: Diccionario con los datos actualizados del movimiento o None si no se encontró.
    """
    allowed = {"tipo", "descripcion", "cantidad", "fecha", "categoria", "recurrente", "frecuencia"}
    updates = {k: v for k, v in campos.items() if k in allowed}
    if not updates:
        return db_obtener_movimiento(movimiento_id)
    if "recurrente" in updates:
        updates["recurrente"] = int(updates["recurrente"])
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [movimiento_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE movimientos SET {set_clause} WHERE id = ?", values)
        conn.commit()
    return db_obtener_movimiento(movimiento_id)


# --------------------------------------------------------------------------- #
# Presupuestos                                                                 #
# --------------------------------------------------------------------------- #

def db_crear_presupuesto(usuario_id: int, categoria: str, limite: float, mes: str) -> dict:
    """
    Función para crear un nuevo presupuesto en la base de datos.
    Args:
        usuario_id (int): ID del usuario propietario del presupuesto.
        categoria (str): Categoría a la que aplica el presupuesto.
        limite (float): Importe máximo de gasto permitido en el mes.
        mes (str): Mes al que aplica el presupuesto en formato 'YYYY-MM'.
    Returns:
        dict: Diccionario con los datos del presupuesto creado.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO presupuestos (usuario_id, categoria, limite, mes) VALUES (?, ?, ?, ?)",
            (usuario_id, categoria, limite, mes),
        )
        conn.commit()
        return {"id": cursor.lastrowid, "usuario_id": usuario_id,
                "categoria": categoria, "limite": limite, "mes": mes}


def db_obtener_presupuestos(usuario_id: int, mes: str | None = None) -> list[dict]:
    """
    Función para obtener los presupuestos de un usuario con filtro opcional por mes.
    Args:
        usuario_id (int): ID del usuario del que se obtienen los presupuestos.
        mes (str | None): Mes en formato 'YYYY-MM' para filtrar (opcional).
    Returns:
        list[dict]: Lista de diccionarios con los datos de cada presupuesto.
    """
    query = "SELECT * FROM presupuestos WHERE usuario_id = ?"
    params: list = [usuario_id]
    if mes:
        query += " AND mes = ?"
        params.append(mes)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def db_eliminar_presupuesto(presupuesto_id: int) -> bool:
    """
    Función para eliminar un presupuesto por su ID.
    Args:
        presupuesto_id (int): ID del presupuesto a eliminar.
    Returns:
        bool: True si el presupuesto fue eliminado, False si no se encontró.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM presupuestos WHERE id = ?", (presupuesto_id,))
        conn.commit()
    return cursor.rowcount > 0


# --------------------------------------------------------------------------- #
# Objetivos de ahorro                                                          #
# --------------------------------------------------------------------------- #

def db_crear_objetivo(usuario_id: int, nombre: str, cantidad_meta: float, fecha_limite: str) -> dict:
    """
    Función para crear un nuevo objetivo de ahorro en la base de datos.
    Args:
        usuario_id (int): ID del usuario propietario del objetivo.
        nombre (str): Nombre descriptivo del objetivo.
        cantidad_meta (float): Cantidad total a alcanzar.
        fecha_limite (str): Fecha límite en formato 'YYYY-MM-DD'.
    Returns:
        dict: Diccionario con los datos del objetivo creado.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO objetivos_ahorro (usuario_id, nombre, cantidad_meta, fecha_limite)
               VALUES (?, ?, ?, ?)""",
            (usuario_id, nombre, cantidad_meta, fecha_limite),
        )
        conn.commit()
        return {"id": cursor.lastrowid, "usuario_id": usuario_id, "nombre": nombre,
                "cantidad_meta": cantidad_meta, "cantidad_actual": 0.0, "fecha_limite": fecha_limite}


def db_obtener_objetivos(usuario_id: int) -> list[dict]:
    """
    Función para obtener todos los objetivos de ahorro de un usuario.
    Args:
        usuario_id (int): ID del usuario del que se obtienen los objetivos.
    Returns:
        list[dict]: Lista de diccionarios con los datos de cada objetivo, ordenados por fecha límite.
    """
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM objetivos_ahorro WHERE usuario_id = ? ORDER BY fecha_limite ASC",
            (usuario_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def db_obtener_objetivo(objetivo_id: int) -> dict | None:
    """
    Función para obtener un objetivo de ahorro por su ID.
    Args:
        objetivo_id (int): ID del objetivo a obtener.
    Returns:
        dict | None: Diccionario con los datos del objetivo o None si no se encontró.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM objetivos_ahorro WHERE id = ?", (objetivo_id,)
        ).fetchone()
    return dict(row) if row else None


def db_actualizar_aportacion(objetivo_id: int, nueva_cantidad: float) -> dict | None:
    """
    Función para actualizar la cantidad actual de un objetivo de ahorro.
    Args:
        objetivo_id (int): ID del objetivo a actualizar.
        nueva_cantidad (float): Nueva cantidad ahorrada acumulada.
    Returns:
        dict | None: Diccionario con los datos actualizados del objetivo o None si no se encontró.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE objetivos_ahorro SET cantidad_actual = ? WHERE id = ?",
            (nueva_cantidad, objetivo_id),
        )
        conn.commit()
    return db_obtener_objetivo(objetivo_id)


def db_eliminar_objetivo(objetivo_id: int) -> bool:
    """
    Función para eliminar un objetivo de ahorro por su ID.
    Args:
        objetivo_id (int): ID del objetivo a eliminar.
    Returns:
        bool: True si el objetivo fue eliminado, False si no se encontró.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM objetivos_ahorro WHERE id = ?", (objetivo_id,))
        conn.commit()
    return cursor.rowcount > 0


# --------------------------------------------------------------------------- #
# Categorías                                                                  #
# --------------------------------------------------------------------------- #

def db_obtener_categorias(usuario_id: int, tipo: str | None = None) -> list[dict]:
    """Devuelve las categorías por defecto más las personalizadas del usuario.
    Si se pasa tipo ('gasto' o 'ingreso'), filtra por él."""
    query = "SELECT * FROM categorias WHERE (usuario_id = 0 OR usuario_id = ?)"
    params: list = [usuario_id]
    if tipo is not None:
        query += " AND tipo = ?"
        params.append(tipo)
    query += " ORDER BY es_default DESC, nombre ASC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def db_crear_categoria(nombre: str, usuario_id: int, tipo: str) -> dict:
    """
    Función para crear una nueva categoría personalizada en la base de datos.
    Args:
        nombre (str): Nombre de la categoría.
        usuario_id (int): ID del usuario propietario de la categoría.
        tipo (str): Tipo de la categoría ('gasto' o 'ingreso').
    Returns:
        dict: Diccionario con los datos de la categoría creada.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO categorias (nombre, usuario_id, es_default, tipo) VALUES (?, ?, 0, ?)",
            (nombre, usuario_id, tipo),
        )
        conn.commit()
        return {"id": cursor.lastrowid, "nombre": nombre,
                "usuario_id": usuario_id, "es_default": False, "tipo": tipo}


def db_eliminar_categoria(categoria_id: int, usuario_id: int) -> str | None:
    """Elimina una categoría solo si no es de sistema.
    Reasigna previamente sus movimientos a 'Otros'.
    Devuelve el nombre eliminado, o None si no existía o era default."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT nombre FROM categorias WHERE id = ? AND es_default = 0",
            (categoria_id,),
        ).fetchone()
        if not row:
            return None
        nombre = row["nombre"]
        conn.execute(
            "UPDATE movimientos SET categoria = 'Otros' WHERE categoria = ? AND usuario_id = ?",
            (nombre, usuario_id),
        )
        conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        conn.commit()
    return nombre


# --------------------------------------------------------------------------- #
# Recurrentes                                                                  #
# --------------------------------------------------------------------------- #

def db_obtener_recurrentes(usuario_id: int) -> list[dict]:
    """
    Función para obtener todos los movimientos recurrentes de un usuario.
    Args:
        usuario_id (int): ID del usuario del que se obtienen los recurrentes.
    Returns:
        list[dict]: Lista de diccionarios con los datos de cada movimiento recurrente.
    """
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM recurrentes WHERE usuario_id = ? ORDER BY tipo, descripcion",
            (usuario_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def db_crear_recurrente(
    usuario_id: int, tipo: str, descripcion: str, cantidad: float,
    categoria: str, frecuencia: str, proxima_fecha: str,
) -> dict:
    """
    Función para crear un nuevo movimiento recurrente en la base de datos.
    Args:
        usuario_id (int): ID del usuario propietario del recurrente.
        tipo (str): Tipo del movimiento ('ingreso' o 'gasto').
        descripcion (str): Descripción del movimiento recurrente.
        cantidad (float): Cantidad del movimiento.
        categoria (str): Categoría del movimiento.
        frecuencia (str): Frecuencia de repetición ('semanal' o 'mensual').
        proxima_fecha (str): Fecha de la próxima ejecución en formato 'YYYY-MM-DD'.
    Returns:
        dict: Diccionario con los datos del movimiento recurrente creado.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO recurrentes
               (usuario_id, tipo, descripcion, cantidad, categoria, frecuencia, proxima_fecha)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (usuario_id, tipo, descripcion, cantidad, categoria, frecuencia, proxima_fecha),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM recurrentes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


def db_editar_recurrente(recurrente_id: int, campos: dict) -> dict | None:
    """
    Función para editar los campos de un movimiento recurrente en la base de datos.
    Args:
        recurrente_id (int): ID del movimiento recurrente a editar.
        campos (dict): Diccionario con los campos y valores a actualizar.
    Returns:
        dict | None: Diccionario con los datos actualizados del recurrente o None si no se encontró.
    """
    if not campos:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM recurrentes WHERE id = ?", (recurrente_id,)).fetchone()
        return dict(row) if row else None
    sets = ', '.join(f"{k} = ?" for k in campos)
    values = list(campos.values()) + [recurrente_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE recurrentes SET {sets} WHERE id = ?", values)
        conn.commit()
        row = conn.execute("SELECT * FROM recurrentes WHERE id = ?", (recurrente_id,)).fetchone()
    return dict(row) if row else None


def db_eliminar_recurrente(recurrente_id: int) -> bool:
    """
    Función para eliminar un movimiento recurrente por su ID.
    Args:
        recurrente_id (int): ID del movimiento recurrente a eliminar.
    Returns:
        bool: True si el recurrente fue eliminado, False si no se encontró.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM recurrentes WHERE id = ?", (recurrente_id,))
        conn.commit()
    return cursor.rowcount > 0


def db_generar_movimientos_recurrentes(usuario_id: int) -> int:
    """
    Función que genera los movimientos pendientes de todos los recurrentes del usuario.
    Args:
        usuario_id (int): ID del usuario cuyos movimientos recurrentes se generan.
    Returns:
        int: Número de movimientos generados.
    """
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta

    hoy = date.today().isoformat()
    generados = 0

    with get_connection() as conn:
        recurrentes = conn.execute(
            "SELECT * FROM recurrentes WHERE usuario_id = ?", (usuario_id,)
        ).fetchall()

        for r in recurrentes:
            proxima = r['proxima_fecha']
            while proxima <= hoy:
                conn.execute(
                    """INSERT INTO movimientos
                       (usuario_id, tipo, descripcion, cantidad, fecha, categoria, recurrente, frecuencia)
                       VALUES (?, ?, ?, ?, ?, ?, 1, ?)""",
                    (r['usuario_id'], r['tipo'], r['descripcion'],
                     r['cantidad'], proxima, r['categoria'], r['frecuencia']),
                )
                generados += 1
                d = date.fromisoformat(proxima)
                proxima = (d + timedelta(weeks=1) if r['frecuencia'] == 'semanal'
                           else d + relativedelta(months=1)).isoformat()

            if proxima != r['proxima_fecha']:
                conn.execute(
                    "UPDATE recurrentes SET proxima_fecha = ? WHERE id = ?",
                    (proxima, r['id']),
                )
        conn.commit()
    return generados
