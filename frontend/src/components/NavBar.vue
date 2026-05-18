<template>
  <nav class="navbar">
    <RouterLink to="/" class="navbar-brand">
      <TrendingUp :size="20" />
      <span>Gestor de Gastos</span>
    </RouterLink>
    <div class="navbar-links">
      <RouterLink to="/"><LayoutDashboard :size="15" /><span>Dashboard</span></RouterLink>
      <RouterLink to="/movimientos"><ArrowLeftRight :size="15" /><span>Movimientos</span></RouterLink>
      <RouterLink to="/recurrentes"><Repeat :size="15" /><span>Recurrentes</span></RouterLink>
      <RouterLink to="/estadisticas"><BarChart3 :size="15" /><span>Estadísticas</span></RouterLink>
      <RouterLink to="/objetivos"><Target :size="15" /><span>Objetivos</span></RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { TrendingUp, LayoutDashboard, ArrowLeftRight, BarChart3, Target, Repeat } from 'lucide-vue-next'
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #1e293b;
  padding: 0.75rem 2rem;
  border-bottom: 1px solid #334155;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #f8fafc;
  text-decoration: none;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.navbar-links {
  display: flex;
  gap: 0.25rem;
}

.navbar-links a {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
}

.navbar-links a:hover {
  background: #334155;
  color: #e2e8f0;
}

.navbar-links a.router-link-active {
  background: #0f172a;
  color: #38bdf8;
  font-weight: 600;
}
</style>
