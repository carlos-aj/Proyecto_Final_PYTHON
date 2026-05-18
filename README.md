# Gestor de Gastos Personales

Aplicación web para gestionar ingresos y gastos personales con estadísticas y gráficas.

- **Backend**: Python 3.11+ · FastAPI · SQLite
- **Frontend**: Vue 3 · Vite · Chart.js

---

## Requisitos previos

| Herramienta | Versión mínima | Verificar |
|-------------|---------------|-----------|
| Python      | 3.11          | `python3 --version` |
| pip         | incluido      | `pip3 --version` |
| Node.js     | 18            | `node --version` |
| pnpm        | 8             | `pnpm --version` |

> **Python 3.13**: compatible, pero pip necesitará descargar una versión de pydantic ≥ 2.9 (lo hace automáticamente). Si prefieres evitar posibles problemas, usa **Python 3.11 o 3.12**.

> Si no tienes pnpm: `npm install -g pnpm`

---

## Instalación y arranque

### 1. Clonar / descomprimir el proyecto

```bash
cd proyecto_final_PYTHON
```

### 2. Backend

```bash
cd backend

# Instalar dependencias Python
pip3 install -r requirements.txt

# Arrancar el servidor (queda escuchando en http://localhost:8000)
uvicorn app.main:app --reload
```

> La base de datos `database.db` se crea automáticamente al primer arranque.

### 3. Frontend (en otra terminal)

```bash
cd frontend

# Instalar dependencias Node
pnpm install

# Arrancar el servidor de desarrollo (http://localhost:5173)
pnpm run dev
```

---

## Uso

| URL | Descripción |
|-----|-------------|
| http://localhost:5173 | Aplicación web |
| http://localhost:8000/docs | Documentación interactiva de la API (Swagger UI) |

> Al primer arranque la base de datos se crea automáticamente, se inserta el usuario de demo y se cargan datos de ejemplo en todas las secciones (movimientos de los últimos tres meses, recurrentes, objetivos de ahorro con progreso y presupuestos mensuales). No es necesario ningún paso adicional.

---

## Estructura del proyecto

```
proyecto_final_PYTHON/
├── backend/
│   ├── app/
│   │   ├── models/        ← Clases OOP (Movimiento, Ingreso, Gasto, Usuario)
│   │   ├── database/      ← Conexión SQLite y operaciones CRUD
│   │   ├── schemas/       ← Validación de datos con Pydantic
│   │   ├── services/      ← Lógica de negocio
│   │   ├── routes/        ← Endpoints de la API REST
│   │   └── main.py        ← Punto de entrada FastAPI
│   ├── requirements.txt
│   └── database.db        ← Generado automáticamente
│
└── frontend/
    ├── src/
    │   ├── components/    ← NavBar, MovimientoForm, CategoriaSelect, etc.
    │   ├── views/         ← Dashboard, Movimientos, Recurrentes, Estadísticas, Objetivos
    │   ├── services/      ← Llamadas a la API con Axios
    │   └── router/        ← Rutas de Vue Router
    └── package.json
```

---

## Funcionalidades

- Registrar ingresos y gastos con categoría, fecha y descripción
- Editar y eliminar movimientos desde el historial
- Filtrar historial por tipo, categoría y rango de fechas
- Gestionar plantillas de gastos e ingresos recurrentes con generación automática de movimientos al llegar su fecha
- Gestionar categorías personalizadas separadas por tipo (gastos / ingresos)
- Ver balance total y estadísticas de gastos por categoría con barras de progreso
- Gráfica de barras de ingresos vs gastos por mes
- Definir presupuestos mensuales por categoría y controlar su consumo en tiempo real
- Crear objetivos de ahorro con fecha límite, registrar aportaciones y seguir el progreso
- Importar y exportar movimientos en formato JSON
- Exportar movimientos en formato CSV
