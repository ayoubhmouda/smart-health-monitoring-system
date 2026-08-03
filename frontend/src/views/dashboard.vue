<!-- dashboard.vue -->
<template>
  <!-- الهيكل العام المشرق والمنقح مع خلفية متوازنة التباين #F0F6F5 ودعم اتجاهات اللغة ديناميكياً -->
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased m-0 p-0 overflow-x-hidden flex" :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'">
    
    <!-- واجهة المراقبة الطبية الشاملة والمشرقة بعد اختيار المريض -->
    <div v-if="!store.currentPatient" class="h-full flex-1 flex flex-col items-center justify-center text-center py-20 px-6">
      <div class="bg-white border border-slate-200/85 rounded-3xl p-8 shadow-sm max-w-md flex flex-col items-center">
        <div class="w-20 h-20 rounded-2xl bg-teal-50 flex items-center justify-center text-teal-600 mb-5 shadow-inner">
          <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-extrabold text-slate-800 mb-2">مرحباً بك في نظام المراقبة الذكية</h2>
        <p class="text-slate-500 text-sm leading-relaxed">
          يرجى اختيار مريض من القائمة الجانبية لبدء مراقبة علاماته الحيوية وعرض تنبؤات الخطر واستبصارات شبكة الأمان فوراً.
        </p>
      </div>
    </div>

    <!-- واجهة المراقبة الطبية الفعالة بعد تحديد المريض -->
    <div v-else class="flex-1 flex flex-col min-w-0 min-h-screen">
      
      <!-- هيدر المراقبة السريرية البارز والناصع -->
      <header class="w-full bg-white border-b border-slate-200/80 px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <div class="flex items-center gap-3">
            <span class="text-xs text-teal-600 font-mono tracking-wider font-extrabold uppercase">لوحة مراقبة فسيولوجية</span>
            <h2 class="text-xl font-extrabold text-slate-800 tracking-tight">{{ store.currentPatient.full_name }}</h2>
            
            <!-- زر ملف المريض السريري والتاريخ الطبي -->
            <router-link
              :to="`/patients/${store.currentPatient.id}/medical-history`"
              class="flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 hover:bg-white hover:text-teal-600 transition-all px-3.5 py-2 rounded-2xl border border-slate-200 hover:border-teal-500/50 shadow-sm"
              title="عرض السجل الطبي والتاريخ المرضي"
            >
              <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span class="font-bold">ملف المريض</span>
            </router-link>
          </div>
          
          <p class="text-xs text-slate-400 mt-1.5 flex items-center gap-2 font-medium">
            <span>{{ $t('type') }}: {{ store.currentPatient.element_type }}</span>
            <span>•</span>
            <span>{{ $t('age') }}: {{ store.currentPatient.age }} {{ $t('years') }}</span>
            <span>•</span>
            <span class="font-mono bg-slate-100 text-slate-500 px-2.5 py-0.5 rounded-lg">ID: {{ store.currentPatient.id }}</span>
          </p>
        </div>

        <!-- مؤقت التحديث البسيط والمشرق -->
        <div class="text-xs font-mono font-bold text-slate-600 bg-white border border-slate-200/80 px-4 py-2 rounded-2xl flex items-center gap-2 select-none shadow-sm self-start sm:self-auto">
          <span class="w-2 h-2 rounded-full bg-teal-500 animate-ping"></span>
          <span>تحديث فوري: {{ countdown }} ثانية</span>
        </div>
      </header>

      <!-- شبكة العناصر الحيوية والمخططات والتحليلات -->
      <main class="flex-1 p-6 space-y-6 w-full overflow-y-auto">
        
        <!-- 2️⃣ شبكة المؤشرات الحيوية المحدثة والمصنفة سريرياً وثلاثياً -->
        <section class="grid grid-cols-1 xl:grid-cols-12 gap-5 w-full items-stretch">
          
          <!-- الحاوية أ: المؤشرات الفسيولوجية الأساسية الـ 5 (تدعم التمرير الأفقي للجوال والاصطفاف الخماسي على الكمبيوتر) -->
          <div class="xl:col-span-8 bg-white border border-slate-200/80 rounded-3xl p-5 shadow-sm shadow-slate-100/50 flex flex-col justify-between gap-3">
            <h4 class="text-xs font-extrabold text-slate-400 tracking-wider uppercase">المؤشرات الفسيولوجية الأساسية</h4>
            <div class="flex overflow-x-auto pb-3 lg:pb-0 lg:grid lg:grid-cols-5 gap-4 snap-x custom-scrollbar">
              <!-- 1. نبضات القلب -->
              <MetricCard :title="$t('heart_rate')" :value="latestReadings.heart_rate ? latestReadings.heart_rate + ' bpm' : '-'" :status="hrStatus" icon="heart" />
              <!-- 2. ضغط الدم الشرياني -->
              <MetricCard :title="$t('blood_pressure')" :value="bpDisplay || '-'" :status="bpStatus" icon="bp" />
              <!-- 3. تشبع الأكسجين -->
              <MetricCard :title="$t('oxygen_saturation')" :value="latestReadings.oxygen ? latestReadings.oxygen + '%' : '-'" :status="o2Status" icon="o2" />
              <!-- 4. معدل التنفس الطبي المطور بأيقونة الرياح من غوغل (cloud) -->
              <MetricCard :title="$t('respiratory_rate')" :value="latestReadings.respiratory_rate ? latestReadings.respiratory_rate + ' rpm' : '-'" :status="rrStatus" icon="cloud" />
              <!-- 5. درجة حرارة الجسم بأيقونة لهب الحرارة (fire) -->
              <MetricCard :title="$t('temperature')" :value="latestReadings.temperature ? latestReadings.temperature + ' °C' : '-'" :status="tempStatus" icon="fire" />
            </div>
          </div>

          <!-- 🟢 التعديل المطور: دمج حاوية النشاط والبيئة في شبكة ثنائية الأعمدة لتظهرا بجانب بعضهما في الجوال -->
          <div class="grid grid-cols-2 gap-4 xl:col-span-4 xl:grid-cols-2 xl:gap-5 items-stretch">
            
            <!-- الحاوية ب: النشاط الحركي (حاوية مستقلة لحساس النشاط الحركي بأيقونة البرق السهمية bolt) -->
            <div class="bg-white border border-slate-200/80 rounded-3xl p-3.5 sm:p-5 shadow-sm shadow-slate-100/50 flex flex-col justify-between gap-3">
              <h4 class="text-xs font-extrabold text-slate-400 tracking-wider uppercase">النشاط الحركي</h4>
              <MetricCard :title="$t('activity')" :value="latestReadings.activity_level != null ? latestReadings.activity_level : '-'" :status="activityStatus" icon="bolt" class="w-full" />
            </div>

            <!-- الحاوية ج: الحساسات البيئية وسياق الغرفة (حاوية مستقلة لدرجة حرارة الغرفة بأيقونة المنزل home) -->
            <div class="bg-white border border-slate-200/80 rounded-3xl p-3.5 sm:p-5 shadow-sm shadow-slate-100/50 flex flex-col justify-between gap-3">
              <h4 class="text-xs font-extrabold text-slate-400 tracking-wider uppercase">السياق البيئي</h4>
              <MetricCard :title="$t('room_temperature')" :value="latestReadings.room_temperature ? latestReadings.room_temperature + ' °C' : '-'" :status="roomTempStatus" icon="home" class="w-full" />
            </div>

          </div>

        </section>

        <!-- المخططات والتحليلات المتناظرة والمشرقة -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start w-full">
          
          <!-- مخطط الاتجاهات الطبية المطور لـ (النبض + الضغط الانقباضي) -->
          <div class="lg:col-span-2 order-2 lg:order-1 bg-white rounded-3xl border border-slate-200/80 p-5 shadow-sm">
            <div class="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <h3 class="text-xs font-extrabold text-slate-500">مخططات الاتجاه الفسيولوجي المتقدمة</h3>
              <div class="flex items-center gap-4 text-[10px] font-bold">
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-1 bg-[#f43f5e] rounded-full"></span>نبضات القلب</span>
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-1 bg-[#0ea5e9] rounded-full"></span>الضغط الانقباضي</span>
              </div>
            </div>
            <TrendChart :readings="readings" />
          </div>

          <!-- استدعاء مكون التنبؤ المستقل والمطور للذكاء الاصطناعي (InsightPanel) -->
          <InsightPanel class="lg:col-span-1 order-1 lg:order-2" :insight="latestInsight" />

        </div>

        <!-- لوحة التحكم المركزية بالسيناريوهات الطبية للأجهزة الـ 8 للمريض -->
        <section class="w-full">
          <SensorControl :patient-id="store.currentPatient.id" />
        </section>

      </main>
    </div>

  </div>
</template>

<!-- باقي الـ script setup تظل كما هي دون أي تعديل -->
<script setup>
import { ref, watch, onUnmounted, onMounted, computed } from 'vue'
import { usePatientStore } from '../stores/patient'
import api from '../api'
import MetricCard from '../components/MetricCard.vue'
import TrendChart from '../components/TrendChart.vue'
import SensorControl from '../components/SensorControl.vue'
import InsightPanel from '../components/insightPanel.vue'

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
    console.error('فشل جلب قائمة المرضى:', e)
  }
}

// سحب المعطيات الفسيولوجية والبيئية والسياقية للمريض المحدد
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
      // جلب قيمة معدل التنفس (Respiratory Rate) من الحساسات
      respiratory_rate: data.find(r => r.sensor?.sensor_type?.name === 'Respiratory Rate')?.value,
      // جلب قيمة درجة حرارة الغرفة (Room Temperature) من الحساسات
      room_temperature: data.find(r => r.sensor?.sensor_type?.name === 'Room Temperature')?.value,
    }

    const insightRes = await api.get('/api/insights/', {
      params: { monitored_element: store.currentPatient.id, ordering: '-detected_at', limit: 1 }
    })
    latestInsight.value = (Array.isArray(insightRes.data) ? insightRes.data : insightRes.data.results)?.[0] || null
  } catch (e) {
    console.error('فشل جلب المعطيات الحيوية والسياقية:', e)
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

// الوعي الكامل بالسياق فسيولوجياً لضبط وتلوين بطاقة النبض ديناميكياً مع مستوى الحركة لتلافي الإنذارات الكاذبة
const hrStatus = computed(() => {
  const v = latestReadings.value.heart_rate
  const act = latestReadings.value.activity_level ?? 0
  if (!v) return 'Normal'
  
  const tolerance = act >= 2 ? 1.3 : (act === 1 ? 1.1 : 1.0)
  const maxHR = 100 * tolerance
  const minHR = 50 / tolerance
  
  return (v > maxHR || v < minHR) ? 'Critical' : 'Good'
})

// الأكسجين مستقر عند حدود عتبة الأمان لـ (ThresholdPredictor): تحت 92 حرج
const o2Status = computed(() => {
  const v = latestReadings.value.oxygen
  if (!v) return 'Normal'
  return v < 92 ? 'Critical' : 'Good'
})

const activityStatus = computed(() => 'Normal')

// الحرارة مستقرة عند حدود عتبة الأمان لـ (ThresholdPredictor): من 36.0 إلى 37.8 طبيعي
const tempStatus = computed(() => {
  const v = latestReadings.value.temperature
  if (!v) return 'Normal'
  return (v > 37.8 || v < 36.0) ? 'Critical' : 'Good'
})

// حساب حالة معدل التنفس ديناميكياً مع مستوى النشاط لتلافي الإنذارات الكاذبة في الشاشة
const rrStatus = computed(() => {
  const v = latestReadings.value.respiratory_rate
  const act = latestReadings.value.activity_level ?? 0
  if (!v) return 'Normal'
  
  const tolerance = act >= 2 ? 1.3 : (act === 1 ? 1.1 : 1.0)
  const maxRR = 20 * tolerance
  const minRR = 12 / tolerance
  
  return (v > maxRR || v < minRR) ? 'Critical' : 'Good'
})

// حساب حالة درجة حرارة الغرفة (البيئية) بشكل مستقر وهادئ
const roomTempStatus = computed(() => {
  const v = latestReadings.value.room_temperature
  if (!v) return 'Normal'
  return (v > 26 || v < 18) ? 'Caution' : 'Good'
})

// الضغط الانقباضي يتعدل ديناميكياً مع الحركة والنشاط فسيولوجياً
const bpStatus = computed(() => {
  const sys = latestReadings.value.bp_sys
  const dia = latestReadings.value.bp_dia
  const act = latestReadings.value.activity_level ?? 0
  if (!sys || !dia) return 'Normal'
  
  const tolerance = act >= 2 ? 1.3 : (act === 1 ? 1.1 : 1.0)
  const maxSys = 140 * tolerance
  const minSys = 90 / tolerance
  
  const isSysAbnormal = sys > maxSys || sys < minSys
  const isDiaAbnormal = dia > 90 || dia < 60
  
  return (isSysAbnormal || isDiaAbnormal) ? 'Critical' : 'Good'
})

const bpDisplay = computed(() => {
  if (latestReadings.value.bp_sys && latestReadings.value.bp_dia) {
    return `${latestReadings.value.bp_sys}/${latestReadings.value.bp_dia}`
  }
  return null
})
</script>

<style scoped>
/* شريط تمرير ناعم ومشرق ومتناسق للبطاقات الـ 5 على الموبايل والجوال */
.custom-scrollbar::-webkit-scrollbar {
  height: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #0d9488;
}
</style>