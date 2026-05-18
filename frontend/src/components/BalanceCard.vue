<template>
  <div class="balance-card" :class="balance >= 0 ? 'positive' : 'negative'">
    <p class="balance-label">Balance total</p>
    <p class="balance-amount">{{ formattedBalance }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  balance: { type: Number, default: 0 },
})

const formattedBalance = computed(() => {
  const sign = props.balance >= 0 ? '+' : ''
  return `${sign}${props.balance.toFixed(2)} €`
})
</script>

<style scoped>
.balance-card {
  border-radius: 12px;
  padding: 1.5rem 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.balance-card.positive {
  background: linear-gradient(135deg, #166534, #22c55e);
  color: #f0fdf4;
}

.balance-card.negative {
  background: linear-gradient(135deg, #7f1d1d, #ef4444);
  color: #fff1f2;
}

.balance-label {
  font-size: 0.9rem;
  opacity: 0.85;
  margin: 0 0 0.4rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.balance-amount {
  font-size: 2.4rem;
  font-weight: 800;
  margin: 0;
}
</style>
