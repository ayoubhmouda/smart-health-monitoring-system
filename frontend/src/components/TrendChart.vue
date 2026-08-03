<!-- TrendChart.vue -->
<template>
  <div class="w-full">
    <!-- حاوية المخطط بارتفاع ثابت لضمان الاستجابة التامة على كافة الشاشات -->
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
  
  // ترتيب القراءات زمنياً من الأقدم للأحدث لعرض التدرج السليم على المحور الأفقي
  const sortedReadings = [...props.readings].reverse()
  
  // تجميع نقاط القراءة لكلا المؤشرين الفسيولوجيين المتناغمين
  const hrDataPoints = sortedReadings.filter(r => r.sensor?.sensor_type?.name === 'Heart Rate')
  const bpSysDataPoints = sortedReadings.filter(r => r.sensor?.sensor_type?.name === 'Blood Pressure Systolic')

  // توليد التسميات الزمنية للمحور الأفقي بناءً على طابع وقت نبض القلب
  const labels = hrDataPoints.map(r => {
    if (!r.recorded_at) return ''
    const date = new Date(r.recorded_at)
    return isNaN(date.getTime()) ? '' : date.toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit' })
  })
  
  const hrValues = hrDataPoints.map(r => r.value)
  const bpSysValues = bpSysDataPoints.map(r => r.value)

  // تدمير المخطط القديم لمنع تسريب الذاكرة (Memory Leak) وإعادة البناء بنقاء
  if (chartInstance) chartInstance.destroy()

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'نبضات القلب (bpm)',
          data: hrValues,
          borderColor: '#f43f5e', // لون أحمر مرجاني دافئ وأنيق
          borderWidth: 1.8,       // خط محدد بوضوح كالأجهزة السريرية
          backgroundColor: 'rgba(244, 63, 94, 0.02)', // ظل وردي ناعم جداً تحت المنحنى
          tension: 0.35,          // تموج انسيابي يحاكي تموجات القلب الحقيقية
          fill: true,
          pointRadius: 0,         // إلغاء النقاط الدائرية لإبقاء المنحنى نقياً
          pointHoverRadius: 4,
          pointBackgroundColor: '#f43f5e',
        },
        {
          label: 'الضغط الانقباضي (mmHg)',
          data: bpSysValues,
          borderColor: '#0ea5e9', // لون أزرق سماوي طبي نقي ومريح
          borderWidth: 1.8,
          backgroundColor: 'rgba(14, 165, 233, 0.02)', // ظل أزرق ناعم جداً تحت المنحنى
          tension: 0.35,
          fill: true,
          pointRadius: 0,
          pointHoverRadius: 4,
          pointBackgroundColor: '#0ea5e9',
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }, // إخفاء عناصر التحكم التقليدية لجعل التصميم أرقى
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(15, 23, 42, 0.9)', // خلفية فحمية أنيقة ومظلمة للتلميحات
          titleFont: { size: 11, family: 'sans-serif', weight: 'bold' },
          bodyFont: { size: 11, family: 'monospace' },
          padding: 10,
          cornerRadius: 8,
          displayColors: true
        }
      },
      scales: {
        x: { 
          ticks: { 
            color: '#64748b', // لون رمادي ناعم ونظيف للأرقام والتوقيت
            font: { size: 9, family: 'monospace' }, 
            maxTicksLimit: 6 
          },
          grid: { 
            color: '#f1f5f9', // خطوط شبكة ناعمة جداً تندمج مع الخلفية الفاتحة للكرت
            drawTicks: false 
          }
        },
        y: { 
          ticks: { 
            color: '#64748b', 
            font: { size: 9, family: 'monospace' } 
          },
          grid: { 
            color: '#f1f5f9', 
            drawTicks: false 
          }
        }
      }
    }
  })
}

// مراقبة القراءات القادمة من الحساسات بشكل مستمر لإعادة تحديث المخطط تلقائياً
watch(() => props.readings, () => buildChart(), { deep: true })
onMounted(() => buildChart())
onUnmounted(() => { if (chartInstance) chartInstance.destroy() })
</script>