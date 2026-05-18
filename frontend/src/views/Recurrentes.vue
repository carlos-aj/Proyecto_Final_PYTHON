<template>
  <div class="recurrentes-page">
    <div class="page-header">
      <div class="page-header-top">
        <div>
          <h2><Repeat :size="20" /> Gastos e Ingresos Recurrentes</h2>
          <p class="page-subtitle">
            Plantillas que generan movimientos automáticamente cada semana o mes.
          </p>
        </div>
        <button class="btn-nuevo" @click="abrirCrear">+ Nuevo recurrente</button>
      </div>
    </div>

    <div class="tabs">
      <button class="tab" :class="{ active: tabActivo === 'ingreso' }" @click="tabActivo = 'ingreso'">
        <TrendingUp :size="14" /> Ingresos
        <span v-if="ingresos.length" class="tab-count">{{ ingresos.length }}</span>
      </button>
      <button class="tab" :class="{ active: tabActivo === 'gasto' }" @click="tabActivo = 'gasto'">
        <TrendingDown :size="14" /> Gastos
        <span v-if="gastos.length" class="tab-count">{{ gastos.length }}</span>
      </button>
    </div>

    <div v-if="loading" class="empty-state">Cargando…</div>

    <div v-else-if="activos.length === 0" class="empty-state">
      <Repeat :size="32" class="empty-icon" />
      <p>No hay {{ tabActivo === 'ingreso' ? 'ingresos' : 'gastos' }} recurrentes.</p>
      <p class="empty-hint">Pulsa "Nuevo recurrente" para añadir uno.</p>
    </div>

    <div v-else class="rec-list">
      <div v-for="r in activos" :key="r.id" class="rec-card">
        <div class="rec-card-left">
          <span class="rec-freq-badge" :class="r.frecuencia">
            {{ r.frecuencia === 'semanal' ? 'Semanal' : 'Mensual' }}
          </span>
          <div class="rec-info">
            <span class="rec-desc">{{ r.descripcion }}</span>
            <span class="rec-meta">{{ r.categoria }} · Próximo: {{ r.proxima_fecha }}</span>
          </div>
        </div>
        <div class="rec-card-right">
          <span class="rec-cantidad" :class="r.tipo">
            {{ r.tipo === 'ingreso' ? '+' : '−' }}{{ r.cantidad.toFixed(2) }} €
          </span>
          <div class="rec-actions">
            <button class="btn-edit" @click="abrirEditar(r)" title="Editar"><Pencil :size="14" /></button>
            <button class="btn-del"  @click="pedirConfirmarEliminar(r)" title="Eliminar"><Trash2 :size="14" /></button>
          </div>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <div v-if="modalAbierto" class="modal-backdrop" @click.self="cerrarModal">
        <div class="modal">
          <h3>{{ modalModo === 'crear' ? 'Nuevo recurrente' : 'Editar recurrente' }}</h3>

          <div class="field">
            <label>Tipo</label>
            <div class="tipo-tabs">
              <button class="tipo-tab" :class="{ active: modalForm.tipo === 'ingreso' }" @click="modalForm.tipo = 'ingreso'">
                <TrendingUp :size="14" /> Ingreso
              </button>
              <button class="tipo-tab gasto" :class="{ active: modalForm.tipo === 'gasto' }" @click="modalForm.tipo = 'gasto'">
                <TrendingDown :size="14" /> Gasto
              </button>
            </div>
          </div>

          <div class="field">
            <label>Descripción</label>
            <input v-model="modalForm.descripcion" placeholder="Ej: Nómina, Netflix…" />
          </div>

          <div class="form-row">
            <div class="field">
              <label>Categoría</label>
              <CategoriaSelect v-model="modalForm.categoria" :tipo="modalForm.tipo" />
            </div>
            <div class="field">
              <label>Cantidad (€)</label>
              <input v-model.number="modalForm.cantidad" type="number" min="0" step="0.01" placeholder="0.00" />
            </div>
          </div>

          <div class="form-row">
            <div class="field">
              <label>Frecuencia</label>
              <select v-model="modalForm.frecuencia" class="frec-select">
                <option value="mensual">Mensual</option>
                <option value="semanal">Semanal</option>
              </select>
            </div>
            <div class="field">
              <label>Próxima fecha</label>
              <input v-model="modalForm.proxima_fecha" type="date" />
            </div>
          </div>

          <p v-if="modalError" class="modal-error">{{ modalError }}</p>

          <div class="modal-actions">
            <button class="btn-cancel" @click="cerrarModal">Cancelar</button>
            <button class="btn-save" @click="guardar" :disabled="modalLoading">
              {{ modalLoading ? 'Guardando…' : (modalModo === 'crear' ? 'Crear' : 'Guardar cambios') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="modal">
      <div v-if="confirmarRec" class="modal-backdrop" @click.self="confirmarRec = null">
        <div class="modal confirm-modal">
          <h3>¿Eliminar recurrente?</h3>
          <p>
            Se eliminará la plantilla <strong>{{ confirmarRec.descripcion }}</strong>.
            Los movimientos ya generados no se verán afectados.
          </p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="confirmarRec = null">Cancelar</button>
            <button class="btn-danger" @click="confirmarEliminar">Eliminar</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Repeat, TrendingUp, TrendingDown, Pencil, Trash2 } from 'lucide-vue-next'
import {
  getRecurrentes,
  crearRecurrente,
  editarRecurrente,
  eliminarRecurrente,
} from '../services/api.js'
import CategoriaSelect from '../components/CategoriaSelect.vue'

const plantillas  = ref([])
const loading     = ref(true)
const tabActivo   = ref('ingreso')

const ingresos = computed(() => plantillas.value.filter(r => r.tipo === 'ingreso'))
const gastos   = computed(() => plantillas.value.filter(r => r.tipo === 'gasto'))
const activos  = computed(() => tabActivo.value === 'ingreso' ? ingresos.value : gastos.value)

const modalAbierto = ref(false)
const modalModo    = ref('crear')
const modalRecId   = ref(null)
const modalForm    = ref({})
const modalLoading = ref(false)
const modalError   = ref('')

function formVacio() {
  return { tipo: tabActivo.value, descripcion: '', categoria: '', cantidad: null, frecuencia: 'mensual', proxima_fecha: '' }
}

function abrirCrear() {
  modalModo.value = 'crear'; modalRecId.value = null
  modalForm.value = formVacio(); modalError.value = ''; modalAbierto.value = true
}

function abrirEditar(r) {
  modalModo.value = 'editar'; modalRecId.value = r.id
  modalForm.value = { tipo: r.tipo, descripcion: r.descripcion, categoria: r.categoria, cantidad: r.cantidad, frecuencia: r.frecuencia, proxima_fecha: r.proxima_fecha }
  modalError.value = ''; modalAbierto.value = true
}

function cerrarModal() { modalAbierto.value = false }

async function guardar() {
  modalError.value = ''
  const f = modalForm.value
  if (!f.descripcion.trim()) { modalError.value = 'La descripción es obligatoria.'; return }
  if (!f.categoria)          { modalError.value = 'Selecciona una categoría.'; return }
  if (!f.cantidad || f.cantidad <= 0) { modalError.value = 'La cantidad debe ser mayor que 0.'; return }
  if (!f.proxima_fecha)      { modalError.value = 'Indica la próxima fecha.'; return }
  modalLoading.value = true
  try {
    if (modalModo.value === 'crear') {
      const { data } = await crearRecurrente(f)
      plantillas.value.push(data)
    } else {
      const { data } = await editarRecurrente(modalRecId.value, f)
      const idx = plantillas.value.findIndex(r => r.id === data.id)
      if (idx !== -1) plantillas.value[idx] = data
    }
    cerrarModal()
  } catch (e) {
    modalError.value = e.response?.data?.detail ?? 'Error al guardar.'
  } finally {
    modalLoading.value = false
  }
}

const confirmarRec = ref(null)
function pedirConfirmarEliminar(r) { confirmarRec.value = r }
async function confirmarEliminar() {
  const id = confirmarRec.value.id; confirmarRec.value = null
  try {
    await eliminarRecurrente(id)
    plantillas.value = plantillas.value.filter(r => r.id !== id)
  } catch (e) { console.error(e) }
}

async function cargar() {
  loading.value = true
  try { const { data } = await getRecurrentes(); plantillas.value = data }
  finally { loading.value = false }
}

onMounted(cargar)
</script>

<style scoped>
.recurrentes-page { display: flex; flex-direction: column; gap: 1.5rem; }

.page-header-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }

.page-header h2 { display: flex; align-items: center; gap: 0.5rem; font-size: 1.25rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.25rem; }
.page-subtitle { color: #64748b; font-size: 0.875rem; }

.btn-nuevo { padding: 0.55rem 1.2rem; border-radius: 8px; border: none; background: #6366f1; color: #fff; font-size: 0.875rem; font-weight: 600; cursor: pointer; white-space: nowrap; flex-shrink: 0; }
.btn-nuevo:hover { opacity: 0.85; }

.tabs { display: flex; gap: 0.5rem; }
.tab { display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1.1rem; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #64748b; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.15s; }
.tab:hover:not(.active) { border-color: #475569; color: #94a3b8; }
.tab.active { border-color: #6366f1; color: #f1f5f9; }
.tab-count { background: #334155; color: #94a3b8; font-size: 0.72rem; padding: 1px 6px; border-radius: 10px; font-weight: 600; }
.tab.active .tab-count { background: #6366f1; color: #fff; }

.empty-state { text-align: center; padding: 3rem 1rem; color: #475569; font-size: 0.9rem; display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.empty-icon { color: #334155; margin-bottom: 0.5rem; }
.empty-hint { font-size: 0.8rem; color: #334155; }

.rec-list { display: flex; flex-direction: column; gap: 0.6rem; }
.rec-card { display: flex; align-items: center; justify-content: space-between; gap: 1rem; background: #1e293b; border-radius: 10px; padding: 0.85rem 1.1rem; border: 1px solid #334155; transition: border-color 0.15s; }
.rec-card:hover { border-color: #475569; }
.rec-card-left  { display: flex; align-items: center; gap: 0.75rem; min-width: 0; }
.rec-card-right { display: flex; align-items: center; gap: 1rem; flex-shrink: 0; }

.rec-freq-badge { padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700; flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.4px; }
.rec-freq-badge.mensual { background: #1e3a5f; color: #7dd3fc; }
.rec-freq-badge.semanal { background: #2d1b69; color: #a78bfa; }

.rec-info { display: flex; flex-direction: column; gap: 0.1rem; min-width: 0; }
.rec-desc { color: #f1f5f9; font-size: 0.9rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rec-meta { color: #64748b; font-size: 0.78rem; }

.rec-cantidad { font-size: 1rem; font-weight: 700; }
.rec-cantidad.ingreso { color: #4ade80; }
.rec-cantidad.gasto   { color: #f87171; }

.rec-actions { display: flex; gap: 0.35rem; }
.btn-edit, .btn-del { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; cursor: pointer; transition: all 0.15s; }
.btn-edit { color: #94a3b8; }
.btn-edit:hover { border-color: #6366f1; color: #6366f1; }
.btn-del  { color: #94a3b8; }
.btn-del:hover  { border-color: #ef4444; color: #ef4444; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 1rem; }
.modal { background: #1e293b; border-radius: 14px; padding: 1.75rem; width: 100%; max-width: 460px; display: flex; flex-direction: column; gap: 1rem; border: 1px solid #334155; }
.modal h3 { margin: 0; color: #f1f5f9; font-size: 1.05rem; font-weight: 700; }

.tipo-tabs { display: flex; gap: 0.5rem; }
.tipo-tab { display: flex; align-items: center; gap: 0.4rem; padding: 0.45rem 1rem; border-radius: 7px; border: 1px solid #334155; background: transparent; color: #64748b; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.15s; }
.tipo-tab.active       { border-color: #4ade80; color: #4ade80; background: rgba(74,222,128,0.07); }
.tipo-tab.gasto.active { border-color: #f87171; color: #f87171; background: rgba(248,113,113,0.07); }
.tipo-tab:not(.active):hover { border-color: #475569; color: #94a3b8; }

.field { display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
.field label { font-size: 0.8rem; color: #94a3b8; font-weight: 500; }
.field input, .frec-select { padding: 0.55rem 0.75rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #f1f5f9; font-size: 0.9rem; }
.field input:focus, .frec-select:focus { outline: none; border-color: #6366f1; }
.frec-select { width: 100%; cursor: pointer; }
.form-row { display: flex; gap: 0.75rem; }

.modal-error { color: #f87171; font-size: 0.82rem; margin: 0; }

.modal-actions { display: flex; gap: 0.6rem; justify-content: flex-end; margin-top: 0.25rem; }
.btn-cancel { padding: 0.5rem 1.1rem; border-radius: 8px; border: 1px solid #334155; background: transparent; color: #94a3b8; font-size: 0.875rem; cursor: pointer; }
.btn-cancel:hover { border-color: #475569; color: #e2e8f0; }
.btn-save { padding: 0.5rem 1.2rem; border-radius: 8px; border: none; background: #6366f1; color: #fff; font-size: 0.875rem; font-weight: 600; cursor: pointer; }
.btn-save:hover:not(:disabled) { opacity: 0.85; }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

.confirm-modal { max-width: 380px; gap: 0.85rem; }
.confirm-modal h3 { color: #f87171; }
.confirm-modal p { margin: 0; color: #94a3b8; font-size: 0.9rem; line-height: 1.5; }
.confirm-actions { display: flex; gap: 0.6rem; justify-content: flex-end; margin-top: 0.25rem; }
.btn-danger { padding: 0.5rem 1.2rem; border-radius: 8px; border: none; background: #ef4444; color: #fff; font-size: 0.875rem; font-weight: 600; cursor: pointer; }
.btn-danger:hover { opacity: 0.85; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95); }
</style>
