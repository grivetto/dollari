
<template>
  <div>
    <h3>Grafico Profitti</h3>
    <canvas id="profitChart"></canvas>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import Chart from 'chart.js';

export default {
  name: 'ProfitChart',
  setup() {
    const chartRef = ref(null);
    let chartInstance = null;

    const updateChart = (data) => {
      if (chartInstance) {
        chartInstance.destroy();
      }
      
      const ctx = document.getElementById('profitChart').getContext('2d');
      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels || [],
          datasets: [{
            label: 'Profitto (EUR)',
            data: data.values || [],
            borderColor: '#3498db',
            fill: false,
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true },
            title: { display: true, text: 'Andamento Profitti' }
          }
        }
      });
    };

    onMounted(() => {
      // Esempio di dati statici (da sostituire con API reale)
      const sampleData = {
        labels: ['09:00', '10:00', '11:00', '12:00'],
        values: [0, 2.5, 1.8, 3.2]
      };
      updateChart(sampleData);
    });

    return { updateChart };
  }
};
</script>
