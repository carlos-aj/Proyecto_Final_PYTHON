import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Movimientos from '../views/Movimientos.vue'
import Estadisticas from '../views/Estadisticas.vue'
import Objetivos from '../views/Objetivos.vue'
import Recurrentes from '../views/Recurrentes.vue'

const routes = [
  { path: '/',              name: 'Dashboard',    component: Dashboard },
  { path: '/movimientos',   name: 'Movimientos',  component: Movimientos },
  { path: '/estadisticas',  name: 'Estadisticas', component: Estadisticas },
  { path: '/objetivos',     name: 'Objetivos',    component: Objetivos },
  { path: '/recurrentes',   name: 'Recurrentes',  component: Recurrentes },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
