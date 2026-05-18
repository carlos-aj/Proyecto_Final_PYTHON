<template>
  <div class="view">
    <div class="page-header">
      <h2>Objetivos de ahorro</h2>
      <button class="new-btn" @click="showForm = !showForm">
        {{ showForm ? 'Cancelar' : '+ Nuevo objetivo' }}
      </button>
    </div>

    <!-- Formulario crear objetivo -->
    <div v-if="showForm" class="card form-card">
      <h3>Nuevo objetivo</h3>
      <form class="obj-form" @submit.prevent="crear">
        <div class="field">
          <label>Nombre</label>
          <input v-model="form.nombre" placeholder="p.ej. Vacaciones" required />
        </div>
        <div class="form-row">
          <div class="field">
            <label>Meta (€)</label>
            <input v-model.number="form.cantidad_meta" type="number" min="0" step="0.01" placeholder="0.00" required />
          </div>
          <div class="field">
            <label>Fecha límite</label>
            <input v-model="form.fecha_limite" type="date" required />
          </div>
        </div>
        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? 'Guardando…' : 'Crear objetivo' }}
        </button>
      </form>
    </div>

    <!-- Grid de objetivos -->
    <div v-if="objetivos.length > 0" class="obj-grid">
      <div v-for="obj in objetivos" :key="obj.id" class="card obj-card">
        <div class="obj-top">
          <span class="obj-nombre">{{ obj.nombre }}</span>
          <span v-if="obj.completado" class="obj-completed-badge">✓ Completado</span>
        </div>

        <!-- Barra de progreso -->
        <div class="obj-bar-wrap">
          <div class="obj-bar-track">
            <div
              class="obj-bar-fill"
              :class="{ 'fill-done': obj.completado }"
              :style="{ width: obj.progreso + '%' }"
            ></div>
          </div>
          <span class="obj-pct">{{ obj.progreso }}%</span>
        </div>

        <!-- Montos -->
        <div class="obj-amounts">
          <span class="obj-actual">{{ obj.cantidad_actual.toFixed(2) }} €</span>
          <span class="obj-sep">/</span>
          <span class="obj-meta">{{ obj.cantidad_meta.toFixed(2) }} €</span>
        </div>

        <!-- Días restantes -->
        <div class="obj-footer">
          <span class="obj-dias" :class="{ 'dias-warn': obj.dias_restantes < 30 && !obj.completado }">
            <template v-if="obj.completado">Meta alcanzada</template>
            <template v-else-if="obj.dias_restantes <= 0">Plazo vencido</template>
            <template v-else>{{ obj.dias_restantes }} días restantes</template>
          </span>
          <span class="obj-fecha">{{ obj.fecha_limite }}</span>
        </div>

        <!-- Acciones -->
        <div class="obj-actions">
          <button class="btn-aport" @click="abrirAport(obj)">+ Aportación</button>
          <button class="btn-del-obj" @click="pedirEliminar(obj)">Eliminar</button>
        </div>
      </div>
    </div>
    <div v-else-if="!loading" class="card empty-card">
      <p class="empty">Sin objetivos de ahorro. ¡Crea el primero!</p>
    </div>

    <!-- Modal aportación -->
    <div v-if="aportMov" class="modal-overlay" @click.self="aportMov = null">
      <div class="modal-card">
        <h3>Registrar aportación</h3>
        <p class="modal-sub">{{ aportMov.nombre }}</p>
        <div class="field">
          <label>Cantidad (€)</label>
          <input v-model.number="aportCantidad" type="number" min="0.01" step="0.01" placeholder="0.00" />
        </div>
        <div class="modal-actions">
          <button class="modal-cancel" @click="aportMov = null">Cancelar</button>
          <button class="modal-save" @click="confirmarAport" :disabled="aportLoading">
            {{ aportLoading ? '…' : 'Añadir' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal eliminar -->
    <div v-if="delMov" class="modal-overlay" @click.self="delMov = null">
      <div class="modal-card del-modal">
        <div class="del-icon-wrap"><span>🗑</span></div>
        <h3>¿Eliminar objetivo?</h3>
        <p class="modal-sub">{{ delMov.nombre }}</p>
        <div class="modal-actions">
          <button class="modal-cancel" @click="delMov = null">Cancelar</button>
          <button class="modal-del-confirm" @click="confirmarEliminar">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getObjetivos, crearObjetivo, aportarObjetivo, eliminarObjetivo } from '../services/api.js'

const objetivos     = ref([])
const showForm      = ref(false)
const loading       = ref(false)
const aportMov      = ref(null)
const aportCantidad = ref(0)
const aportLoading  = ref(false)
const delMov        = ref(null)

const form = ref({ nombre: '', cantidad_meta: '', fecha_limite: '' })

async function cargar() {
  const { data } = await getObjetivos()
  objetivos.value = data
}

async function crear() {
  loading.value = true
  try {
    await crearObjetivo(form.value)
    form.value = { nombre: '', cantidad_meta: '', fecha_limite: '' }
    showForm.value = false
    await cargar()
  } finally {
    loading.value = false
  }
}

function abrirAport(obj) {
  aportMov.value = obj
  aportCantidad.value = 0
}

async function confirmarAport() {
  if (!aportCantidad.value || aportCantidad.value <= 0) return
  aportLoading.value = true
  try {
    const { data } = await aportarObjetivo(aportMov.value.id, aportCantidad.value)
    const idx = objetivos.value.findIndex(o => o.id === data.id)
    if (idx !== -1) objetivos.value[idx] = data
    aportMov.value = null
  } finally {
    aportLoading.value = false
  }
}

function pedirEliminar(obj) {
  delMov.value = obj
}

async function confirmarEliminar() {
  await eliminarObjetivo(delMov.value.id)
  objetivos.value = objetivos.value.filter(o => o.id !== delMov.value.id)
  delMov.value = null
}

onMounted(cargar)
</script>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1.5rem; }
h2 { color: #f1f5f9; margin: 0; }
h3 { color: #cbd5e1; margin: 0 0 1rem; font-size: 1rem; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.new-btn {
  padding: 0.5rem 1.1rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s;
}
.new-btn:hover { background: #334155; }

.card { background: #1e293b; border-radius: 12px; padding: 1.5rem; }

/* Form card */
.form-card { border-top: 3px solid #6366f1; }
.obj-form { display: flex; flex-direction: column; gap: 1rem; }
.form-row { display: flex; gap: 0.75rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }
input {
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #f1f5f9;
  font-size: 0.9rem;
}
input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.submit-btn {
  padding: 0.65rem;
  border: none;
  border-radius: 8px;
  background: #6366f1;
  color: #fff;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
}
.submit-btn:hover:not(:disabled) { opacity: 0.85; }
.submit-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Grid objetivos */
.obj-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.obj-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border-top: 3px solid #6366f1;
}

.obj-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.obj-nombre { color: #f1f5f9; font-weight: 600; font-size: 0.95rem; }
.obj-completed-badge {
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(34,197,94,0.12);
  color: #4ade80;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
}

.obj-bar-wrap { display: flex; align-items: center; gap: 0.6rem; }
.obj-bar-track {
  flex: 1;
  background: #0f172a;
  border-radius: 99px;
  height: 8px;
  overflow: hidden;
}
.obj-bar-fill {
  height: 100%;
  border-radius: 99px;
  background: #6366f1;
  min-width: 4px;
  transition: width 0.3s;
}
.fill-done { background: #22c55e; }
.obj-pct { color: #94a3b8; font-size: 0.78rem; white-space: nowrap; }

.obj-amounts { display: flex; align-items: center; gap: 0.3rem; font-size: 0.85rem; }
.obj-actual { color: #e2e8f0; font-weight: 600; }
.obj-sep    { color: #334155; }
.obj-meta   { color: #64748b; }

.obj-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
}
.obj-dias { color: #64748b; }
.dias-warn { color: #fb923c; }
.obj-fecha { color: #475569; }

.obj-actions { display: flex; gap: 0.6rem; margin-top: 0.25rem; }
.btn-aport {
  flex: 1;
  padding: 0.5rem;
  border-radius: 7px;
  border: 1px solid rgba(99,102,241,0.3);
  background: rgba(99,102,241,0.1);
  color: #818cf8;
  font-size: 0.83rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-aport:hover { opacity: 0.8; }
.btn-del-obj {
  padding: 0.5rem 0.8rem;
  border-radius: 7px;
  border: 1px solid rgba(239,68,68,0.2);
  background: transparent;
  color: #64748b;
  font-size: 0.83rem;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
}
.btn-del-obj:hover { color: #ef4444; background: rgba(239,68,68,0.07); }

.empty-card { text-align: center; }
.empty { color: #475569; padding: 1.5rem; margin: 0; }

/* Modals */
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
  width: 380px;
  max-width: 95vw;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-top: 3px solid #6366f1;
}
.modal-card h3 { color: #f1f5f9; margin: 0; font-size: 1rem; }
.modal-sub { color: #64748b; font-size: 0.875rem; margin: 0; }
.modal-card .field { display: flex; flex-direction: column; gap: 0.35rem; }
.modal-card label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }
.modal-card input { padding: 0.6rem 0.75rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #f1f5f9; font-size: 0.9rem; }
.modal-card input:focus { outline: none; border-color: #6366f1; }
.modal-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
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

.del-modal { border-top-color: #ef4444; }
.del-icon-wrap { font-size: 1.5rem; text-align: center; }
.del-modal h3 { text-align: center; }
.del-modal .modal-sub { text-align: center; }
.modal-del-confirm {
  padding: 0.55rem 1.1rem; border-radius: 8px; border: none;
  background: #ef4444; color: #fff; font-size: 0.88rem; font-weight: 600; cursor: pointer;
}
.modal-del-confirm:hover { opacity: 0.85; }
</style>
