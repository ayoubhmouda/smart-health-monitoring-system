<!-- dashboard.vue -->
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
        <!-- لمسة إضاءة تراكوازية متدرجة بالخلفية -->
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
    <!-- h-full بدل min-h-screen، عشان يرث الارتفاع الثابت من الجذر ويصير main قابل للتمرير الداخلي فعلياً -->
    <div v-else class="flex-1 flex flex-col min-w-0 h-full relative">

      <!-- main هو المنطقة الوحيدة القابلة للتمرير، وتحتوي على الهيدر (يتحرك عادي) وبطاقة المريض (تلتصق بالأعلى) -->
      <main class="flex-1 min-h-0 overflow-y-auto">

        <!-- 1. الترويسة العليا — عنصر عادي، يتحرك مع التمرير ويختفي مثل أي عنصر -->
        <header class="px-8 pt-6 pb-2 select-none flex justify-between items-center">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="w-2.5 h-2.5 rounded-full bg-teal-600 shadow-sm shadow-teal-500/50 animate-pulse"></span>
              <h1 class="text-xl font-black text-teal-950 tracking-tight">لوحة تحكم المراقبة المباشرة <span class="text-teal-700/60 font-semibold text-sm">(Live Patient Dashboard)</span></h1>
            </div>
            <p class="text-xs text-slate-400 font-medium mr-4">مراقبة حية فورية ومستمرة للعلامات الفسيولوجية والسياق الحركي والبيئي بالثانية (Real-time monitoring)</p>
          </div>
        </header>

        <!-- 2. بطاقة تعريف المريض — sticky داخل المكوّن نفسه، فتلتصق بأعلى main بعد ما الهيدر يمر ويختفي -->
        <div class="sticky top-0 z-20 px-8 py-2">
          <PatientHeader 
            :patient="store.currentPatient"
            :is-ws-connected="alertsStore.isWsConnected"
            :just-updated="alertsStore.justUpdated"
            :countdown="alertsStore.countdown"
            :last-updated-time="alertsStore.lastUpdatedTime"
          />
        </div>

        <!-- شبكة العناصر الحيوية والمخططات والتحليلات -->
        <div class="px-8 py-4 space-y-6 w-full">

        <!-- شبكة المؤشرات الحيوية الرئيسيّة -->
        <section class="grid grid-cols-1 xl:grid-cols-12 gap-6 w-full items-stretch">
          
          <!-- الحاوية أ: المؤشرات الفسيولوجية الأساسية (Soft UI Card) -->
          <div class="xl:col-span-8 bg-white/80 backdrop-blur-xl border border-white/90 rounded-[2rem] p-6 shadow-xl shadow-teal-950/[0.03] flex flex-col justify-between gap-4 hover:shadow-2xl hover:shadow-teal-900/[0.06] transition-all duration-300">
            <div class="flex items-center justify-between border-b border-slate-100/80 pb-3">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-teal-500"></div>
                <h4 class="text-xs font-black text-teal-900 tracking-wider uppercase">المؤشرات الفسيولوجية الأساسية</h4>
              </div>
              <span class="text-[10px] font-bold px-2.5 py-1 rounded-full bg-teal-50 text-teal-700 border border-teal-200/50">تحديث مباشر</span>
            </div>
            
            <div class="flex overflow-x-auto pb-2 lg:pb-0 lg:grid lg:grid-cols-5 gap-3.5 snap-x custom-scrollbar">
              <!-- 1. نبضات القلب (البطاقة الكلاسيكية) -->
              <MetricCard :title="$t('heart_rate')" :value="alertsStore.latestReadings.heart_rate ? alertsStore.latestReadings.heart_rate.value + ' bpm' : '-'" :status="hrStatus" icon="heart" />
              <!-- 2. ضغط الدم الشرياني -->
              <MetricCard :title="$t('blood_pressure')" :value="bpDisplay || '-'" :status="bpStatus" icon="bp" />
              <!-- 3. تشبع الأكسجين -->
              <MetricCard :title="$t('oxygen_saturation')" :value="alertsStore.latestReadings.oxygen ? alertsStore.latestReadings.oxygen.value + '%' : '-'" :status="o2Status" icon="o2" />
              <!-- 4. معدل التنفس -->
              <MetricCard :title="$t('respiratory_rate')" :value="alertsStore.latestReadings.respiratory_rate ? alertsStore.latestReadings.respiratory_rate.value + ' rpm' : '-'" :status="rrStatus" icon="cloud" />
              <!-- 5. درجة حرارة الجسم -->
              <MetricCard :title="$t('temperature')" :value="alertsStore.latestReadings.temperature ? alertsStore.latestReadings.temperature.value + ' °C' : '-'" :status="tempStatus" icon="fire" />
            </div>
          </div>

          <!-- دمج حاوية النشاط والبيئة -->
          <div class="grid grid-cols-2 gap-4 xl:col-span-4 xl:grid-cols-2 xl:gap-5 items-stretch">
            
            <!-- الحاوية ب: النشاط الحركي (البطاقة الكلاسيكية) -->
            <div class="bg-white/80 backdrop-blur-xl border border-white/90 rounded-[2rem] p-5 shadow-xl shadow-teal-950/[0.03] flex flex-col justify-between gap-3 hover:shadow-2xl hover:shadow-teal-900/[0.06] transition-all duration-300">
              <div class="flex items-center gap-2 border-b border-slate-100/80 pb-2.5">
                <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
                <h4 class="text-xs font-black text-teal-900 tracking-wider uppercase">النشاط الحركي</h4>
              </div>
              <MetricCard :title="$t('activity')" :value="alertsStore.latestReadings.activity_level ? String(alertsStore.latestReadings.activity_level.value) : '-'" :status="activityStatus" icon="bolt" class="w-full" />
            </div>

            <!-- الحاوية ج: السياق البيئي -->
            <div class="bg-white/80 backdrop-blur-xl border border-white/90 rounded-[2rem] p-5 shadow-xl shadow-teal-950/[0.03] flex flex-col justify-between gap-3 hover:shadow-2xl hover:shadow-teal-900/[0.06] transition-all duration-300">
              <div class="flex items-center gap-2 border-b border-slate-100/80 pb-2.5">
                <div class="w-2 h-2 rounded-full bg-cyan-500"></div>
                <h4 class="text-xs font-black text-teal-900 tracking-wider uppercase">السياق البيئي</h4>
              </div>
              <MetricCard :title="$t('room_temperature')" :value="alertsStore.latestReadings.room_temperature ? alertsStore.latestReadings.room_temperature.value + ' °C' : '-'" :status="roomTempStatus" icon="home" class="w-full" />
            </div>

          </div>

        </section>

        <!-- المخططات والتحليلات الطبية -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start w-full">
          
          <!-- مخطط الاتجاهات الطبية العصري -->
          <div class="lg:col-span-2 order-2 lg:order-1 bg-white/80 backdrop-blur-xl rounded-[2rem] border border-white/90 p-6 shadow-xl shadow-teal-950/[0.03] hover:shadow-2xl hover:shadow-teal-900/[0.06] transition-all duration-300">
            <div class="flex items-center justify-between mb-5 border-b border-slate-100 pb-3.5">
              <div class="flex items-center gap-2">
                <div class="w-2.5 h-2.5 rounded-full bg-teal-600"></div>
                <h3 class="text-xs font-black text-teal-950 tracking-wide uppercase">مخططات الاتجاه الفسيولوجي المتقدمة</h3>
              </div>
              <div class="flex items-center gap-4 text-[11px] font-bold">
                <span class="flex items-center gap-2 bg-rose-50 text-rose-700 px-2.5 py-1 rounded-full border border-rose-100">
                  <span class="w-2 h-2 bg-rose-500 rounded-full shadow-sm"></span>نبضات القلب
                </span>
                <span class="flex items-center gap-2 bg-sky-50 text-sky-700 px-2.5 py-1 rounded-full border border-sky-100">
                  <span class="w-2 h-2 bg-sky-500 rounded-full shadow-sm"></span>الضغط الانقباضي
                </span>
              </div>
            </div>
            <TrendChart :readings="alertsStore.readings" :latest="alertsStore.latestReadings" />
          </div>

          <!-- مكون التنبؤ المستقل للذكاء الاصطناعي -->
          <InsightPanel class="lg:col-span-1 order-1 lg:order-2" :insight="alertsStore.latestInsight" />

        </div>

        <!-- لوحة التحكم المركزية بالسيناريوهات الطبية - بدون غلاف أبيض -->
        <section class="w-full">
          <SensorControl :patient-id="store.currentPatient.id" />
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

const store = usePatientStore()
const alertsStore = useAlertsStore()

const selectedRange = ref('1h')
const showCustomRange = ref(false)

const selectChartRange = (range) => {
  selectedRange.value = range
  showCustomRange.value = range === 'custom'
  if (range !== 'custom' && store.currentPatient?.id) {
    alertsStore.readings = []
    alertsStore.fetchChartData(store.currentPatient.id, range)
  }
}

// تلوين البطاقات الفوري بقراءة الـ status من الـ AlertsStore المشترك مباشرة
const hrStatus = computed(() => alertsStore.latestReadings.heart_rate?.status || 'Good')
const o2Status = computed(() => alertsStore.latestReadings.oxygen?.status || 'Good')
const activityStatus = computed(() => 'Good')
const tempStatus = computed(() => alertsStore.latestReadings.temperature?.status || 'Good')
const rrStatus = computed(() => alertsStore.latestReadings.respiratory_rate?.status || 'Good')
const roomTempStatus = computed(() => alertsStore.latestReadings.room_temperature?.status || 'Good')

const bpStatus = computed(() => {
  const sysS = alertsStore.latestReadings.bp_sys?.status || 'Good'
  const diaS = alertsStore.latestReadings.bp_dia?.status || 'Good'
  return (sysS === 'Caution' || diaS === 'Caution') ? 'Caution' : 'Good'
})

const bpDisplay = computed(() => {
  if (alertsStore.latestReadings.bp_sys?.value && alertsStore.latestReadings.bp_dia?.value) {
    return `${alertsStore.latestReadings.bp_sys.value}/${alertsStore.latestReadings.bp_dia.value}`
  }
  return null
})
</script>