<template>
  <div class="view">
    <h2>Estadísticas</h2>

    <div class="top-grid">
      <!-- Barras: gastos por categoría -->
      <div class="card">
        <div class="cat-header">
          <h3>Gastos por categoría</h3>
          <span class="cat-total">{{ totalGastos.toFixed(2) }} €</span>
        </div>

        <div v-if="categoriasOrdenadas.length > 0" class="cat-list">
          <div class="cat-row" v-for="([cat, val], i) in categoriasOrdenadas" :key="cat">
            <div class="cat-meta">
              <span
                class="cat-dot"
                :style="{ background: presupuestoDeCat(cat) ? colorPres(presupuestoDeCat(cat)) : COLORS[i % COLORS.length] }"
              ></span>
              <span class="cat-name">{{ cat }}</span>
              <span class="cat-amount">
                {{ val.toFixed(2) }} €
                <span v-if="presupuestoDeCat(cat)" class="cat-limit">
                  &nbsp;/&nbsp;{{ presupuestoDeCat(cat).limite.toFixed(2) }} €
                </span>
              </span>
            </div>
            <div class="cat-bar-track">
              <div
                class="cat-bar-fill"
                :style="{
                  width: presupuestoDeCat(cat)
                    ? Math.min(presupuestoDeCat(cat).porcentaje, 100) + '%'
                    : porcentaje(val) + '%',
                  background: presupuestoDeCat(cat)
                    ? colorPres(presupuestoDeCat(cat))
                    : COLORS[i % COLORS.length]
                }"
              ></div>
            </div>
            <span
              class="cat-pct"
              :style="presupuestoDeCat(cat) ? { color: colorPres(presupuestoDeCat(cat)), fontWeight: 700 } : {}"
            >
              {{ presupuestoDeCat(cat)
                ? presupuestoDeCat(cat).porcentaje + '%'
                : porcentaje(val) + '%' }}
            </span>
          </div>
        </div>
        <p v-else class="empty">Sin datos.</p>
      </div>

      <!-- Bar: balance mensual -->
      <div class="card">
        <h3>Balance mensual</h3>
        <div class="chart-wrap">
          <Bar v-if="barReady" :data="barData" :options="barOptions" />
          <p v-else class="empty">Sin datos.</p>
        </div>
      </div>
    </div>

    <!-- Presupuestos -->
    <div class="card pres-card">
      <div class="pres-header">
        <h3>Presupuestos</h3>
        <button class="pres-toggle-btn" @click="showPresForm = !showPresForm">
          {{ showPresForm ? 'Cancelar' : '+ Nuevo' }}
        </button>
      </div>

      <!-- Formulario crear presupuesto -->
      <form v-if="showPresForm" class="pres-form" @submit.prevent="crearPres">
        <div class="pres-form-row">
          <CategoriaSelect v-model="presForm.categoria" class="pres-cat-select" :tipo="'gasto'" />
          <input v-model.number="presForm.limite" type="number" min="0" step="0.01" placeholder="Límite (€)" required />
          <input v-model="presForm.mes" type="month" required />
          <button type="submit" :disabled="presLoading" class="pres-save-btn">
            {{ presLoading ? '…' : 'Guardar' }}
          </button>
        </div>
      </form>

      <!-- Lista de presupuestos -->
      <div v-if="presupuestos.length > 0" class="pres-list">
        <div v-for="p in presupuestos" :key="p.id" class="pres-row">
          <div class="pres-meta">
            <span class="pres-cat">{{ p.categoria }}</span>
            <span class="pres-mes">{{ p.mes }}</span>
            <span :class="['pres-badge', p.superado ? 'pres-over' : p.porcentaje >= 80 ? 'pres-warn' : 'pres-ok']">
              {{ p.porcentaje }}%
            </span>
          </div>
          <div class="pres-track">
            <div
              class="pres-fill"
              :class="{ 'pres-fill-over': p.superado, 'pres-fill-warn': !p.superado && p.porcentaje >= 80 }"
              :style="{ width: Math.min(p.porcentaje, 100) + '%' }"
            ></div>
          </div>
          <div class="pres-amounts">
            <span class="pres-spent">{{ p.gastado.toFixed(2) }} €</span>
            <span class="pres-sep">/</span>
            <span class="pres-limit">{{ p.limite.toFixed(2) }} €</span>
            <button class="pres-del" @click="elimPres(p.id)" title="Eliminar">&times;</button>
          </div>
        </div>
      </div>
      <p v-else class="empty">Sin presupuestos para este mes.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Tooltip, Legend,
  CategoryScale, LinearScale, BarElement, Title,
} from 'chart.js'
import { getCategoriasStats, getCategorias, getMovimientos, getPresupuestos, crearPresupuesto, eliminarPresupuesto } from '../services/api.js'
import CategoriaSelect from '../components/CategoriaSelect.vue'

ChartJS.register(Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title)

const categorias   = ref({})
const movimientos  = ref([])
const barReady     = ref(false)
const presupuestos = ref([])
const showPresForm = ref(false)
const presLoading  = ref(false)
const presForm     = ref({ categoria: '', limite: '', mes: new Date().toISOString().slice(0, 7) })

async function cargarPresupuestos() {
  const { data } = await getPresupuestos(presForm.value.mes)
  presupuestos.value = data
}

async function crearPres() {
  presLoading.value = true
  try {
    await crearPresupuesto(presForm.value)
    presForm.value = { categoria: '', limite: '', mes: presForm.value.mes }
    showPresForm.value = false
    await cargarPresupuestos()
  } finally {
    presLoading.value = false
  }
}

async function elimPres(id) {
  await eliminarPresupuesto(id)
  presupuestos.value = presupuestos.value.filter(p => p.id !== id)
}

function presupuestoDeCat(cat) {
  return presupuestos.value.find(
    p => p.categoria.toLowerCase() === cat.toLowerCase()
  ) || null
}

function colorPres(p) {
  if (p.superado) return '#f87171'
  if (p.porcentaje >= 80) return '#fb923c'
  return '#4ade80'
}

// Paleta de colores
const COLORS = [
  '#38bdf8','#818cf8','#fb923c','#4ade80','#f472b6',
  '#facc15','#a78bfa','#34d399','#f87171','#60a5fa',
]

// ── Doughnut ───────────────────────────────────────────────────────────────────

// ── Barras de categoría ──────────────────────────────────────────────────────

const totalGastos = computed(() => Object.values(categorias.value).reduce((s, v) => s + v, 0))

const categoriasOrdenadas = computed(() =>
  Object.entries(categorias.value).sort(([, a], [, b]) => b - a)
)

function porcentaje(val) {
  if (!totalGastos.value) return '0.0'
  return ((val / totalGastos.value) * 100).toFixed(1)
}

// ── Bar mensual ────────────────────────────────────────────────────────────────

function agruparPorMes(tipo) {
  const mapa = {}
  movimientos.value
    .filter(m => m.tipo === tipo)
    .forEach(m => {
      const mes = m.fecha.slice(0, 7)
      mapa[mes] = (mapa[mes] ?? 0) + m.cantidad
    })
  return mapa
}

const barData = computed(() => {
  const ingMap = agruparPorMes('ingreso')
  const gasMap = agruparPorMes('gasto')
  const labels = [...new Set([...Object.keys(ingMap), ...Object.keys(gasMap)])].sort()
  return {
    labels,
    datasets: [
      {
        label: 'Ingresos',
        data: labels.map(l => ingMap[l] ?? 0),
        backgroundColor: 'rgba(34,197,94,0.2)',
        borderColor: '#22c55e',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: 'rgba(34,197,94,0.45)',
      },
      {
        label: 'Gastos',
        data: labels.map(l => gasMap[l] ?? 0),
        backgroundColor: 'rgba(244,63,94,0.2)',
        borderColor: '#f43f5e',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: 'rgba(244,63,94,0.45)',
      },
    ],
  }
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#94a3b8',
        padding: 20,
        usePointStyle: true,
        pointStyle: 'rectRounded',
        font: { size: 13 },
      },
    },
    tooltip: {
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      borderWidth: 1,
      titleColor: '#f1f5f9',
      bodyColor: '#94a3b8',
      padding: 12,
      callbacks: {
        label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} €`,
      },
    },
  },
  scales: {
    x: {
      ticks: { color: '#64748b', font: { size: 12 } },
      grid:   { display: false },
      border: { display: false },
    },
    y: {
      ticks: {
        color: '#64748b',
        font: { size: 12 },
        callback: v => v.toLocaleString('es-ES') + ' €',
      },
      grid:   { color: '#1e293b' },
      border: { display: false },
    },
  },
}

// ── Carga inicial ──────────────────────────────────────────────────────────────

onMounted(async () => {
  const [catRes, movRes] = await Promise.all([getCategoriasStats(), getMovimientos()])
  categorias.value  = catRes.data.categorias
  movimientos.value = movRes.data
  barReady.value = movimientos.value.length > 0
  await cargarPresupuestos()
})
</script>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1.5rem; }
h2 { color: #f1f5f9; margin: 0; }
h3 { color: #cbd5e1; margin: 0 0 1rem; font-size: 1rem; }

.top-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.card { background: #1e293b; border-radius: 12px; padding: 1.5rem; }

.chart-wrap { height: 300px; position: relative; }

.empty { color: #475569; text-align: center; padding: 2rem; margin: 0; }

/* Cabecera de la card de categorías */
.cat-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.25rem;
}
.cat-header h3 { margin: 0; }
.cat-total { color: #f87171; font-weight: 700; font-size: 1.1rem; }

/* Lista de barras */
.cat-list { display: flex; flex-direction: column; gap: 0.85rem; }

.cat-row {
  display: grid;
  grid-template-columns: 1fr 2fr 42px;
  align-items: center;
  gap: 0.75rem;
}

.cat-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}
.cat-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}
.cat-name {
  color: #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cat-amount {
  color: #64748b;
  font-size: 0.75rem;
  margin-left: auto;
  white-space: nowrap;
}
.cat-limit {
  color: #475569;
  font-size: 0.72rem;
}

.cat-bar-track {
  background: #0f172a;
  border-radius: 99px;
  height: 8px;
  overflow: hidden;
}
.cat-bar-fill {
  height: 100%;
  border-radius: 99px;
  min-width: 4px;
}

.cat-pct {
  color: #64748b;
  font-size: 0.75rem;
  text-align: right;
  white-space: nowrap;
}

/* ── Presupuestos ───────────────────────────────────────────────────────── */
.pres-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.pres-header h3 { margin: 0; }
.pres-toggle-btn {
  padding: 0.35rem 0.9rem;
  border-radius: 7px;
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  font-size: 0.82rem;
  cursor: pointer;
  transition: background 0.15s;
}
.pres-toggle-btn:hover { background: #334155; }

.pres-form { margin-bottom: 1rem; }
.pres-form-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  align-items: flex-start;
}
.pres-cat-select {
  flex: 1;
  min-width: 160px;
}
.pres-form-row input {
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #f1f5f9;
  font-size: 0.875rem;
  flex: 1;
  min-width: 120px;
}
.pres-form-row input:focus { outline: none; border-color: #6366f1; }
.pres-save-btn {
  padding: 0.55rem 1.1rem;
  border-radius: 8px;
  border: none;
  background: #6366f1;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}
.pres-save-btn:hover:not(:disabled) { opacity: 0.85; }
.pres-save-btn:disabled { opacity: 0.4; }

.pres-list { display: flex; flex-direction: column; gap: 1rem; }

.pres-row { display: flex; flex-direction: column; gap: 0.4rem; }

.pres-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.pres-cat { color: #e2e8f0; font-size: 0.875rem; font-weight: 500; }
.pres-mes { color: #475569; font-size: 0.75rem; }
.pres-badge {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
}
.pres-ok   { background: rgba(34,197,94,0.12);  color: #4ade80; }
.pres-warn { background: rgba(251,146,60,0.12);  color: #fb923c; }
.pres-over { background: rgba(239,68,68,0.12);   color: #f87171; }

.pres-track {
  background: #0f172a;
  border-radius: 99px;
  height: 7px;
  overflow: hidden;
}
.pres-fill {
  height: 100%;
  border-radius: 99px;
  background: #4ade80;
  min-width: 4px;
  transition: width 0.3s;
}
.pres-fill-warn { background: #fb923c; }
.pres-fill-over { background: #f87171; }

.pres-amounts {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.78rem;
}
.pres-spent { color: #94a3b8; }
.pres-sep   { color: #334155; }
.pres-limit { color: #475569; }
.pres-del {
  margin-left: auto;
  border: none;
  background: transparent;
  color: #334155;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0;
  transition: color 0.15s;
}
.pres-del:hover { color: #ef4444; }
</style>
