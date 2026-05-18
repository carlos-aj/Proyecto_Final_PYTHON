import axios from 'axios'

const USUARIO_ID = 1

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// ── Movimientos ────────────────────────────────────────────────────────────────

export function getMovimientos({ tipo, categoria, fechaDesde, fechaHasta } = {}) {
  return api.get('/movimientos', {
    params: {
      usuario_id: USUARIO_ID,
      ...(tipo && { tipo }),
      ...(categoria && { categoria }),
      ...(fechaDesde && { fecha_desde: fechaDesde }),
      ...(fechaHasta && { fecha_hasta: fechaHasta }),
    },
  })
}

export function crearIngreso({ descripcion, cantidad, fecha, categoria, recurrente = false, frecuencia = null }) {
  return api.post('/ingresos', {
    usuario_id: USUARIO_ID,
    tipo: 'ingreso',
    descripcion,
    cantidad: parseFloat(cantidad),
    fecha,
    categoria,
    recurrente,
    ...(frecuencia && { frecuencia }),
  })
}

export function crearGasto({ descripcion, cantidad, fecha, categoria, recurrente = false, frecuencia = null }) {
  return api.post('/gastos', {
    usuario_id: USUARIO_ID,
    tipo: 'gasto',
    descripcion,
    cantidad: parseFloat(cantidad),
    fecha,
    categoria,
    recurrente,
    ...(frecuencia && { frecuencia }),
  })
}

export function eliminarMovimiento(id) {
  return api.delete(`/movimientos/${id}`)
}

export function editarMovimiento(id, data) {
  return api.put(`/movimientos/${id}`, data)
}

// ── Recurrentes ───────────────────────────────────────────────────────────────

export function getRecurrentes() {
  return api.get('/recurrentes', { params: { usuario_id: USUARIO_ID } })
}

export function crearRecurrente(data) {
  return api.post('/recurrentes', { ...data, usuario_id: USUARIO_ID })
}

export function editarRecurrente(id, data) {
  return api.put(`/recurrentes/${id}`, data)
}

export function eliminarRecurrente(id) {
  return api.delete(`/recurrentes/${id}`)
}

// ── Estadísticas ───────────────────────────────────────────────────────────────

export function getBalance() {
  return api.get('/estadisticas/balance', { params: { usuario_id: USUARIO_ID } })
}

export function getCategoriasStats() {
  return api.get('/estadisticas/categorias', { params: { usuario_id: USUARIO_ID } })
}

// ── JSON ───────────────────────────────────────────────────────────────────────

export function exportarJson() {
  return api.get('/exportar-json', { params: { usuario_id: USUARIO_ID } })
}

export function importarJson(datos) {
  return api.post('/importar-json', datos, { params: { usuario_id: USUARIO_ID } })
}

export function exportarCSV() {
  return api.get('/exportar-csv', {
    params: { usuario_id: USUARIO_ID },
    responseType: 'blob',
  })
}

// ── Presupuestos ───────────────────────────────────────────────────────────────

export function getPresupuestos(mes = null) {
  return api.get('/presupuestos', {
    params: { usuario_id: USUARIO_ID, ...(mes && { mes }) },
  })
}

export function crearPresupuesto({ categoria, limite, mes }) {
  return api.post('/presupuestos', { usuario_id: USUARIO_ID, categoria, limite: parseFloat(limite), mes })
}

export function eliminarPresupuesto(id) {
  return api.delete(`/presupuestos/${id}`)
}

// ── Objetivos ──────────────────────────────────────────────────────────────────

export function getObjetivos() {
  return api.get('/objetivos', { params: { usuario_id: USUARIO_ID } })
}

export function crearObjetivo({ nombre, cantidad_meta, fecha_limite }) {
  return api.post('/objetivos', { usuario_id: USUARIO_ID, nombre, cantidad_meta: parseFloat(cantidad_meta), fecha_limite })
}

export function aportarObjetivo(id, cantidad) {
  return api.put(`/objetivos/${id}/aportacion`, { cantidad: parseFloat(cantidad) })
}

export function eliminarObjetivo(id) {
  return api.delete(`/objetivos/${id}`)
}

// ── Categorías ───────────────────────────────────────────────────────────────────

export function getCategorias(tipo = null) {
  const params = { usuario_id: USUARIO_ID }
  if (tipo) params.tipo = tipo
  return api.get('/categorias', { params })
}

export function crearCategoria(nombre, tipo) {
  return api.post('/categorias', { usuario_id: USUARIO_ID, nombre, tipo })
}

export function eliminarCategoria(id) {
  return api.delete(`/categorias/${id}`, { params: { usuario_id: USUARIO_ID } })
}
