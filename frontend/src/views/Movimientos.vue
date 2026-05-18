<template>
  <div class="view">
    <h2>Movimientos</h2>

    <div class="layout">
      <!-- Formulario -->
      <MovimientoForm @creado="onCreado" @categoria-creada="onCategoriaCreada" />

      <!-- Columna derecha: JSON + Categorias -->
      <div class="right-col">
        <!-- Importar / Exportar JSON -->
      <div class="card json-panel">
        <h3>Datos JSON</h3>

        <div class="json-action">
          <div class="json-icon export-icon"><Download :size="18" /></div>
          <div class="json-info">
            <span class="json-title">Exportar</span>
            <span class="json-desc">Descarga todos los movimientos como .json</span>
          </div>
          <button class="json-btn export-btn" @click="exportar">Exportar</button>
        </div>

        <div class="json-divider"></div>

        <div class="json-action">
          <div class="json-icon import-icon"><Upload :size="18" /></div>
          <div class="json-info">
            <span class="json-title">Importar</span>
            <span class="json-desc">Carga movimientos desde un archivo .json</span>
          </div>
          <label class="json-btn import-btn">
            Importar
            <input type="file" accept=".json" @change="importar" hidden />
          </label>
        </div>

        <div class="json-divider"></div>

        <div class="json-action">
          <div class="json-icon csv-icon"><FileText :size="18" /></div>
          <div class="json-info">
            <span class="json-title">Exportar CSV</span>
            <span class="json-desc">Descarga todos los movimientos como .csv</span>
          </div>
          <button class="json-btn csv-btn" @click="exportarCSVBtn">Exportar</button>
        </div>

        <div v-if="jsonMsg" class="json-msg">{{ jsonMsg }}</div>
      </div>

        <!-- Gestor de categorías -->
        <div class="card cat-panel">
          <div class="cat-panel-header">
            <h3>Categorías</h3>
            <div class="cat-tabs">
              <button class="cat-tab" :class="{ active: catFiltroTipo === 'gasto' }" @click="catFiltroTipo = 'gasto'">Gastos</button>
              <button class="cat-tab" :class="{ active: catFiltroTipo === 'ingreso' }" @click="catFiltroTipo = 'ingreso'">Ingresos</button>
            </div>
            <button class="cat-panel-toggle" @click="showCatForm = !showCatForm">
              {{ showCatForm ? 'Cancelar' : '+ Nueva' }}
            </button>
          </div>

          <Transition name="slide">
            <div v-if="showCatForm" class="cat-new-form">
              <div class="cat-new-row">
                <input
                  v-model="newCatNombre"
                  class="cat-new-input"
                  :placeholder="`Nombre de categoría de ${catFiltroTipo}…`"
                  maxlength="50"
                  @keydown.enter.prevent="crearCat"
                  @keydown.escape="showCatForm = false"
                />
                <button class="cat-new-ok" @click="crearCat" :disabled="catLoading">
                  {{ catLoading ? '…' : 'Añadir' }}
                </button>
              </div>
            </div>
          </Transition>
          <p v-if="catError" class="cat-error">{{ catError }}</p>

          <div class="cat-chips">
            <span
              v-for="c in categoriasActivas"
              :key="c.id"
              class="cat-chip"
              :class="{ 'cat-chip-default': c.es_default }"
            >
              {{ c.nombre }}
              <button
                v-if="!c.es_default"
                class="cat-chip-del"
                @click="pedirConfirmarCat(c)"
                title="Eliminar"
              >&times;</button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Lista con filtros -->
    <div class="card">
      <h3>Historial de movimientos</h3>
      <MovimientosList
        :movimientos="movimientos"
        :show-filters="true"
        :show-delete="true"
        @filtrar="aplicarFiltros"
        @eliminar="eliminar"
        @editar="abrirEditar"
      />
    </div>

    <!-- Modal edición -->
    <div v-if="editMov" class="modal-overlay" @click.self="editMov = null">
      <div class="modal-card">
        <h3>Editar movimiento</h3>
        <div class="field">
          <label>Descripción</label>
          <input v-model="editForm.descripcion" />
        </div>
        <div class="form-row">
          <div class="field">
            <label>Categoría</label>
            <CategoriaSelect v-model="editForm.categoria" :tipo="editForm.tipo" @categoria-creada="onCategoriaCreada" />
          </div>
          <div class="field">
            <label>Cantidad (€)</label>
            <input v-model.number="editForm.cantidad" type="number" min="0" step="0.01" />
          </div>
        </div>
        <div class="field half">
          <label>Fecha</label>
          <input v-model="editForm.fecha" type="date" />
        </div>
        <div class="modal-actions">
          <button class="modal-cancel" @click="editMov = null">Cancelar</button>
          <button class="modal-save" @click="guardarEdicion" :disabled="editLoading">
            {{ editLoading ? 'Guardando…' : 'Guardar cambios' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal de confirmación: eliminar categoría -->
  <Transition name="modal">
    <div v-if="confirmarCat" class="modal-backdrop" @click.self="confirmarCat = null">
      <div class="modal-box confirm-cat-modal">
        <h3>¿Eliminar categoría?</h3>
        <p>Se eliminará <strong>{{ confirmarCat.nombre }}</strong>. Los movimientos con esta categoría pasarán a "Otros".</p>
        <div class="confirm-actions">
          <button class="modal-cancel" @click="confirmarCat = null">Cancelar</button>
          <button class="btn-danger-confirm" @click="confirmarEliminarCat">Eliminar</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Download, Upload, FileText } from 'lucide-vue-next'
import MovimientoForm from '../components/MovimientoForm.vue'
import MovimientosList from '../components/MovimientosList.vue'
import CategoriaSelect from '../components/CategoriaSelect.vue'
import {
  getMovimientos,
  eliminarMovimiento,
  editarMovimiento,
  exportarJson,
  importarJson,
  exportarCSV,
  getCategorias,
  crearCategoria,
  eliminarCategoria,
} from '../services/api.js'

const movimientos  = ref([])
const jsonMsg      = ref('')
const editMov      = ref(null)
const editForm     = ref({})
const editLoading  = ref(false)
const categorias   = ref([])
const catFiltroTipo = ref('gasto')
const categoriasActivas = computed(() => categorias.value.filter(c => c.tipo === catFiltroTipo.value))
const showCatForm  = ref(false)
const newCatNombre = ref('')
const catLoading   = ref(false)
const catError     = ref('')
const confirmarCat = ref(null)

async function cargarCategorias() {
  const { data } = await getCategorias()
  categorias.value = data
}

async function crearCat() {
  const nombre = newCatNombre.value.trim()
  if (!nombre) return
  catLoading.value = true
  catError.value = ''
  try {
    const { data } = await crearCategoria(nombre, catFiltroTipo.value)
    categorias.value.push(data)
    newCatNombre.value = ''
    showCatForm.value = false
  } catch (e) {
    catError.value = e.response?.data?.detail ?? 'Error al crear categoría.'
  } finally {
    catLoading.value = false
  }
}

function pedirConfirmarCat(c) {
  confirmarCat.value = c
}

async function confirmarEliminarCat() {
  const id = confirmarCat.value.id
  confirmarCat.value = null
  await eliminarCat(id)
}

async function eliminarCat(id) {
  try {
    await eliminarCategoria(id)
    categorias.value = categorias.value.filter(c => c.id !== id)
    await cargar()   // algunos movimientos cambiaron a "Otros"
  } catch (e) {
    catError.value = e.response?.data?.detail ?? 'Error al eliminar categoría.'
  }
}

async function cargar(filtros = {}) {
  const { data } = await getMovimientos(filtros)
  movimientos.value = data
}

function onCreado() {
  cargar()
}

function onCategoriaCreada(cat) {
  if (!categorias.value.find(c => c.id === cat.id)) {
    categorias.value.push(cat)
  }
}

async function aplicarFiltros(filtros) {
  await cargar(filtros)
}

async function eliminar(id) {
  await eliminarMovimiento(id)
  movimientos.value = movimientos.value.filter(m => m.id !== id)
}

async function exportar() {
  const { data } = await exportarJson()
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = 'gastos.json'
  a.click()
  URL.revokeObjectURL(url)
}

async function importar(event) {
  const file = event.target.files[0]
  if (!file) return
  try {
    const texto = await file.text()
    const datos = JSON.parse(texto)
    const { data } = await importarJson(datos)
    jsonMsg.value = `Importados: ${data.importados} movimiento(s). Errores: ${data.errores.length}`
    await cargar()
  } catch {
    jsonMsg.value = 'Error al importar el archivo.'
  }
  event.target.value = ''
}

async function exportarCSVBtn() {
  const { data } = await exportarCSV()
  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'movimientos.csv'
  a.click()
  URL.revokeObjectURL(url)
}

function abrirEditar(mov) {
  editMov.value = mov
  editForm.value = { descripcion: mov.descripcion, categoria: mov.categoria, cantidad: mov.cantidad, fecha: mov.fecha, tipo: mov.tipo }
}

async function guardarEdicion() {
  editLoading.value = true
  try {
    const { data } = await editarMovimiento(editMov.value.id, editForm.value)
    const idx = movimientos.value.findIndex(m => m.id === data.id)
    if (idx !== -1) movimientos.value[idx] = data
    editMov.value = null
  } finally {
    editLoading.value = false
  }
}

onMounted(() => { cargar(); cargarCategorias() })
</script>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1.5rem; }
h2 { color: #f1f5f9; margin: 0; }
h3 { color: #cbd5e1; margin: 0 0 1rem; font-size: 1rem; }

.layout { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; align-items: start; }
.right-col { display: flex; flex-direction: column; gap: 1rem; }

.card { background: #1e293b; border-radius: 12px; padding: 1.5rem; }

.json-panel {
  display: flex;
  flex-direction: column;
  gap: 0;
  border-top: 3px solid #334155;
}

.json-action {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.6rem 0;
}

.json-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.export-icon { background: rgba(14,165,233,0.12); color: #38bdf8; }
.import-icon { background: rgba(139,92,246,0.12); color: #a78bfa; }

.json-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}
.json-title { color: #e2e8f0; font-size: 0.875rem; font-weight: 600; }
.json-desc  { color: #64748b; font-size: 0.75rem; }

.json-btn {
  padding: 0.4rem 0.9rem;
  border-radius: 7px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.15s;
  flex-shrink: 0;
}
.json-btn:hover { opacity: 0.8; }
.export-btn {
  background: rgba(14,165,233,0.12);
  color: #38bdf8;
  border: 1px solid rgba(14,165,233,0.25);
}
.import-btn {
  background: rgba(139,92,246,0.12);
  color: #a78bfa;
  border: 1px solid rgba(139,92,246,0.25);
  display: flex;
  align-items: center;
}
.csv-icon { background: rgba(16,185,129,0.12); color: #34d399; }
.csv-btn {
  background: rgba(16,185,129,0.12);
  color: #34d399;
  border: 1px solid rgba(16,185,129,0.25);
}

.json-divider { height: 1px; background: #334155; margin: 0.15rem 0; opacity: 0.4; }

.json-msg {
  background: #0f172a;
  border-radius: 8px;
  padding: 0.6rem 0.875rem;
  color: #94a3b8;
  font-size: 0.82rem;
  margin-top: 0.5rem;
  border-left: 3px solid #334155;
}

/* Modal edición */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal-card {
  background: #1e293b;
  border-radius: 14px;
  padding: 1.75rem;
  width: 420px;
  max-width: 95vw;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-top: 3px solid #6366f1;
}
.modal-card h3 { color: #f1f5f9; margin: 0; font-size: 1rem; }
.modal-card .field { display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
.modal-card .form-row { display: flex; gap: 0.75rem; }
.modal-card .half { flex: none; width: 170px; }
.modal-card label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }
.modal-card input { padding: 0.6rem 0.75rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #f1f5f9; font-size: 0.9rem; }
.modal-card input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.modal-actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 0.25rem; }
.modal-cancel {
  padding: 0.55rem 1.1rem; border-radius: 8px; border: 1px solid #334155;
  background: transparent; color: #94a3b8; font-size: 0.88rem; cursor: pointer;
}
.modal-cancel:hover { background: #334155; }
.modal-save {
  padding: 0.55rem 1.1rem; border-radius: 8px; border: none;
  background: #6366f1; color: #fff; font-size: 0.88rem; font-weight: 600; cursor: pointer;
}
.modal-save:hover:not(:disabled) { opacity: 0.85; }
.modal-save:disabled { opacity: 0.4; cursor: not-allowed; }

.cat-panel { border-top: 3px solid #334155; }
.cat-panel-header { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.75rem; }
.cat-panel-header h3 { margin: 0; flex: none; }
.cat-tabs { display: flex; gap: 2px; background: #0f172a; border-radius: 8px; padding: 3px; flex: 1; }
.cat-tab {
  flex: 1; padding: 0.25rem 0; border-radius: 6px; border: none;
  background: transparent; color: #64748b; font-size: 0.8rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.cat-tab:hover:not(.active) { color: #94a3b8; }
.cat-tab.active { background: #1e293b; color: #f1f5f9; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
.cat-tab:first-child.active { color: #f87171; }
.cat-tab:last-child.active  { color: #4ade80; }
.cat-panel-toggle {
  padding: 0.3rem 0.8rem; border-radius: 7px; border: 1px solid #334155;
  background: #0f172a; color: #94a3b8; font-size: 0.8rem; cursor: pointer;
}
.cat-panel-toggle:hover { border-color: #6366f1; color: #6366f1; }
.cat-new-row { display: flex; gap: 0.5rem; margin-bottom: 0.6rem; }
.cat-new-form { margin-bottom: 0.6rem; }
.cat-new-input {
  flex: 1; padding: 0.45rem 0.7rem; border-radius: 8px;
  border: 1px solid #334155; background: #0f172a; color: #f1f5f9; font-size: 0.875rem;
}
.cat-new-input:focus { outline: none; border-color: #6366f1; }
.cat-new-ok {
  padding: 0.45rem 0.9rem; border-radius: 8px; border: none;
  background: #6366f1; color: #fff; font-size: 0.875rem; font-weight: 600; cursor: pointer;
}
.cat-new-ok:hover:not(:disabled) { opacity: 0.85; }
.cat-new-ok:disabled { opacity: 0.4; cursor: not-allowed; }
.cat-error { color: #f87171; font-size: 0.8rem; margin: 0.25rem 0 0.5rem; }
.cat-chips { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.5rem; }
.cat-chip {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.25rem 0.65rem; border-radius: 20px; font-size: 0.8rem;
  background: #334155; color: #94a3b8;
}
.cat-chip-default { background: #1e3a5f; color: #7dd3fc; }
.cat-chip-del {
  background: none; border: none; color: #f87171; cursor: pointer;
  font-size: 0.95rem; line-height: 1; padding: 0 1px;
}
.cat-chip-del:hover { color: #ef4444; }

/* Transición slide */
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-6px); }

/* Modal confirm categoría */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}
.confirm-cat-modal {
  background: #1e293b; border-radius: 14px; padding: 1.75rem;
  width: 100%; max-width: 360px;
  display: flex; flex-direction: column; gap: 0.85rem;
  border: 1px solid #334155;
}
.confirm-cat-modal h3 { margin: 0; color: #f87171; font-size: 1.05rem; font-weight: 700; }
.confirm-cat-modal p  { margin: 0; color: #94a3b8; font-size: 0.9rem; line-height: 1.5; }
.confirm-actions { display: flex; gap: 0.6rem; justify-content: flex-end; margin-top: 0.25rem; }
.btn-danger-confirm {
  padding: 0.5rem 1.2rem; border-radius: 8px; border: none;
  background: #ef4444; color: #fff; font-size: 0.875rem; font-weight: 600; cursor: pointer;
}
.btn-danger-confirm:hover { opacity: 0.85; }

/* Modal transitions */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal-box, .modal-leave-active .modal-box { transition: transform 0.2s; }
.modal-enter-from .modal-box, .modal-leave-to .modal-box { transform: scale(0.95); }
</style>
