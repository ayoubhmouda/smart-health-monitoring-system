<template>
  <!-- جعلنا الاتجاه ديناميكياً ليتحول تلقائياً لـ ltr عند قلب اللغة للإنجليزي -->
  <div class="w-full min-h-screen bg-[#0b1319] text-slate-300 font-sans antialiased m-0 p-0 overflow-x-hidden" :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'">
    
    <!-- الواجهة الأولى الناضجة: إذا لم يحدد الطبيب مريضاً، تعرض القائمة فوراً للاختيار المباشر -->
    <div v-if="!store.currentPatient" class="max-w-md mx-auto pt-16 px-4 space-y-6">
      <div class="text-center space-y-2">
        <h2 class="text-xl font-bold text-white tracking-tight">{{ $t('patient_monitoring_system') }}</h2>
        <p class="text-xs text-slate-500">{{ $t('select_patient_instruction') }}</p>
      </div>
      
      <!-- قائمة اختيار الحالات المباشرة في واجهة الاستقبال -->
      <div class="bg-[#111c24] border border-[#1e2d38] rounded-xl overflow-hidden shadow-xl">
        <div v-if="patients.length === 0" class="p-6 text-center text-xs text-slate-500">{{ $t('loading_patients') }}</div>
        <ul class="divide-y divide-[#1e2d38]">
          <li v-for="patient in patients" :key="patient.id"
              @click="store.selectPatient(patient)"
              class="p-4 hover:bg-[#162530] cursor-pointer transition-colors flex justify-between items-center"
          >
            <div>
              <div class="text-sm font-semibold text-white">{{ patient.full_name }}</div>
              <div class="text-xs text-slate-500 mt-1">{{ patient.element_type }}</div>
            </div>
            <span class="text-xs font-mono text-cyan-500 bg-cyan-500/10 px-2 py-1 rounded">{{ $t('age') }}: {{ patient.age }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- واجهة المراقبة الطبية بعد اختيار المريض -->
    <div v-else class="flex flex-col lg:flex-row min-h-screen w-full">
      
      <!-- محتوى لوحة المراقبة الفعلي -->
      <div class="flex-1 flex flex-col w-full">
        
        <!-- الهيدر الطبي المتناسق مع الهوية -->
        <header class="w-full bg-[#0b1319] border-b border-[#16222f] px-6 py-4 flex items-center justify-between">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-cyan-500 font-mono tracking-wider font-bold">{{ $t('patient_monitor') }} //</span>
              <h2 class="text-xl font-bold text-white">{{ store.currentPatient.full_name }}</h2>
              <!-- زر التاريخ الطبي -->
              <router-link
                :to="`/patients/${store.currentPatient.id}/medical-history`"
                class="flex items-center gap-1 text-xs text-slate-400 hover:text-cyan-400 transition px-3 py-1.5 rounded-lg border border-[#1e2d38] hover:border-cyan-500/50"
                title="التاريخ الطبي"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span class="hidden sm:inline">ملف المريض</span>
              </router-link>
            </div>
            <p class="text-xs text-slate-500 mt-1 flex items-center gap-2">
              <span>{{ $t('type') }}: {{ store.currentPatient.element_type }}</span>
              <span>•</span>
              <span>{{ $t('age') }}: {{ store.currentPatient.age }} {{ $t('years') }}</span>
              <span>•</span>
              <span class="font-mono">ID: {{ store.currentPatient.id }}</span>
            </p>
          </div>

          <!-- مؤقت التحديث البسيط -->
          <div class="text-xs font-mono text-slate-500 bg-[#111c24] border border-[#16222f] px-3 py-1.5 rounded-lg">
            {{ $t('auto_refresh') }}: {{ countdown }} {{ $t('seconds') }}
          </div>
        </header>

        <!-- شبكة العناصر الحيوية والمخططات -->
        <main class="flex-1 p-6 space-y-6 w-full">
          
          <!-- قسم الكروت الحيوية النقي -->
          <section class="space-y-3">
            <h3 class="text-xs font-bold text-slate-400 tracking-wider uppercase">{{ $t('current_physiological_context') }}</h3>
            <div class="flex overflow-x-auto pb-2 lg:pb-0 lg:grid lg:grid-cols-5 gap-4 snap-x">
              <MetricCard :title="$t('heart_rate')" :value="latestReadings.heart_rate ? latestReadings.heart_rate + ' bpm' : '-'" :status="hrStatus" color="border-[#1e2d38]" icon="heart" />
              <MetricCard :title="$t('oxygen_saturation')" :value="latestReadings.oxygen ? latestReadings.oxygen + '%' : '-'" :status="o2Status" color="border-[#1e2d38]" icon="o2" />
              <MetricCard :title="$t('activity')" :value="latestReadings.activity_level != null ? latestReadings.activity_level : '-'" :status="activityStatus" color="border-[#1e2d38]" icon="activity" />
              <MetricCard :title="$t('temperature')" :value="latestReadings.temperature ? latestReadings.temperature + ' °C' : '-'" :status="tempStatus" color="border-[#1e2d38]" icon="temp" />
              <MetricCard :title="$t('blood_pressure')" :value="bpDisplay || '-'" :status="bpStatus" color="border-[#1e2d38]" icon="bp" />
            </div>
          </section>

          <!-- المخططات والتحليلات المتناظرة -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start w-full">
            
            <!-- المخطط البياني الطبي النظيف -->
            <div class="lg:col-span-2 bg-[#111c24] rounded-xl border border-[#16222f] p-4 shadow-lg">
              <div class="flex items-center justify-between mb-4 border-b border-[#16222f] pb-3">
                <h3 class="text-xs font-bold text-slate-400">{{ $t('advanced_physiological_trends') }}</h3>
                <div class="flex items-center gap-3 text-[10px] font-mono font-bold">
                  <span class="flex items-center gap-1"><span class="w-2 h-0.5 bg-amber-500"></span>{{ $t('heart_pulse') }}</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-0.5 bg-cyan-400"></span>{{ $t('activity') }}</span>
                </div>
              </div>
              <TrendChart :readings="readings" />
            </div>

            <!-- محرك الاستدلال والتنبؤ النظيف بدون إضافات -->
            <div class="bg-[#111c24] rounded-xl border border-[#16222f] p-4 shadow-lg space-y-4">
              <div class="flex items-center justify-between border-b border-[#16222f] pb-3">
                <h3 class="text-xs font-bold text-slate-400">{{ $t('smart_inference_engine') }}</h3>
                <span v-if="latestInsight" :class="insightBadgeClass" class="px-2 py-0.5 rounded text-[10px] font-bold font-mono">
                  {{ latestInsight.severity }}
                </span>
              </div>
              <div class="space-y-2">
                <div class="flex justify-between items-center text-xs text-slate-400">
                  <span>{{ $t('prediction_confidence_level') }}</span>
                  <span class="font-mono text-cyan-400">{{ latestInsight ? (latestInsight.confidence * 100).toFixed(0) + '%' : '0%' }}</span>
                </div>
                <p class="text-xs text-slate-400 bg-[#0b1319] p-3 rounded-lg border border-[#16222f] leading-relaxed">
                  {{ latestInsight ? $t('insight_warning_message') : $t('insight_stable_message') }}
                </p>
              </div>
            </div>

          </div>

          <!-- تحكم الحساسات المباشر -->
          <section class="bg-[#111c24] rounded-xl border border-[#16222f] p-4 shadow-lg">
            <SensorControl :patient-id="store.currentPatient.id" />
          </section>

        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, onMounted, computed } from 'vue'
import { usePatientStore } from '../stores/patient'
import api from '../api'
import MetricCard from '../components/MetricCard.vue'
import TrendChart from '../components/TrendChart.vue'
import SensorControl from '../components/SensorControl.vue'

const store = usePatientStore()
const patients = ref([])
const latestReadings = ref({})
const latestInsight = ref(null)
const readings = ref([])
const countdown = ref(30)
let countdownTimer = null

const fetchPatients = async () => {
  try {
    const res = await api.get('/api/monitored-elements/')
    patients.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('فشل جلب المرضى:', e)
  }
}

const fetchData = async () => {
  if (!store.currentPatient) return
  try {
    const res = await api.get('/api/sensor-readings/', {
      params: { sensor__monitored_element: store.currentPatient.id, ordering: '-recorded_at', limit: 20 }
    })
    const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
    readings.value = data

    latestReadings.value = {
      heart_rate: data.find(r => r.sensor?.sensor_type?.name === 'Heart Rate')?.value,
      oxygen: data.find(r => r.sensor?.sensor_type?.name === 'Oxygen Saturation')?.value,
      activity_level: data.find(r => r.sensor?.sensor_type?.name === 'Activity Level')?.value,
      temperature: data.find(r => r.sensor?.sensor_type?.name === 'Body Temperature')?.value,
      bp_sys: data.find(r => r.sensor?.sensor_type?.name === 'Blood Pressure Systolic')?.value,
      bp_dia: data.find(r => r.sensor?.sensor_type?.name === 'Blood Pressure Diastolic')?.value,
    }

    const insightRes = await api.get('/api/insights/', {
      params: { monitored_element: store.currentPatient.id, ordering: '-detected_at', limit: 1 }
    })
    latestInsight.value = (Array.isArray(insightRes.data) ? insightRes.data : insightRes.data.results)?.[0] || null
  } catch (e) {
    console.error('فشل جلب المعطيات الحيوية:', e)
  }
}

const startCountdown = () => {
  countdown.value = 30
  clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      fetchData()
      countdown.value = 30
    }
  }, 1000)
}

watch(() => store.currentPatient, (newPatient) => {
  if (newPatient) {
    fetchData()
    startCountdown()
  }
}, { immediate: true })

onMounted(() => {
  fetchPatients()
})

onUnmounted(() => {
  clearInterval(countdownTimer)
})

const hrStatus = computed(() => {
  const v = latestReadings.value.heart_rate
  if (!v) return 'Normal'
  return (v > 100 || v < 60) ? 'Critical' : 'Good'
})
const o2Status = computed(() => {
  const v = latestReadings.value.oxygen
  if (!v) return 'Normal'
  return v < 95 ? 'Critical' : 'Good'
})
const activityStatus = computed(() => 'Normal')
const tempStatus = computed(() => {
  const v = latestReadings.value.temperature
  if (!v) return 'Normal'
  return (v > 37.5 || v < 36.5) ? 'Critical' : 'Good'
})
const bpStatus = computed(() => {
  const sys = latestReadings.value.bp_sys
  const dia = latestReadings.value.bp_dia
  if (!sys || !dia) return 'Normal'
  return (sys > 140 || dia > 90) ? 'Critical' : 'Good'
})
const bpDisplay = computed(() => {
  if (latestReadings.value.bp_sys && latestReadings.value.bp_dia) {
    return `${latestReadings.value.bp_sys}/${latestReadings.value.bp_dia}`
  }
  return null
})
const insightBadgeClass = computed(() => {
  const s = latestInsight.value?.severity
  if (s === 'high' || s === 'critical') return 'text-rose-400 bg-rose-500/10'
  return 'text-emerald-400 bg-emerald-500/10'
})
</script>