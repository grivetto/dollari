
<template>
  <div class="dashboard">
    <h1>Denaro V3 Trading Dashboard</h1>
    <div class="status-card">
      <h2>Sniper Status</h2>
      <p v-if="sniperStatus === 'ACTIVE'" class="active">Attivo</p>
      <p v-else class="error">Errore: {{ sniperStatus }}</p>
    </div>
    <div class="profit-card">
      <h2>Profitto Totale</h2>
      <p>{{ totalProfit }} EUR</p>
    </div>
    <div class="chart-card">
      <h2>Grafico Profitti</h2>
      <canvas id="profitChart"></canvas>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import Chart from 'chart.js';

export default {
  name: 'Dashboard',
  setup() {
    const sniperStatus = ref('');
    const totalProfit = ref(0);
    const profitData = ref([]);

    // Chiamata API per ottenere lo stato e i profitti
    const fetchDashboardData = async () => {
      try {
        const res = await fetch('http://93.43.252.114:8080/api/profit');
        const data = await res.json();
        sniperStatus.value = data.status || 'UNKNOWN';
        totalProfit.value = data.total_profit || 0;
        profitData.value = data.profit_history || [];
      } catch (err) {
        console.error('Errore API:', err);
        sniperStatus.value = 'ERROR';
      }
    };

    onMounted(() => {
      fetchDashboardData();
      // Aggiorna ogni 30 secondi
      setInterval(fetchDashboardData, 30000);
    });

    return { sniperStatus, totalProfit, profitData };
  }
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
  font-family: Arial, sans-serif;
}
.status-card, .profit-card, .chart-card {
  margin: 20px 0;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}
.active { color: green; }
.error { color: red; }
</style>
