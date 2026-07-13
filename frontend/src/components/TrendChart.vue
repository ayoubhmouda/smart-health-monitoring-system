<template>
  <div class="w-full">
    <div style="height: 220px; position: relative;">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  readings: { type: Array, default: () => [] }
})

const chartCanvas = ref(null)
let chartInstance = null

const buildChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  const sortedReadings = [...props.readings].reverse()
  
  const hrDataPoints = sortedReadings.filter(r => r.sensor?.sensor_type?.name === 'Heart Rate')
  const activityDataPoints = sortedReadings.filter(r => r.sensor?.sensor_type?.name === 'Activity Level')

  const labels = hrDataPoints.map(r => {
    if (!r.recorded_at) return ''
    const date = new Date(r.recorded_at)
    return isNaN(date.getTime()) ? '' : date.toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit' })
  })
  
  const hrValues = hrDataPoints.map(r => r.value)
  const activityValues = activityDataPoints.map(r => r.value)

  if (chartInstance) chartInstance.destroy()

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'نبضات القلب',
          data: hrValues,
          borderColor: '#f59e0b',
          borderWidth: 1.5, // خط رفيع جداً ومحدد كالأجهزة الطبية
          backgroundColor: 'rgba(245, 158, 11, 0.03)', // تعبئة خفيفة للغاية شبه معدومة للتموجات
          tension: 0.4, 
          fill: true,
          pointRadius: 0, // إلغاء النقاط الدائرية المشوهة للمنحنى
          pointHoverRadius: 3,
        },
        {
          label: 'مستوى النشاط',
          data: activityValues,
          borderColor: '#22d3ee',
          borderWidth: 1.2,
          backgroundColor: 'rgba(34, 211, 238, 0.01)',
          tension: 0.4,
          fill: true,
          pointRadius: 0,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false } // تم إزالة المربع الأسود المزعج نهائياً بناءً على طلبك
      },
      scales: {
        x: { 
          ticks: { color: '#475569', font: { size: 9, family: 'monospace' }, maxTicksLimit: 5 },
          grid: { color: '#16222f', drawTicks: false }
        },
        y: { 
          ticks: { color: '#475569', font: { size: 9, family: 'monospace' } },
          grid: { color: '#16222f', drawTicks: false }
        }
      }
    }
  })
}

watch(() => props.readings, () => buildChart(), { deep: true })
onMounted(() => buildChart())
onUnmounted(() => { if (chartInstance) chartInstance.destroy() })
</script>