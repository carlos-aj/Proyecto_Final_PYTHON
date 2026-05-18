# Manual de usuario — Gestor de Gastos

Bienvenido a tu gestor de finanzas personal. Esta guía te explica todo lo que puedes hacer con la aplicación, pantalla por pantalla, sin rodeos.

> **Nota:** La aplicación incluye datos de demostración precargados (movimientos de los últimos tres meses, objetivos de ahorro con progreso, presupuestos mensuales y movimientos recurrentes) con el fin de facilitar la visualización de todas las funcionalidades del proyecto desde el primer arranque.

---

## Cómo navegar

En la parte superior siempre verás la barra de navegación con cinco secciones:

| Sección | Para qué sirve |
|---------|----------------|
| **Dashboard** | Resumen rápido de tu situación financiera |
| **Movimientos** | Registrar y consultar todos tus movimientos |
| **Recurrentes** | Ver y gestionar nóminas, suscripciones, etc. |
| **Estadísticas** | Gráficos, presupuestos y análisis por categoría |
| **Objetivos** | Metas de ahorro con seguimiento de progreso |

La sección activa se resalta en azul.

---

## Movimientos

Esta es la sección principal. Aquí apuntas todo lo que entra y sale.

### Añadir un movimiento

1. Elige si es un **Ingreso** (verde) o un **Gasto** (rojo) con los botones de arriba del formulario.
2. Escribe una **descripción** (p. ej. "Compra supermercado").
3. Selecciona la **categoría** — el desplegable solo muestra las categorías del tipo elegido (gastos o ingresos por separado).
4. Introduce la **cantidad** en euros.
5. Confirma la **fecha** (por defecto aparece la de hoy).
6. Pulsa el botón de añadir.

Cuando se guarda correctamente aparece un pequeño aviso en pantalla con el tipo, la descripción y el importe.

### Editar un movimiento

En la lista del historial, pulsa el icono de lápiz del movimiento que quieras cambiar. Se abrirá un modal donde puedes modificar la descripción, la categoría, la cantidad y la fecha. Pulsa **Guardar cambios** cuando termines.

### Eliminar un movimiento

Pulsa el icono de papelera en la fila del movimiento. Se eliminará directamente.

### Filtrar el historial

Puedes filtrar los movimientos por fecha, tipo (ingreso/gasto) y categoría para encontrar lo que buscas más rápido.

---

## Categorías

El panel de categorías está en la columna derecha de la pantalla de Movimientos.

- Hay dos pestañas: **Gastos** e **Ingresos** — cada tipo tiene sus propias categorías.
- Las categorías que vienen por defecto aparecen en azul claro y **no se pueden eliminar**.
- Puedes crear tus propias categorías pulsando **+ Nueva**, escribiendo el nombre y confirmando con **Añadir**.
- Para eliminar una categoría personalizada, pulsa la **x** que aparece sobre su etiqueta. Se te pedirá confirmación antes de borrarla — los movimientos que tuvieran esa categoría pasarán automáticamente a "Otros".

---

## Recurrentes

Esta sección gestiona **plantillas** de gastos e ingresos que se repiten periódicamente. Cuando cargas la página, la aplicación revisa automáticamente qué plantillas tienen fecha vencida y genera los movimientos correspondientes en el historial.

- Dos pestañas: **Ingresos** y **Gastos**, cada una con un contador.
- Cada tarjeta muestra la descripción, la categoría, la próxima fecha de generación, la frecuencia (semanal o mensual) y el importe.

### Crear un recurrente

Pulsa **+ Nuevo recurrente**. En el modal elige el tipo (ingreso/gasto), escribe la descripción, selecciona la categoría, introduce la cantidad, la frecuencia y la fecha a partir de la cual debe empezar a generarse.

### Editar un recurrente

Pulsa el icono de lápiz. Puedes cambiar cualquier campo, incluida la próxima fecha de generación.

### Eliminar un recurrente

Pulsa el icono de papelera. Aparecerá un modal de confirmación. Al confirmar, la plantilla se elimina pero los movimientos ya generados en el historial no se ven afectados.

---

## Estadísticas

### Gastos por categoría

Un desglose visual de en qué categorías estás gastando más. Cada fila muestra la cantidad gastada y, si tienes un presupuesto configurado para esa categoría, también el límite. La barra de progreso cambia de color:

- **Verde** — dentro del presupuesto
- **Naranja** — has gastado más del 80 %
- **Rojo** — has superado el presupuesto

### Gráfico mensual

Un gráfico de barras que compara tus ingresos (verde) y gastos (rojo) mes a mes. Pasa el ratón por encima de las barras para ver los valores exactos.

### Presupuestos

Puedes asignar un límite de gasto mensual a cualquier categoría de gasto:

1. Pulsa **+ Nuevo**.
2. Elige la **categoría**, el **límite** en euros y el **mes** al que aplica.
3. Pulsa **Guardar**.

El presupuesto aparecerá en la lista con una barra de progreso que se actualiza automáticamente según lo que hayas gastado en esa categoría ese mes. Para eliminar un presupuesto, pulsa la **x** a la derecha de la fila.

---

## Objetivos de ahorro

Sirve para marcarte metas: un viaje, un fondo de emergencia, cambiar de móvil…

### Crear un objetivo

1. Pulsa **+ Nuevo objetivo**.
2. Ponle un **nombre** (p. ej. "Vacaciones de verano").
3. Indica la **cantidad meta** en euros.
4. Elige una **fecha límite**.
5. Pulsa **Crear objetivo**.

### Hacer una aportación

Cuando tengas dinero disponible, pulsa **+ Aportación** en la tarjeta del objetivo, introduce la cantidad y confirma. La barra de progreso se actualiza al instante.

### Estados de un objetivo

- La barra es **azul** mientras estás progresando.
- Cuando alcanzas el 100 %, la barra se vuelve **verde** y aparece el badge "Completado".
- Si quedan menos de 30 días para la fecha límite, el contador de días aparece en **naranja** como aviso.

### Eliminar un objetivo

Pulsa **Eliminar** en la tarjeta. Se pedirá confirmación antes de borrarlo.

---

## Importar y exportar datos

En la pantalla de Movimientos, en el panel de la derecha, tienes tres botones:

| Botón | Función |
|-------|---------|
| **Exportar JSON** | Descarga todos tus movimientos en formato `.json` |
| **Importar JSON** | Carga movimientos desde un archivo `.json` exportado previamente |
| **Exportar CSV** | Descarga los datos en formato `.csv`, compatible con Excel y hojas de cálculo |

Después de importar, verás un mensaje indicando cuántos movimientos se añadieron y si hubo algún error.

---

## Consejos rápidos

- Cambia el **tipo de movimiento** (ingreso/gasto) antes de seleccionar la categoría — el desplegable se actualiza automáticamente.
- Si creas una categoría que ya existe con el mismo nombre, la aplicación te avisará.
- Los presupuestos son **por mes**: puedes tener uno diferente para cada categoría en cada mes.
- Los recurrentes generan movimientos **automáticamente** al cargar la sección Recurrentes: si la próxima fecha ya ha pasado, se crea el movimiento en el historial y la fecha avanza al siguiente período.
