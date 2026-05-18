<template>
  <div class="cat-select-wrap">
    <select
      class="cat-select"
      :value="modelValue"
      @change="onChange"
      required
    >
      <option value="" disabled>Seleccionar categoría…</option>
      <option v-if="pendingNombre" :value="pendingNombre" class="cat-option-pending">
        {{ pendingNombre }} ★ (nueva)
      </option>
      <option v-for="c in categorias" :key="c.id" :value="c.nombre">
        {{ c.nombre }}
      </option>
    </select>

    <button type="button" class="cat-add-btn" @click="toggleNew" :title="showNew ? 'Cancelar' : 'Nueva categoría'">
      {{ showNew ? '✕' : '+' }}
    </button>

    <Transition name="slide">
      <div v-if="showNew" class="cat-new-row">
        <input
          v-model="newNombre"
          class="cat-new-input"
          placeholder="Nombre de la categoría…"
          maxlength="50"
          @keydown.enter.prevent="stageNew"
          @keydown.escape="showNew = false"
        />
        <button type="button" class="cat-new-ok" @click="stageNew">
          Añadir
        </button>
      </div>
    </Transition>

    <p v-if="errorMsg" class="cat-error">{{ errorMsg }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getCategorias, crearCategoria } from '../services/api.js'

const props = defineProps({
  modelValue: { type: String, default: '' },
  tipo: { type: String, default: 'gasto' },
  // Opcional: categorías ya cargadas desde el padre para evitar llamadas duplicadas
  categoriasExternas: { type: Array, default: null },
})

const emit = defineEmits(['update:modelValue', 'categoria-creada'])

const categorias    = ref([])
const showNew       = ref(false)
const newNombre     = ref('')
const pendingNombre = ref('')   // nombre temporal, aún no guardado en BD
const errorMsg      = ref('')

async function cargar() {
  if (props.categoriasExternas) {
    categorias.value = props.categoriasExternas
    return
  }
  const { data } = await getCategorias(props.tipo)
  categorias.value = data
}

function toggleNew() {
  showNew.value = !showNew.value
  newNombre.value = ''
  errorMsg.value = ''
}

// Al cambiar la selección: si el usuario elige una real, descartar el pendiente.
function onChange(e) {
  const val = e.target.value
  if (val !== pendingNombre.value) {
    pendingNombre.value = ''
  }
  emit('update:modelValue', val)
}

// Solo añade la categoría como opción temporal en el desplegable (sin llamar a la API).
function stageNew() {
  const nombre = newNombre.value.trim()
  if (!nombre) return
  errorMsg.value = ''

  // Comprobar duplicado local
  const existe = categorias.value.some(c => c.nombre.toLowerCase() === nombre.toLowerCase())
  if (existe) {
    errorMsg.value = 'Esa categoría ya existe.'
    return
  }

  pendingNombre.value = nombre
  emit('update:modelValue', nombre)
  showNew.value = false
  newNombre.value = ''
}

// Recargar categorías y limpiar selección al cambiar el tipo
watch(() => props.tipo, async () => {
  pendingNombre.value = ''
  emit('update:modelValue', '')
  await cargar()
})

onMounted(cargar)

// Llamado por el formulario padre al confirmar: persiste la categoría pendiente en BD.
async function flushPending() {
  if (!pendingNombre.value) return true
  // Si el usuario cambió la selección, ya no hay nada que guardar
  if (props.modelValue !== pendingNombre.value) {
    pendingNombre.value = ''
    return true
  }
  errorMsg.value = ''
  try {
    const { data } = await crearCategoria(pendingNombre.value, props.tipo)
    categorias.value.push(data)
    emit('categoria-creada', data)
    pendingNombre.value = ''
    return true
  } catch (e) {
    errorMsg.value = e.response?.data?.detail ?? 'Error al crear categoría.'
    return false
  }
}

defineExpose({ flushPending })
</script>

<style scoped>
.cat-select-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.cat-select {
  flex: 1;
  min-width: 0;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #f1f5f9;
  font-size: 0.9rem;
  cursor: pointer;
  transition: border-color 0.15s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2rem;
}
.cat-select:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }

.cat-add-btn {
  width: 32px;
  height: 32px;
  border-radius: 7px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #64748b;
  font-size: 1rem;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s, border-color 0.15s;
}
.cat-add-btn:hover { color: #818cf8; border-color: #6366f1; }

.cat-new-row {
  width: 100%;
  display: flex;
  gap: 0.4rem;
}
.cat-new-input {
  flex: 1;
  padding: 0.5rem 0.7rem;
  border-radius: 7px;
  border: 1px solid #6366f1;
  background: #0f172a;
  color: #f1f5f9;
  font-size: 0.875rem;
}
.cat-new-input:focus { outline: none; box-shadow: 0 0 0 3px rgba(99,102,241,0.12); }
.cat-new-ok {
  padding: 0.5rem 0.9rem;
  border-radius: 7px;
  border: none;
  background: #6366f1;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
.cat-new-ok:hover:not(:disabled) { opacity: 0.85; }
.cat-new-ok:disabled { opacity: 0.5; }

.cat-error { width: 100%; color: #fca5a5; font-size: 0.8rem; margin: 0; }

/* Transition */
.slide-enter-active, .slide-leave-active { transition: all 0.15s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
