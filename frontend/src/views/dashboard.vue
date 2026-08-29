<!-- src/views/dashboard.vue -->
<template>
  <!-- الخلفية العامة: تدرج ناعم مع تأثير إضاءة محيطية دافئة بلون تراكوازي -->
  <!-- تم تثبيت الارتفاع h-screen + overflow-hidden هنا لضمان أن main هو الوحيد القابل للتمرير -->
  <div 
    class="w-full h-screen bg-slate-50/70 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-teal-100/30 via-slate-50 to-teal-50/20 text-slate-700 font-sans antialiased m-0 p-0 overflow-hidden flex" 
    :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'"
  >
    
    <!-- واجهة المراقبة الطبية قبل اختيار المريض (بطاقة زجاجية عائمة) -->
    <div v-if="!store.currentPatient" class="h-full flex-1 flex flex-col items-center justify-center text-center py-20 px-6">
      <div class="bg-white/80 backdrop-blur-xl border border-white/90 rounded-[2.5rem] p-10 shadow-2xl shadow-teal-950/5 max-w-md flex flex-col items-center relative overflow-hidden group hover:shadow-teal-900/10 transition-all duration-500">
        <div class="absolute -top-12 -right-12 w-32 h-32 bg-teal-400/15 rounded-full blur-2xl"></div>
        
        <div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-teal-500/10 to-teal-700/20 flex items-center justify-center text-teal-700 mb-6 shadow-inner border border-teal-500/20 group-hover:scale-105 transition-transform duration-300">
          <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        
        <h2 class="text-xl font-black text-teal-950 mb-2.5 tracking-tight">مرحباً بك في نظام المراقبة الذكية</h2>
        <p class="text-slate-500 text-xs sm:text-sm leading-relaxed font-medium">
          يرجى اختيار مريض من القائمة الجانبية لبدء مراقبة علاماته الحيوية وعرض تنبؤات الخطر واستبصارات شبكة الأمان فوراً.
        </p>
      </div>
    </div>

    <!-- واجهة المراقبة الطبية بعد تحديد المريض -->
    <div v-else class="flex-1 flex flex-col min-w-0 h-full relative">
      <main class="flex-1 min-h-0 overflow-y-auto">

        <!-- Page Header -->
        <header class="px-6 sm:px-7 xl:px-9 pt-6 pb-5">
          <div class="flex items-center justify-between gap-4">

            <div class="min-w-0">
              <h1 class="text-xl font-extrabold tracking-tight text-slate-900 truncate">
                لوحة تحكم المراقبة المباشرة
              </h1>

              <p class="mt-1 text-xs text-slate-400 font-medium">
                مراقبة فورية للعلامات الفسيولوجية والنشاط والبيئة المحيطة
              </p>
            </div>
          </div>
        </header>


        <!-- STICKY PATIENT HEADER (حر بالكامل بـ bg-transparent وبادينج صفر ليلتصق بجزء الكروت تحت تماماً) -->
        <div
          class="sticky top-0 z-30 px-6 sm:px-7 xl:px-9 pt-0 pb-0 bg-transparent"
        >
          <PatientHeader
            :patient="store.currentPatient"
            :is-ws-connected="alertsStore.isWsConnected"
            :just-updated="alertsStore.justUpdated"
            :countdown="alertsStore.countdown"
            :last-updated-time="alertsStore.lastUpdatedTime"
          />
        </div>


        <!-- Dashboard Content -->
        <div class="px-6 sm:px-7 xl:px-9 mt-6 pb-10 space-y-6">

          <!-- ===================================================
               VITAL SIGNS
          ==================================================== -->
          <!-- كارت الأب الفسيولوجي: تلوين نبضي تركماني مضيء بالأطراف + هيدر تركوازي غامق فخم بنسب دائرية كاملة وأيقونة بيضاء منسجمة لليسار -->
          <section
            :class="alertsStore.justUpdated 
              ? 'border-[#0a3d48]/85 ring-1 ring-[#0a3d48]/15 shadow-[0_0_15px_rgba(10,61,72,0.22)]' 
              : 'border-slate-200 shadow-sm'"
            class="bg-white rounded-[2rem] border transition-all duration-500 overflow-hidden"
          >
            <!-- الترويسة الموحدة بالتركوازي الغامق والأيقونة البيضاء على الطرف المقابل دون إطارات عازلة -->
            <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none">
              <div class="min-w-0">
                <h2 class="text-sm font-extrabold text-white leading-tight">
                  المؤشرات الفسيولوجية
                </h2>
                
              </div>
              <Icon icon="solar:heart-pulse-bold" class="w-6 h-6 text-white shrink-0" />
            </div>

            <div class="p-5 sm:p-6">
              <!-- شريط التمرير الأفقي الذكي للموبايل والشبكة الخماسية للكمبيوتر -->
              <div class="flex overflow-x-auto gap-3 pb-3 snap-x xl:grid xl:grid-cols-5 xl:gap-3 xl:pb-0 custom-scrollbar scroll-smooth">

                <MetricCard
                  class="snap-start shrink-0 min-w-[145px] xl:min-w-0"
                  :title="$t('heart_rate')"
                  :value="
                    alertsStore.latestReadings.heart_rate
                      ? alertsStore.latestReadings.heart_rate.value + ' bpm'
                      : '-'
                  "
                  :status="hrStatus"
                  icon="heart"
                  :min-val="alertsStore.latestReadings.heart_rate?.min_val"
                  :max-val="alertsStore.latestReadings.heart_rate?.max_val"
                />

                <MetricCard
                  class="snap-start shrink-0 min-w-[145px] xl:min-w-0"
                  :title="$t('blood_pressure')"
                  :value="bpDisplay || '-'"
                  :status="bpStatus"
                  icon="bp"
                  :min-val="alertsStore.latestReadings.heart_rate?.min_val"
                  :max-val="alertsStore.latestReadings.heart_rate?.max_val"
                />

                <MetricCard
                  class="snap-start shrink-0 min-w-[145px] xl:min-w-0"
                  :title="$t('oxygen_saturation')"
                  :value="
                    alertsStore.latestReadings.oxygen
                      ? alertsStore.latestReadings.oxygen.value + '%'
                      : '-'
                  "
                  :status="o2Status"
                  icon="o2"
                  :min-val="alertsStore.latestReadings.oxygen?.min_val"
                  :max-val="alertsStore.latestReadings.oxygen?.max_val"
                />

                <MetricCard
                  class="snap-start shrink-0 min-w-[145px] xl:min-w-0"
                  :title="$t('respiratory_rate')"
                  :value="
                    alertsStore.latestReadings.respiratory_rate
                      ? alertsStore.latestReadings.respiratory_rate.value + ' rpm'
                      : '-'
                  "
                  :status="rrStatus"
                  icon="cloud"
                  :min-val="alertsStore.latestReadings.respiratory_rate?.min_val"
                  :max-val="alertsStore.latestReadings.respiratory_rate?.max_val"
                />

                <MetricCard
                  class="snap-start shrink-0 min-w-[145px] xl:min-w-0"
                  :title="$t('temperature')"
                  :value="
                    alertsStore.latestReadings.temperature
                      ? alertsStore.latestReadings.temperature.value + ' °C'
                      : '-'
                  "
                  :status="tempStatus"
                  icon="fire"
                  :min-val="alertsStore.latestReadings.temperature?.min_val"
                  :max-val="alertsStore.latestReadings.temperature?.max_val"
                />

              </div>
            </div>
          </section>


          <!-- ===================================================
               ACTIVITY + ENVIRONMENT
          ==================================================== -->
          <section class="grid grid-cols-1 lg:grid-cols-2 gap-5">

            <!-- Activity -->
            <!-- كارت الأب الحركي: تلوين نبضي تركماني مضيء بالأطراف + هيدر تركوازي غامق فخم بنسب دائرية كاملة وأيقونة بيضاء منسجمة لليسار -->
            <article
              :class="alertsStore.justUpdated 
                ? 'border-[#0a3d48]/85 ring-1 ring-[#0a3d48]/15 shadow-[0_0_15px_rgba(10,61,72,0.22)]' 
                : 'border-slate-200 shadow-sm'"
              class="bg-white rounded-[2rem] border flex flex-col transition-all duration-500 overflow-hidden"
            >
              <!-- الترويسة الموحدة بالتركوازي الغامق والأيقونة البيضاء على الطرف المقابل دون إطارات عازلة -->
              <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none">
                <div class="min-w-0">
                  <h3 class="text-sm font-extrabold text-white leading-tight">
                    النشاط الحركي
                  </h3>
                  <p class="text-[10px] text-teal-200/60 mt-0.5 font-medium">
                    الوضعية الحالية للمريض
                  </p>
                </div>
                <Icon icon="solar:running-2-bold" class="w-6 h-6 text-white shrink-0" />
              </div>

              <div class="p-5 sm:p-6 pt-5 flex items-center gap-5 flex-1 select-none">
                <div
                  class="w-16 h-16 shrink-0 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-700 flex items-center justify-center shadow-inner"
                >
                  <Icon :icon="activityIcon" class="w-9 h-9" />
                </div>

                <div class="min-w-0">
                  <span class="block text-[10px] text-slate-400 font-semibold">
                    الوضعية الحركية
                  </span>

                  <strong class="block text-xl font-extrabold text-slate-900 mt-1 truncate">
                    {{ activityLabel }}
                  </strong>

                  <span class="flex items-center gap-1.5 mt-2 text-[9px] text-slate-400 font-medium">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    يتم التحديث تلقائياً
                  </span>
                </div>
              </div>
            </article>


            <!-- Environment -->
            <!-- كارت الأب البيئي: تلوين نبضي تركماني مضيء بالأطراف + هيدر تركوازي غامق فخم بنسب دائرية كاملة وأيقونة بيضاء منسجمة لليسار -->
            <article
              :class="alertsStore.justUpdated 
                ? 'border-[#0a3d48]/85 ring-1 ring-[#0a3d48]/15 shadow-[0_0_15px_rgba(10,61,72,0.22)]' 
                : 'border-slate-200 shadow-sm'"
              class="bg-white rounded-[2rem] border flex flex-col transition-all duration-500 overflow-hidden"
            >
              <!-- الترويسة الموحدة بالتركوازي الغامق والأيقونة البيضاء على الطرف المقابل دون إطارات عازلة -->
              <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none">
                <div class="min-w-0">
                  <h3 class="text-sm font-extrabold text-white leading-tight">
                    البيئة المحيطة
                  </h3>
                  <p class="text-[10px] text-teal-200/60 mt-0.5 font-medium">
                    السياق البيئي للمريض
                  </p>
                </div>
                <Icon icon="solar:temperature-bold" class="w-6 h-6 text-white shrink-0" />
              </div>

              <div class="p-5 sm:p-6 pt-5 flex items-center gap-5 flex-1 select-none">
                <div
                  class="w-16 h-16 shrink-0 rounded-2xl bg-cyan-50 border border-cyan-100 text-cyan-700 flex items-center justify-center shadow-inner"
                >
                  <Icon icon="solar:temperature-bold" class="w-9 h-9" />
                </div>

                <div class="min-w-0">
                  <span class="block text-[10px] text-slate-400 font-semibold">
                    درجة حرارة الغرفة
                  </span>

                  <strong class="block text-xl font-extrabold text-slate-900 mt-1 truncate font-mono">
                    {{
                      alertsStore.latestReadings.room_temperature
                        ? alertsStore.latestReadings.room_temperature.value + ' °C'
                        : '-'
                    }}
                  </strong>

                  <span class="flex items-center gap-1.5 mt-2 text-[9px] text-slate-400 font-medium">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    البيئة مستقرة
                  </span>
                </div>
              </div>
            </article>

          </section>


          <!-- ===================================================
               ANALYTICS
          ==================================================== -->
          <section class="grid grid-cols-1 xl:grid-cols-3 gap-5 items-stretch">

            <!-- Trend Chart -->
            <!-- كارت المخططات: تلوين نبضي تركماني مضيء بالأطراف + هيدر تركوازي غامق فخم بنسب دائرية كاملة وأيقونة بيضاء منسجمة لليسار -->
            <div
              :class="alertsStore.justUpdated 
                ? 'border-[#0a3d48]/85 ring-1 ring-[#0a3d48]/15 shadow-[0_0_15px_rgba(10,61,72,0.22)]' 
                : 'border-slate-200 shadow-sm'"
              class="xl:col-span-2 min-w-0 bg-white rounded-[2rem] border flex flex-col transition-all duration-500 overflow-hidden"
            >
              <!-- ترويسة المخططات بالتركوازي الغامق والأيقونة البيضاء على اليسار المقابل بجانب مفاتيح الرسم الشرياني -->
              <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none">
                <div class="min-w-0">
                  <h2 class="text-sm font-extrabold text-white leading-tight">
                    الاتجاهات الفسيولوجية
                  </h2>
                  <p class="text-[10px] text-teal-200/60 mt-0.5 font-medium">
                    تطور المؤشرات الصحية بمرور الوقت
                  </p>
                </div>

                <div class="flex items-center gap-4">
                  <div class="flex items-center gap-3 text-[9px] font-bold shrink-0">
                    <span class="flex items-center gap-1.5 text-rose-300">
                      <span class="w-3 h-0.5 rounded-full bg-rose-500"></span>
                      معدل ضربات القلب
                    </span>
                    <span class="flex items-center gap-1.5 text-sky-300">
                      <span class="w-3 h-0.5 rounded-full bg-sky-400"></span>
                      ضغط الدم
                    </span>
                  </div>
                  <Icon icon="solar:chart-2-bold" class="w-6 h-6 text-white shrink-0" />
                </div>
              </div>

              <div class="p-5 sm:p-6 flex-1 min-h-0">
                <TrendChart
                  :readings="alertsStore.readings"
                  :latest="alertsStore.latestReadings"
                />
              </div>
            </div>


            <!-- AI Insight -->
            <div class="min-w-0 flex flex-col">
              <InsightPanel
                :insight="alertsStore.latestInsight"
              />
            </div>

          </section>


          <!-- ===================================================
               SENSOR CONTROL (حراً بلا حدود بيضاء أو حشر بصري أو عبارات مكررة)
          ==================================================== -->
          <section class="w-full">
            <SensorControl
              :patient-id="store.currentPatient.id"
            />
          </section>

        </div>
      </main>
    </div>
  </div>
</template>


<script setup>
import { ref, computed } from 'vue'
import { usePatientStore } from '../stores/patient'
import { useAlertsStore } from '../stores/alerts'

import MetricCard from '../components/MetricCard.vue'
import TrendChart from '../components/TrendChart.vue'
import SensorControl from '../components/SensorControl.vue'
import InsightPanel from '../components/insightPanel.vue'
import PatientHeader from '../components/PatientHeader.vue'

import { Icon } from '@iconify/vue'


const store = usePatientStore()
const alertsStore = useAlertsStore()


const selectedRange = ref('1h')
const showCustomRange = ref(false)


const selectChartRange = (range) => {
  selectedRange.value = range
  showCustomRange.value = range === 'custom'

  if (range !== 'custom' && store.currentPatient?.id) {
    alertsStore.readings = []
    alertsStore.fetchChartData(
      store.currentPatient.id,
      range
    )
  }
}


const activityLabel = computed(() => {
  const val = alertsStore.latestReadings.activity_level?.value

  if (val === undefined || val === null) {
    return 'غير معروف'
  }

  const num = Number(val)

  if (num === 0) return 'نوم / سكون'
  if (num === 1) return 'جلوس'
  if (num === 2) return 'مشي'
  if (num === 3) return 'جري'

  return 'غير معروف'
})


const activityIcon = computed(() => {
  const val = alertsStore.latestReadings.activity_level?.value

  if (val === undefined || val === null) {
    return 'solar:user-bold'
  }

  const num = Number(val)

  if (num === 0) return 'solar:sleeping-bold'
  if (num === 1) return 'solar:armchair-bold'
  if (num === 2) return 'solar:walking-round-bold'
  if (num === 3) return 'solar:running-round-bold'

  return 'solar:user-bold'
})


const hrStatus = computed(() =>
  alertsStore.latestReadings.heart_rate?.status || 'Good'
)

const o2Status = computed(() =>
  alertsStore.latestReadings.oxygen?.status || 'Good'
)

const activityStatus = computed(() => 'Good')

const tempStatus = computed(() =>
  alertsStore.latestReadings.temperature?.status || 'Good'
)

const rrStatus = computed(() =>
  alertsStore.latestReadings.respiratory_rate?.status || 'Good'
)

const roomTempStatus = computed(() =>
  alertsStore.latestReadings.room_temperature?.status || 'Good'
)


const bpStatus = computed(() => {
  const sysS =
    alertsStore.latestReadings.bp_sys?.status || 'Good'

  const diaS =
    alertsStore.latestReadings.bp_dia?.status || 'Good'

  return (
    sysS === 'Caution' ||
    diaS === 'Caution'
  )
    ? 'Caution'
    : 'Good'
})


const bpDisplay = computed(() => {
  if (
    alertsStore.latestReadings.bp_sys?.value &&
    alertsStore.latestReadings.bp_dia?.value
  ) {
    return `${alertsStore.latestReadings.bp_sys.value}/${alertsStore.latestReadings.bp_dia.value}`
  }

  return null
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
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