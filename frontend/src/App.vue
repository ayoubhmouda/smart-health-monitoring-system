<!-- frontend/src/App.vue -->
<template>
  <div v-if="isAuthPage" class="min-h-screen bg-gray-100">
    <router-view />
  </div>

  <div v-else class="h-screen flex flex-col bg-slate-100 overflow-hidden relative">
    <Navbar />
    
    <div class="flex flex-1 overflow-hidden pt-0 relative">
      <Sidebar />
      
      <main class="flex-1 min-w-0 overflow-y-auto bg-[#F0F6F5] relative">
        <!-- 🔴 شريط الطوارئ العائم الموحد -->
        <transition name="slide-fade">
          <div 
            v-if="activeEmergencyAlert && alertsStore.showEmergencyBanner" 
            :class="['fixed top-6 left-6 z-[999] w-[360px] sm:w-[380px] border rounded-3xl shadow-2xl p-5 flex flex-col gap-4 animate-[pulse_3s_ease-in-out_infinite] transition-colors duration-300', alertClasses.card]"
          >
            <!-- الهيدر: شارة التنبيه وزر الإغلاق -->
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-2.5">
                <span class="flex h-3.5 w-3.5 relative flex-shrink-0">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 duration-1000" :class="alertClasses.beaconPing"></span>
                  <span class="relative inline-flex rounded-full h-3.5 w-3.5 shadow-inner" :class="alertClasses.beaconDot"></span>
                </span>
                <span class="text-[9px] font-black px-2.5 py-0.5 rounded-full border uppercase tracking-wider" :class="alertClasses.badge">
                  {{ alertSourceLabel }} ({{ severityLabel }})
                </span>
              </div>
              <button @click="dismissEmergencyAlert" class="text-slate-400 hover:text-slate-600 transition-colors p-1.5 rounded-xl hover:bg-slate-100 flex-shrink-0 cursor-pointer">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- بيانات المريض المتأثر بالخطر -->
            <div class="bg-black/5 rounded-2xl p-3.5 border border-black/10 flex flex-col gap-1.5 text-[11px] font-semibold select-none">
              <div class="flex justify-between border-b border-black/10 pb-1.5">
                <span>المريض المتأثر: <strong class="text-xs font-black">{{ alertPatientDetails?.full_name || 'جاري الفحص...' }}</strong></span>
                <span>ID: <strong class="font-bold">#{{ alertPatientDetails?.id || targetPatientId }}</strong></span>
              </div>
              <div class="flex justify-between pt-1">
                <span>العمر: <strong class="font-bold">{{ alertPatientDetails?.age || '--' }} سنة</strong></span>
                <span>النوع: <strong class="font-bold">{{ alertPatientDetails?.element_type || 'مريض' }}</strong></span>
              </div>
            </div>

            <!-- تفاصيل الإنذار -->
            <div class="flex flex-col gap-1">
              <h4 class="font-black text-xs sm:text-sm">
                {{ activeEmergencyAlert.rule_name ? `تجاوز للبروتوكول: [${activeEmergencyAlert.rule_name}]` : 'تجاوز لشبكة الأمان الصارمة!' }}
              </h4>
              <p class="text-xs leading-relaxed font-bold animate-pulse" :class="alertClasses.descText">
                {{ activeEmergencyAlert.rule_name ? 'تم رصد نشاط فسيولوجي يتطابق مع شروط القاعدة السريرية للمريض.' : 'تم رصد هبوط حاد في مستويات الأكسجين أو التنفس للمريض المعروض أعلاه.' }}
              </p>
            </div>

            <!-- الإجراء العلاجي المقترح -->
            <div class="bg-black/5 text-slate-800 rounded-xl p-3 text-xs font-bold border border-black/10">
              <div class="text-[9px] text-slate-500 font-black uppercase tracking-wider mb-0.5">الإجراء السريري المقترح</div>
              {{ activeEmergencyAlert.action_template || 'يرجى التوجه لمعاينة المريض سريرياً فوراً' }}
            </div>

            <!-- زر الانتقال السريع للمريض المهدد -->
            <button 
              @click="viewAffectedPatient"
              class="w-full text-white rounded-xl py-2.5 px-3 text-center text-[11px] font-black shadow-md transition-colors cursor-pointer active:scale-[0.98]"
              :class="alertClasses.button"
            >
              ⚠️ اضغط هنا لمعاينة المريض سريرياً فوراً
            </button>
          </div>
        </transition>

        <router-view />
      </main>
    </div>

    <!-- موبايل Overlay -->
    <transition name="fade">
      <div
        v-if="patientStore.isSidebarOpen"
        @click="patientStore.isSidebarOpen = false"
        class="lg:hidden fixed inset-0 z-30 bg-black/60 backdrop-blur-sm"
      />
    </transition>
  </div>
</template>

<script setup>
import { computed, watch, watchEffect, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Sidebar from './components/sidebar.vue'          
import Navbar from './components/Navbar.vue'             
import { useDoctorStore } from './stores/doctor'
import { usePatientStore } from './stores/patient'        
import { useAlertsStore } from './stores/alerts'          

const route = useRoute()
const router = useRouter()
const doctorStore = useDoctorStore()
const patientStore = usePatientStore()              
const alertsStore = useAlertsStore()                

const { locale } = useI18n()
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')

watch(() => patientStore.currentPatient?.id, (newId) => {
  if (newId) {
    alertsStore.showEmergencyBanner = true
    alertsStore.fetchData(newId)
    alertsStore.fetchChartData(newId)
    alertsStore.startCountdown(newId)
  }
}, { immediate: true })

const targetPatientId = computed(() => {
  const alert = alertsStore.latestThresholdInsight
  if (!alert) return null
  const alertPatient = alert.monitored_element
  return alertPatient && typeof alertPatient === 'object' ? alertPatient.id : alertPatient
})

const alertPatientDetails = computed(() => {
  const pId = targetPatientId.value
  if (!pId) return null
  return patientStore.patients?.find(p => Number(p.id) === Number(pId)) || null
})

const activeEmergencyAlert = computed(() => {
  if (!alertsStore.latestThresholdInsight) return null
  const pId = targetPatientId.value
  if (!pId || !alertsStore.patientAlertStates[pId]) return null

  const severityFormatted = String(alertsStore.latestThresholdInsight.severity).toUpperCase()
  if (!['CRITICAL', 'HIGH'].includes(severityFormatted)) return null

  return alertsStore.latestThresholdInsight
})

const alertSeverity = computed(() => {
  if (!activeEmergencyAlert.value) return 'MEDIUM'
  return String(activeEmergencyAlert.value.severity).toUpperCase()
})

const severityLabel = computed(() => {
  switch (alertSeverity.value) {
    case 'CRITICAL': return 'حالة حرجة'
    case 'HIGH': return 'خطورة عالية'
    default: return 'خطورة متوسطة'
  }
})

const alertClasses = computed(() => {
  switch (alertSeverity.value) {
    case 'CRITICAL':
      return {
        card: 'bg-rose-50/95 border-rose-300 border-r-rose-600 text-rose-950',
        badge: 'bg-rose-100 text-rose-800 border-rose-300',
        beaconPing: 'bg-rose-400',
        beaconDot: 'bg-rose-600',
        descText: 'text-rose-900',
        button: 'bg-rose-600 hover:bg-rose-700 shadow-rose-600/10'
      }
    default:
      return {
        card: 'bg-amber-50/95 border-amber-300 border-r-amber-600 text-amber-950',
        badge: 'bg-amber-100 text-amber-800 border-amber-300',
        beaconPing: 'bg-amber-400',
        beaconDot: 'bg-amber-600',
        descText: 'text-amber-900',
        button: 'bg-amber-600 hover:bg-amber-700 shadow-amber-600/10'
      }
  }
})

// مسمى شارة نوع التنبيه ديناميكياً بناءً على مصدر وقناة التنبيه
const alertSourceLabel = computed(() => {
  const alert = activeEmergencyAlert.value
  if (!alert) return ''
  const src = alert.source?.toLowerCase()
  if (src === 'threshold') return 'إنذار شبكة الأمان'
  
  // 🟢 التمييز البرمجي والسريري الدقيق بين البروتوكول العام وقاعدة الطبيب
  if (src === 'rules' || src === 'rule') {
    return alert.is_global_rule ? 'بروتوكول عام (المدير)' : 'قاعدة مخصصة للمريض'
  }
  return 'قاعدة مخصصة للمريض'
})

const viewAffectedPatient = () => {
  const patient = alertPatientDetails.value
  if (patient) {
    patientStore.selectPatient(patient)
    alertsStore.showEmergencyBanner = true
    router.push('/dashboard')
  }
}

const dismissEmergencyAlert = () => {
  alertsStore.showEmergencyBanner = false
}

watch(() => alertsStore.latestThresholdInsight?.id, () => {
  alertsStore.showEmergencyBanner = true
})

onMounted(async () => {
  if (localStorage.getItem('token')) {
    try {
      await doctorStore.fetchProfile()
    } catch (e) {
      console.error('فشل استعادة البروفايل:', e)
    }
  }
})

watchEffect(() => {
  document.documentElement.lang = locale.value
  document.documentElement.dir = locale.value === 'ar' ? 'rtl' : 'ltr'
})
</script>

<style scoped>
.slide-fade-enter-active { transition: all 0.4s ease-out; }
.slide-fade-leave-active { transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(-20px); opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>