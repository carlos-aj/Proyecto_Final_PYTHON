<template>
  <form class="mov-form" :class="form.tipo" @submit.prevent="handleSubmit">
    <h3>Nuevo movimiento</h3>

    <!-- Tipo toggle -->
    <div class="tipo-toggle">
      <button
        type="button"
        class="tipo-btn"
        :class="{ active: form.tipo === 'ingreso' }"
        @click="form.tipo = 'ingreso'"
      >
        <Upload :size="14" /> Ingreso
      </button>
      <button
        type="button"
        class="tipo-btn"
        :class="{ active: form.tipo === 'gasto' }"
        @click="form.tipo = 'gasto'"
      >
        <Download :size="14" /> Gasto
      </button>
    </div>

    <!-- Descripción -->
    <div class="field">
      <label>Descripción</label>
      <input v-model="form.descripcion" placeholder="¿En qué?" required />
    </div>

    <!-- Categoría + Cantidad -->
    <div class="form-row">
      <div class="field">
        <label>Categoría</label>
        <CategoriaSelect ref="catSelectRef" :tipo="form.tipo" v-model="form.categoria" @categoria-creada="emit('categoria-creada', $event)" />
      </div>
      <div class="field">
        <label>Cantidad (€)</label>
        <input
          v-model.number="form.cantidad"
          type="number"
          min="0"
          step="0.01"
          placeholder="0.00"
          required
        />
      </div>
    </div>

    <!-- Fecha -->
    <div class="field half">
      <label>Fecha</label>
      <input v-model="form.fecha" type="date" required />
    </div>

    <p v-if="error" class="form-error">{{ error }}</p>

    <button type="submit" :disabled="loading" class="submit-btn">
      {{ loading ? 'Guardando…' : (form.tipo === 'ingreso' ? '+ Añadir ingreso' : '− Añadir gasto') }}
    </button>
  </form>

  <!-- Toast de confirmación -->
  <Transition name="toast">
    <div v-if="toast" class="toast-overlay" @click="toast = null">
      <div class="toast" :class="toast.tipo">
        <div class="toast-check">
          <CheckCircle :size="40" />
        </div>
        <span class="toast-title">{{ toast.tipo === 'ingreso' ? 'Ingreso registrado' : 'Gasto registrado' }}</span>
        <span class="toast-desc">{{ toast.descripcion }}</span>
        <span class="toast-amount">{{ toast.tipo === 'ingreso' ? '+' : '−' }}{{ toast.cantidad.toFixed(2) }} €</span>
        <span class="toast-hint">Toca para cerrar</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Upload, Download, CheckCircle } from 'lucide-vue-next'
import { crearIngreso, crearGasto } from '../services/api.js'
import CategoriaSelect from './CategoriaSelect.vue'

const emit = defineEmits(['creado', 'categoria-creada'])

const catSelectRef = ref(null)

const today = new Date().toISOString().split('T')[0]

const form = ref({
  tipo: 'gasto',
  descripcion: '',
  cantidad: '',
  fecha: today,
  categoria: '',
})

const loading = ref(false)
const error   = ref('')
const toast   = ref(null)
let   toastTimer = null

// Limpiar categoría cuando cambia el tipo (gastos e ingresos tienen categorías distintas)
watch(() => form.value.tipo, () => { form.value.categoria = '' })

function mostrarToast(mov) {
  clearTimeout(toastTimer)
  toast.value = mov
  toastTimer = setTimeout(() => { toast.value = null }, 1500)
}

async function handleSubmit() {
  // Si hay texto pendiente en el campo "nueva categoría", créala antes de guardar
  if (catSelectRef.value) {
    const ok = await catSelectRef.value.flushPending()
    if (!ok) return
  }
  error.value = ''
  loading.value = true
  try {
    const fn = form.value.tipo === 'ingreso' ? crearIngreso : crearGasto
    const { data } = await fn({ ...form.value })
    emit('creado', data)
    mostrarToast(data)
    form.value = { tipo: form.value.tipo, descripcion: '', cantidad: '', fecha: today, categoria: '' }
  } catch (e) {
    error.value = e.response?.data?.detail?.[0]?.msg ?? e.response?.data?.detail ?? 'Error al guardar.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mov-form {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-top: 3px solid #334155;
  transition: border-color 0.2s;
}
.mov-form.ingreso { border-top-color: #22c55e; }
.mov-form.gasto   { border-top-color: #f43f5e; }

.mov-form h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
}

/* Toggle tipo */
.tipo-toggle {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  background: #0f172a;
  border-radius: 10px;
  padding: 4px;
}
.tipo-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.tipo-btn:hover:not(.active) { color: #94a3b8; }
.mov-form.ingreso .tipo-btn.active { background: #052e16; color: #4ade80; }
.mov-form.gasto   .tipo-btn.active { background: #450a0a; color: #f87171; }

/* Campos */
.form-row { display: flex; gap: 0.75rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
.field.half { flex: none; width: 170px; }

label {
  font-size: 0.72rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 600;
}

input {
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #f1f5f9;
  font-size: 0.9rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
input::placeholder { color: #475569; }
input:focus { outline: none; }
.mov-form.ingreso input:focus {
  border-color: #22c55e;
  box-shadow: 0 0 0 3px rgba(34,197,94,0.12);
}
.mov-form.gasto input:focus {
  border-color: #f43f5e;
  box-shadow: 0 0 0 3px rgba(244,63,94,0.12);
}

/* Botón enviar */
.submit-btn {
  width: 100%;
  padding: 0.7rem;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  margin-top: 0.25rem;
  transition: opacity 0.15s, transform 0.1s;
}
.mov-form.ingreso .submit-btn { background: #22c55e; color: #052e16; }
.mov-form.gasto   .submit-btn { background: #f43f5e; color: #fff; }
.submit-btn:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.submit-btn:active:not(:disabled) { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.form-error { color: #fca5a5; font-size: 0.82rem; margin: 0; }

/* Toast */
.toast-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: pointer;
}
.toast {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  padding: 2.2rem 2.8rem;
  border-radius: 20px;
  background: #1e293b;
  border: 1px solid #334155;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  text-align: center;
  min-width: 260px;
  pointer-events: none;
}
.toast.ingreso { border-top: 4px solid #22c55e; }
.toast.gasto   { border-top: 4px solid #f43f5e; }
.toast-check { margin-bottom: 0.25rem; }
.toast.ingreso .toast-check { color: #22c55e; }
.toast.gasto   .toast-check { color: #f43f5e; }
.toast-title  { color: #f1f5f9; font-size: 1.1rem; font-weight: 700; }
.toast-desc   { color: #94a3b8; font-size: 0.9rem; }
.toast-amount { font-size: 1.6rem; font-weight: 800; margin-top: 0.25rem; }
.toast.ingreso .toast-amount { color: #4ade80; }
.toast.gasto   .toast-amount { color: #f87171; }
.toast-hint   { color: #475569; font-size: 0.72rem; margin-top: 0.5rem; }

.toast-enter-active { transition: all 0.2s ease; }
.toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from   { opacity: 0; transform: scale(0.9); }
.toast-leave-to     { opacity: 0; transform: scale(0.95); }
</style>
