<template>
  <div class="view">
    <h2>Dashboard</h2>

    <div class="top-row">
      <BalanceCard :balance="balance" />

      <div class="stats-mini">
        <div class="stat ingreso">
          <span class="stat-label">Total ingresos</span>
          <span class="stat-val">+{{ totalIngresos.toFixed(2) }} €</span>
        </div>
        <div class="stat gasto">
          <span class="stat-label">Total gastos</span>
          <span class="stat-val">-{{ totalGastos.toFixed(2) }} €</span>
        </div>
      </div>
    </div>

    <!-- Resumen mensual con navegación -->
    <div class="card">
      <div class="mes-header">
        <h3>Resumen mensual</h3>
        <div class="mes-nav">
          <button class="nav-btn" @click="mesAnterior" :disabled="mesIndex <= 0">&#8249;</button>
          <span class="mes-label">{{ mesLabel }}</span>
          <button class="nav-btn" @click="mesSiguiente" :disabled="mesIndex >= mesesDisponibles.length - 1">&#8250;</button>
        </div>
      </div>

      <div class="mes-grid">
        <div class="mes-item ing">
          <div class="mis-lbl">Ingresos</div>
          <div class="mis-val">+{{ mesIngresos.toFixed(2) }} €</div>
        </div>
        <div class="mes-item gto">
          <div class="mis-lbl">Gastos</div>
          <div class="mis-val">-{{ mesGastos.toFixed(2) }} €</div>
        </div>
        <div class="mes-item" :class="mesBalance >= 0 ? 'bal-pos' : 'bal-neg'">
          <div class="mis-lbl">Balance</div>
          <div class="mis-val">{{ mesBalance >= 0 ? '+' : '' }}{{ mesBalance.toFixed(2) }} €</div>
        </div>
        <div class="mes-item mov">
          <div class="mis-lbl">Movimientos</div>
          <div class="mis-val">{{ movimientosMes.length }}</div>
        </div>
      </div>

      <Line v-if="lineReady" :key="mesMostrado" :data="lineDataMes" :options="lineOptions" />
    </div>

    <!-- Evolución anual -->
    <div class="card">
      <h3>Evolución anual</h3>
      <Line v-if="lineReady" :data="lineData" :options="lineOptions" />
    </div>

    <!-- Últimos movimientos -->
    <div class="card">
      <h3>Últimos movimientos</h3>
      <MovimientosList :movimientos="ultimos" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js'
import BalanceCard from '../components/BalanceCard.vue'
import MovimientosList from '../components/MovimientosList.vue'
import { getBalance, getMovimientos } from '../services/api.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const balance      = ref(0)
const movimientos  = ref([])
const lineReady    = ref(false)
const mesMostrado  = ref('')

const ultimos = computed(() => movimientos.value.slice(0, 5))

// ── Navegación mensual ────────────────────────────────────────────────────────

const mesesDisponibles = computed(() =>
  [...new Set(movimientos.value.map(m => m.fecha.slice(0, 7)))].sort()
)

const mesIndex = computed(() => {
  const lista = mesesDisponibles.value
  if (!mesMostrado.value) return lista.length - 1
  const idx = lista.indexOf(mesMostrado.value)
  return idx >= 0 ? idx : lista.length - 1
})

const mesLabel = computed(() => {
  const lista = mesesDisponibles.value
  const val   = mesMostrado.value || lista[lista.length - 1]
  if (!val) return '—'
  const [y, m] = val.split('-')
  return new Date(Number(y), Number(m) - 1, 1)
    .toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
})

const movimientosMes = computed(() => {
  const lista = mesesDisponibles.value
  const mes   = mesMostrado.value || lista[lista.length - 1]
  if (!mes) return []
  return movimientos.value.filter(m => m.fecha.slice(0, 7) === mes)
})

const mesIngresos = computed(() =>
  movimientosMes.value.filter(m => m.tipo === 'ingreso').reduce((s, m) => s + m.cantidad, 0)
)
const mesGastos = computed(() =>
  movimientosMes.value.filter(m => m.tipo === 'gasto').reduce((s, m) => s + m.cantidad, 0)
)
const mesBalance = computed(() => mesIngresos.value - mesGastos.value)

function mesAnterior() {
  const idx = mesIndex.value
  if (idx > 0) mesMostrado.value = mesesDisponibles.value[idx - 1]
}
function mesSiguiente() {
  const idx = mesIndex.value
  if (idx < mesesDisponibles.value.length - 1) mesMostrado.value = mesesDisponibles.value[idx + 1]
}

const totalIngresos = computed(() =>
  movimientos.value.filter(m => m.tipo === 'ingreso').reduce((s, m) => s + m.cantidad, 0)
)
const totalGastos = computed(() =>
  movimientos.value.filter(m => m.tipo === 'gasto').reduce((s, m) => s + m.cantidad, 0)
)

// ── Datos gráfica de línea mensual ─────────────────────────────────────────────

function agruparPorMes(tipo) {
  const mapa = {}
  movimientos.value
    .filter(m => m.tipo === tipo)
    .forEach(m => {
      const mes = m.fecha.slice(0, 7) // "YYYY-MM"
      mapa[mes] = (mapa[mes] ?? 0) + m.cantidad
    })
  return mapa
}

const lineData = computed(() => {
  const ingMap  = agruparPorMes('ingreso')
  const gasMap  = agruparPorMes('gasto')
  const labels  = [...new Set([...Object.keys(ingMap), ...Object.keys(gasMap)])].sort()

  return {
    labels,
    datasets: [
      {
        label: 'Ingresos',
        data: labels.map(l => ingMap[l] ?? 0),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34,197,94,0.1)',
        fill: true,
        tension: 0.3,
      },
      {
        label: 'Gastos',
        data: labels.map(l => gasMap[l] ?? 0),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.1)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

// ── Datos gráfica diaria del mes seleccionado ────────────────────────────────

function agruparPorDia(tipo, mes) {
  const mapa = {}
  movimientos.value
    .filter(m => m.tipo === tipo && m.fecha.slice(0, 7) === mes)
    .forEach(m => {
      const dia = m.fecha.slice(0, 10)
      mapa[dia] = (mapa[dia] ?? 0) + m.cantidad
    })
  return mapa
}

const lineDataMes = computed(() => {
  const lista = mesesDisponibles.value
  const mes   = mesMostrado.value || lista[lista.length - 1]
  if (!mes) return { labels: [], datasets: [] }

  const ingMap = agruparPorDia('ingreso', mes)
  const gasMap = agruparPorDia('gasto', mes)
  const labels = [...new Set([...Object.keys(ingMap), ...Object.keys(gasMap)])].sort()

  return {
    labels: labels.map(d => d.slice(8)),
    datasets: [
      {
        label: 'Ingresos',
        data: labels.map(l => ingMap[l] ?? 0),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34,197,94,0.1)',
        fill: true,
        tension: 0.3,
      },
      {
        label: 'Gastos',
        data: labels.map(l => gasMap[l] ?? 0),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.1)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

const lineOptions = {
  responsive: true,
  plugins: { legend: { labels: { color: '#94a3b8' } } },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
    y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
  },
}

onMounted(async () => {
  const [balRes, movRes] = await Promise.all([getBalance(), getMovimientos()])
  balance.value     = balRes.data.balance
  movimientos.value = movRes.data
  lineReady.value   = true
  // Iniciar en el mes más reciente
  if (mesesDisponibles.value.length > 0) {
    mesMostrado.value = mesesDisponibles.value[mesesDisponibles.value.length - 1]
  }
})
</script>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1.5rem; }
h2 { color: #f1f5f9; margin: 0; }
h3 { color: #cbd5e1; margin: 0 0 1rem; font-size: 1rem; }

.top-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stats-mini {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat {
  border-radius: 10px;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat.ingreso { background: #052e16; }
.stat.gasto   { background: #450a0a; }

.stat-label { color: #94a3b8; font-size: 0.85rem; }

.stat-val { font-size: 1.3rem; font-weight: 700; }
.stat.ingreso .stat-val { color: #4ade80; }
.stat.gasto   .stat-val { color: #f87171; }

.card {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
}

/* Navegación mensual */
.mes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.mes-header h3 { margin: 0; }

.mes-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.nav-btn {
  background: #0f172a;
  border: 1px solid #334155;
  color: #94a3b8;
  border-radius: 6px;
  width: 2rem;
  height: 2rem;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}
.nav-btn:hover:not(:disabled) { background: #1e293b; color: #f1f5f9; }
.nav-btn:disabled { opacity: 0.35; cursor: default; }

.mes-label {
  min-width: 130px;
  text-align: center;
  color: #f1f5f9;
  font-weight: 600;
  font-size: 0.95rem;
  text-transform: capitalize;
}

.mes-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.mes-item {
  border-radius: 8px;
  padding: 0.75rem 1rem;
}
.mes-item.ing       { background: #052e16; }
.mes-item.gto       { background: #450a0a; }
.mes-item.bal-pos   { background: #052e16; }
.mes-item.bal-neg   { background: #450a0a; }
.mes-item.mov       { background: #0f172a; }

.mis-lbl { color: #94a3b8; font-size: 0.75rem; margin-bottom: 0.3rem; }
.mis-val { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; }
.mes-item.ing     .mis-val { color: #4ade80; }
.mes-item.gto     .mis-val { color: #f87171; }
.mes-item.bal-pos .mis-val { color: #4ade80; }
.mes-item.bal-neg .mis-val { color: #f87171; }
.mes-item.mov     .mis-val { color: #38bdf8; }
</style>
