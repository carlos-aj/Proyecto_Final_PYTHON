# Gestor de Gastos Personales

Aplicación web para gestionar ingresos y gastos personales con estadísticas y gráficas.

- **Backend**: Python 3.11+ · FastAPI · SQLite
- **Frontend**: Vue 3 · Vite · Chart.js

---

## Requisitos previos

### Python (3.11 o superior)

```bash
python3 --version
```

> Python 3.13 es compatible. Si usas una versión anterior a 3.11 descarga el instalador desde [python.org](https://www.python.org/downloads/).

### Node.js (18 o superior)

```bash
node --version
```

> Si no tienes Node.js, descarga el instalador LTS desde [nodejs.org](https://nodejs.org) y ejecútalo.  
> En macOS con Homebrew: `brew install node`

### pnpm (gestor de paquetes para el frontend)

```bash
pnpm --version
```

> Si no tienes pnpm, instálalo una vez con:
> ```bash
> npm install -g pnpm
> ```

---

## Instalación y arranque

### 1. Clonar / descomprimir el proyecto y entrar en la carpeta

```bash
cd proyecto_final_PYTHON
```

### 2. Backend

Abre una terminal, entra en la carpeta `backend` **desde la raíz del proyecto**:

```bash
cd proyecto_final_PYTHON/backend
```

Crea un entorno virtual e instala las dependencias:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **macOS**: el sistema bloquea `pip3` fuera de un entorno virtual (PEP 668). El entorno virtual (`venv`) es obligatorio.

Arranca el servidor:

```bash
uvicorn app.main:app --reload
```

El backend quedará escuchando en **http://localhost:8000**.  
La base de datos `database.db` se crea automáticamente al primer arranque.

> **La próxima vez que abras el proyecto** recuerda activar el entorno antes de arrancar:
> ```bash
> cd proyecto_final_PYTHON/backend
> source venv/bin/activate
> uvicorn app.main:app --reload
> ```

> **Error "Address already in use"**: el puerto 8000 ya está ocupado. Libéralo con:
> ```bash
> kill -9 $(lsof -t -i:8000)
> ```
> Y vuelve a ejecutar `uvicorn`.

### 3. Frontend (en otra terminal)

Abre una **nueva** terminal, entra en `frontend` e instala las dependencias:

```bash
cd frontend
pnpm install
```

Arranca el servidor de desarrollo:

```bash
pnpm run dev
```

El frontend quedará disponible en **http://localhost:5173**.

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
