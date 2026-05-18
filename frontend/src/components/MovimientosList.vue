<template>
  <div class="mov-list">
    <!-- Filtros -->
    <div v-if="showFilters" class="filtros">
      <!-- Tipo pills -->
      <div class="tipo-pills">
        <button :class="['pill', filtroTipo === '' && 'active-all']" @click="filtroTipo = ''">Todos</button>
        <button :class="['pill', 'pill-ingreso', filtroTipo === 'ingreso' && 'active']" @click="filtroTipo = 'ingreso'">Ingresos</button>
        <button :class="['pill', 'pill-gasto',   filtroTipo === 'gasto'   && 'active']" @click="filtroTipo = 'gasto'">Gastos</button>
      </div>

      <div class="filtro-sep"></div>

      <!-- Categoría -->
      <select v-model="filtroCategoria" class="filtro-select">
        <option value="">Todas las categorías</option>
        <option v-for="cat in categoriasUnicas" :key="cat" :value="cat">{{ cat }}</option>
      </select>

      <!-- Fechas -->
      <input v-model="filtroDesde" type="date" @change="emitFiltros" class="filtro-date" />
      <span class="date-arrow">→</span>
      <input v-model="filtroHasta" type="date" @change="emitFiltros" class="filtro-date" />

      <button class="btn-clear" @click="limpiarFiltros">
        <X :size="13" /> Limpiar
      </button>
    </div>

    <div v-if="showFilters" class="resultado-info">
      {{ filtrados.length }} movimiento{{ filtrados.length !== 1 ? 's' : '' }}
    </div>

    <!-- Lista -->
    <div class="lista">
      <p v-if="filtrados.length === 0" class="empty">Sin movimientos.</p>
      <div v-for="m in filtrados" :key="m.id" class="mov-row">
        <div class="mov-indicator" :class="m.tipo"></div>
        <div class="mov-body">
          <span class="mov-desc">{{ m.descripcion }}</span>
          <span class="mov-cat">{{ m.categoria }}</span>
        </div>
        <div class="mov-meta">
          <span class="mov-fecha">{{ m.fecha }}</span>
          <span class="mov-amount" :class="m.tipo">
            {{ m.tipo === 'ingreso' ? '+' : '-' }}{{ m.cantidad.toFixed(2) }} €
          </span>
        </div>
        <button v-if="showDelete" class="btn-edit" @click="emit('editar', m)" title="Editar">
          <Pencil :size="13" />
        </button>
        <button v-if="showDelete" class="btn-del" @click="pedirConfirm(m)" title="Eliminar">
          <Trash2 :size="14" />
        </button>
      </div>
    </div>

    <!-- Modal de confirmación -->
    <div v-if="pendingMov" class="modal-overlay" @click.self="pendingMov = null">
      <div class="modal">
        <div class="modal-icon-wrap">
          <Trash2 :size="20" />
        </div>
        <h3 class="modal-title">¿Eliminar movimiento?</h3>
        <p class="modal-desc">{{ pendingMov.descripcion }}</p>
        <p class="modal-sub">
          <span :class="['modal-badge', pendingMov.tipo]">{{ pendingMov.tipo }}</span>
          {{ pendingMov.tipo === 'ingreso' ? '+' : '-' }}{{ pendingMov.cantidad.toFixed(2) }} €
          &middot; {{ pendingMov.categoria }}
        </p>
        <div class="modal-actions">
          <button class="modal-cancel" @click="pendingMov = null">Cancelar</button>
          <button class="modal-confirm" @click="confirmarEliminar">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Trash2, X, Pencil } from 'lucide-vue-next'

const pendingMov = ref(null)

function pedirConfirm(m) {
  pendingMov.value = m
}

function confirmarEliminar() {
  emit('eliminar', pendingMov.value.id)
  pendingMov.value = null
}

const props = defineProps({
  movimientos: { type: Array, default: () => [] },
  showFilters: { type: Boolean, default: false },
  showDelete:  { type: Boolean, default: false },
})

const emit = defineEmits(['filtrar', 'eliminar', 'editar'])

const filtroTipo      = ref('')
const filtroCategoria = ref('')
const filtroDesde     = ref('')
const filtroHasta     = ref('')

const categoriasUnicas = computed(() => {
  const cats = [...new Set(props.movimientos.map(m => m.categoria))].filter(Boolean)
  return cats.sort((a, b) => a.localeCompare(b, 'es'))
})

// Tipo y categoría se filtran en el cliente sobre los datos ya cargados
const filtrados = computed(() => {
  return props.movimientos.filter(m => {
    const coincideTipo = !filtroTipo.value || m.tipo === filtroTipo.value
    const coincideCat  = !filtroCategoria.value || m.categoria === filtroCategoria.value
    return coincideTipo && coincideCat
  })
})

function emitFiltros() {
  emit('filtrar', {
    // Solo las fechas van a la API; tipo y categoría se resuelven localmente
    fechaDesde: filtroDesde.value || undefined,
    fechaHasta: filtroHasta.value || undefined,
  })
}

function limpiarFiltros() {
  filtroTipo.value      = ''
  filtroCategoria.value = ''
  filtroDesde.value     = ''
  filtroHasta.value     = ''
  emitFiltros()
}
</script>

<style scoped>
.mov-list { display: flex; flex-direction: column; gap: 1rem; }

/* ── Filtros ─────────────────────────────────── */
.filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  background: #0f172a;
  padding: 0.65rem 0.75rem;
  border-radius: 10px;
  border: 1px solid #1e293b;
}

.tipo-pills {
  display: flex;
  background: #1e293b;
  border-radius: 7px;
  padding: 3px;
  gap: 2px;
}
.pill {
  padding: 0.28rem 0.7rem;
  border-radius: 5px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.pill:hover { color: #94a3b8; }
.pill.active-all   { background: #334155; color: #e2e8f0; }
.pill-ingreso.active { background: #14532d; color: #86efac; }
.pill-gasto.active   { background: #7f1d1d; color: #fca5a5; }

.filtro-sep { width: 1px; height: 22px; background: #334155; }

.filtro-select {
  padding: 0.32rem 0.65rem;
  border-radius: 7px;
  border: 1px solid #334155;
  background: #1e293b;
  color: #e2e8f0;
  font-size: 0.8rem;
  min-width: 140px;
  cursor: pointer;
}
.filtro-select:focus { outline: none; border-color: #475569; }

.filtro-date {
  padding: 0.32rem 0.6rem;
  border-radius: 7px;
  border: 1px solid #334155;
  background: #1e293b;
  color: #e2e8f0;
  font-size: 0.8rem;
}
.filtro-date:focus { outline: none; border-color: #475569; }

.date-arrow { color: #475569; font-size: 0.78rem; }

.btn-clear {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0.32rem 0.65rem;
  border: 1px solid #334155;
  border-radius: 7px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  font-size: 0.78rem;
  margin-left: auto;
  transition: color 0.15s, border-color 0.15s;
}
.btn-clear:hover { color: #94a3b8; border-color: #475569; }

.resultado-info { color: #475569; font-size: 0.76rem; }

/* ── Lista ─────────────────────────────────── */
.lista { display: flex; flex-direction: column; }

.mov-row {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.65rem 0.4rem;
  border-bottom: 1px solid #1e293b;
  border-radius: 6px;
  transition: background 0.12s;
}
.mov-row:last-child { border-bottom: none; }
.mov-row:hover { background: rgba(30,41,59,0.55); }

.mov-indicator {
  width: 3px;
  height: 34px;
  border-radius: 3px;
  flex-shrink: 0;
}
.mov-indicator.ingreso { background: #22c55e; }
.mov-indicator.gasto   { background: #f43f5e; }

.mov-body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  min-width: 0;
}
.mov-desc {
  color: #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mov-cat {
  display: inline-block;
  background: #1e293b;
  color: #64748b;
  font-size: 0.71rem;
  padding: 1px 8px;
  border-radius: 999px;
  width: fit-content;
}

.mov-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  flex-shrink: 0;
}
.mov-fecha  { color: #475569; font-size: 0.74rem; }
.mov-amount { font-size: 0.875rem; font-weight: 700; }
.mov-amount.ingreso { color: #4ade80; }
.mov-amount.gasto   { color: #f87171; }

.btn-edit {
  border: none;
  background: transparent;
  color: #334155;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 5px;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;
}
.btn-edit:hover { color: #818cf8; background: rgba(99,102,241,0.08); }

.btn-del {
  border: none;
  background: transparent;
  color: #334155;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 5px;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;
}
.btn-del:hover { color: #ef4444; background: rgba(239,68,68,0.08); }

/* ── Modal ─────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 14px;
  padding: 1.75rem 1.75rem 1.5rem;
  width: 340px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  animation: slideUp 0.18s ease;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

@keyframes slideUp { from { transform: translateY(12px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  margin-bottom: 0.25rem;
}

.modal-title {
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
  text-align: center;
}

.modal-desc {
  color: #cbd5e1;
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
  text-align: center;
}

.modal-sub {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #64748b;
  font-size: 0.8rem;
  margin: 0;
}

.modal-badge {
  display: inline-block;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: capitalize;
}
.modal-badge.ingreso { background: #14532d; color: #86efac; }
.modal-badge.gasto   { background: #7f1d1d; color: #fca5a5; }

.modal-actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.5rem;
  width: 100%;
}

.modal-cancel {
  flex: 1;
  padding: 0.6rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.modal-cancel:hover { border-color: #475569; color: #e2e8f0; }

.modal-confirm {
  flex: 1;
  padding: 0.6rem;
  border-radius: 8px;
  border: none;
  background: #ef4444;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.modal-confirm:hover { background: #dc2626; }

.empty { color: #475569; text-align: center; padding: 2.5rem; margin: 0; }
</style>
