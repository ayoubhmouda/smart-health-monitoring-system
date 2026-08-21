<!-- TrendChart.vue -->
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

const formatTime = (ts) => {
  if (!ts) return ''
  const date = new Date(ts)
  return isNaN(date.getTime()) 
    ? '' 
    : date.toLocaleTimeString('ar-LY', { hour: '2-digit', minute: '2-digit' })
}

// 🟢 دالة فرز مرنة تفحص كائنات الـ WebSocket والـ API معاً دون انقطاع
const getSensorName = (r) => {
  if (!r) return ''
  return r.sensor_name || r.sensor?.sensor_type?.name || ''
}

const updateOrCreateChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  
  // 1. فرز كافة القراءات زمنياً
  const sortedReadings = [...props.readings].sort((a, b) => new Date(a.recorded_at) - new Date(b.recorded_at))
  
  // 2. تجميع القراءات حسب الطابع الزمني الموحد بدعم المسميات الفلكية المباشرة والمسطحة
  const timeMap = new Map()

  sortedReadings.forEach(r => {
    if (!r.recorded_at) return
    const timeKey = formatTime(r.recorded_at)
    if (!timeKey) return

    if (!timeMap.has(timeKey)) {
      timeMap.set(timeKey, { hr: null, bpSys: null, rawTime: r.recorded_at })
    }

    const entry = timeMap.get(timeKey)
    const sensorName = getSensorName(r) // 🟢 استخدام الفلترة المصلحة

    if (sensorName === 'Heart Rate' && r.value != null) {
      entry.hr = Number(r.value)
    } else if (sensorName === 'Blood Pressure Systolic' && r.value != null) {
      entry.bpSys = Number(r.value)
    }
  })

  const labels = []
  const hrValues = []
  const bpSysValues = []

  timeMap.forEach((entry, timeKey) => {
    labels.push(timeKey)
    hrValues.push(entry.hr)
    bpSysValues.push(entry.bpSys)
  })

  // 3. إضافة نقاط مستقبلية فارغة للتوسع الأفقِي
  if (labels.length > 0) {
    const lastReading = sortedReadings[sortedReadings.length - 1]
    const lastTime = lastReading ? new Date(lastReading.recorded_at) : null
    
    if (lastTime && !isNaN(lastTime.getTime())) {
      for (let i = 1; i <= 3; i++) {
        const futureDate = new Date(lastTime.getTime() + i * 2 * 60 * 1000)
        labels.push(formatTime(futureDate))
        hrValues.push(null)
        bpSysValues.push(null)
      }
    }
  }

  // 4. التحديث الانسيابي عند وجود المخطط بالذاكرة
  if (chartInstance) {
    chartInstance.data.labels = labels
    chartInstance.data.datasets[0].data = hrValues
    chartInstance.data.datasets[1].data = bpSysValues
    chartInstance.update('none')
    return
  }

  // 5. البناء الأولي للمخطط
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'نبضات القلب (bpm)',
          data: hrValues,
          borderColor: '#f43f5e',
          borderWidth: 2,
          backgroundColor: 'rgba(244, 63, 94, 0.04)',
          tension: 0.35,
          fill: true,
          spanGaps: true,
          pointRadius: (context) => {
            const index = context.dataIndex
            const count = context.dataset.data.length
            return index === count - 4 ? 5 : 0
          },
          pointHoverRadius: 6,
          pointBackgroundColor: '#f43f5e',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
        },
        {
          label: 'الضغط الانقباضي (mmHg)',
          data: bpSysValues,
          borderColor: '#0ea5e9',
          borderWidth: 2,
          backgroundColor: 'rgba(14, 165, 233, 0.04)',
          tension: 0.35,
          fill: true,
          spanGaps: true,
          pointRadius: (context) => {
            const index = context.dataIndex
            const count = context.dataset.data.length
            return index === count - 4 ? 5 : 0
          },
          pointHoverRadius: 6,
          pointBackgroundColor: '#0ea5e9',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 400,
        easing: 'easeOutQuart'
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: {
        x: { 
          ticks: { color: '#64748b', font: { size: 9, family: 'monospace' }, maxTicksLimit: 12 },
          grid: { color: '#f1f5f9', drawTicks: false }
        },
        y: { 
          suggestedMin: 50,
          suggestedMax: 150,
          ticks: { color: '#64748b', font: { size: 9, family: 'monospace' } },
          grid: { color: '#f1f5f9', drawTicks: false }
        }
      }
    }
  })
}

watch(() => props.readings, () => updateOrCreateChart(), { deep: true })

onMounted(() => updateOrCreateChart())

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>