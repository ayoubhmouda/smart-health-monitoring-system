<!-- src/views/Alerts.vue -->
<template>
  <div class="flex-1 flex flex-col h-screen max-h-screen bg-[#F0F6F5]" dir="rtl">
    
    <!-- الترويسة العلوية لمركز الإشعارات -->
    <div class="px-6 pt-6 pb-4 flex-shrink-0 select-none flex items-center justify-between border-b border-slate-200/50 bg-white shadow-xs">
      <div>
        <h1 class="text-lg font-black text-slate-800 tracking-tight flex items-center gap-2">
          <svg class="w-5 h-5 text-rose-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span>مركز الإشعارات والتنبيهات الطبية (Caregiver Alert Hub)</span>
        </h1>
        <p class="text-xs text-slate-400 mt-0.5 font-medium">متابعة ومراجعة فروع الإنذارات الطارئة المستنبطة من شبكة الأمان، البروتوكولات، وقواعد المرضى المخصصة.</p>
      </div>

      <!-- مؤشر العداد المباشر الإجمالي العام في السوكيت -->
      <div v-if="alertsStore.activeAlertsCount > 0" class="flex items-center gap-2 bg-rose-50 border border-rose-200 rounded-xl py-1.5 px-3">
        <span class="w-2 h-2 rounded-full bg-rose-600 animate-ping"></span>
        <span class="text-xs font-black text-rose-800">يوجد {{ alertsStore.activeAlertsCount }} إنذار سريري نشط حالياً</span>
      </div>
    </div>

    <!-- شريط فلاتر التصفية المنسدلة الثلاثية الموحدة (Dropdowns Filter Bar) -->
    <div class="px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 flex-shrink-0 border-b border-slate-200/40 bg-white shadow-xs select-none">
      
      <div class="text-xs font-bold text-slate-700">
        تصفية الإنذارات السريرية النشطة والتاريخية:
      </div>

      <!-- القوائم المنسدلة الثلاث الموحدة للتصفية الدقيقة والسريرية المتقدمة -->
      <div class="flex flex-wrap items-center gap-4">
        
        <!-- 1. قائمة تصفية نوع ومصدر الإنذار المحدثة -->
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-wider">نوع الإنذار:</span>
          <select 
            v-model="selectedTab" 
            @change="onFilterChange"
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl py-2 px-3 focus:outline-none focus:ring-1 focus:ring-[#0d9488] cursor-pointer"
          >
            <option value="all">كل أنواع التنبيهات</option>
            <option value="threshold">شبكة الأمان (النظام)</option>
            <option value="global">البروتوكولات السريرية (المدير)</option>
            <option value="patient_rule">قواعد الطبيب الخاصة</option>
          </select>
        </div>

        <!-- 2. تصفية المرضى -->
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-wider">تصفية المريض:</span>
          <select 
            v-model="selectedPatientId" 
            @change="onFilterChange"
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl py-2 px-3 focus:outline-none focus:ring-1 focus:ring-[#0d9488] cursor-pointer"
          >
            <option value="all">كل المرضى في العنبر</option>
            <option v-for="p in patientStore.patients" :key="p.id" :value="p.id">
              {{ p.full_name }} (#{{ p.id }})
            </option>
          </select>
        </div>

        <!-- 3. تصفية مستوى الخطورة -->
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-wider">تصفية الخطورة:</span>
          <select 
            v-model="selectedSeverity" 
            @change="onFilterChange"
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl py-2 px-3 focus:outline-none focus:ring-1 focus:ring-[#0d9488] cursor-pointer"
          >
            <option value="all">كل مستويات الخطورة</option>
            <option value="CRITICAL">حالة حرجة (CRITICAL)</option>
            <option value="HIGH">خطورة عالية (HIGH)</option>
            <option value="MEDIUM">خطورة متوسطة (MEDIUM)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- شريط معلومات إحصائي يوضح إجمالي التنبيهات المصفاة في القسم المفتوح -->
    <div class="px-6 py-3 flex-shrink-0 flex items-center justify-between text-[11px] font-black text-slate-400 select-none uppercase tracking-wider">
      <div class="flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
        <span>إجمالي التنبيهات المعروضة في هذا القسم: ({{ filteredAlerts.length }}) تنبيه تاريخي</span>
      </div>
      <div class="flex items-center gap-1">
        <span>الترتيب:</span>
        <span class="text-[#0d9488]">من الأحدث إلى الأقدم</span>
      </div>
    </div>

    <!-- جسد عرض قائمة التنبيهات مع شريط تصفح رأسي مخصص -->
    <main class="flex-1 px-6 pb-6 overflow-y-auto w-full custom-scrollbar pr-1">
      
      <!-- مؤشر جاري التحميل -->
      <div v-if="loading && alertsHistory.length === 0" class="py-20 text-center flex flex-col items-center justify-center gap-3">
        <div class="w-8 h-8 border-3 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        <span class="text-xs font-bold text-slate-400">جاري فحص وتصفية سجل الإشعارات الطبية...</span>
      </div>

      <!-- عرض القائمة المصفاة والمنظمة تنازلياً للإنذارات -->
      <div v-else-if="filteredAlerts.length > 0">
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <div 
            v-for="alert in filteredAlerts" 
            :key="alert.id"
            :class="[
              isCritical(alert) 
                ? 'border-r-rose-600 bg-rose-50/20 hover:border-rose-300 shadow-rose-100/30' 
                : 'border-r-amber-500 bg-amber-50/20 hover:border-amber-300 shadow-amber-100/30'
            ]"
            class="bg-white border border-slate-200/90 border-r-4 rounded-2xl p-5 shadow-sm transition-all duration-200 flex flex-col justify-between gap-4"
          >
            <!-- الهيدر الداخلي للكارت: المصدر وتاريخ التنبيه -->
            <div class="flex items-center justify-between">
              <span :class="getSourceBadgeClass(alert)" class="text-[9px] font-black px-2 py-0.5 rounded-full border">
                {{ getSourceLabel(alert) }}
              </span>
              <span class="text-[10px] text-slate-400 font-mono font-semibold">
                {{ formatDateTime(alert.detected_at) }}
              </span>
            </div>

            <!-- تفاصيل ديموغرافية المريض المتأثر بالحدث -->
            <div class="bg-slate-50 border border-slate-100 rounded-xl p-3 flex flex-col gap-1 text-[11px] text-slate-500 font-bold select-none">
              <div class="flex justify-between">
                <span>المريض: <strong class="text-slate-800 text-xs font-black">{{ alert.patient_name || 'غير معروف' }}</strong></span>
                <span>ID: <strong>#{{ alert.monitored_element_id || alert.monitored_element }}</strong></span>
              </div>
              <div class="flex justify-between pt-0.5">
                <span>العمر: <strong>{{ alert.patient_age || 'غير حدد' }} سنة</strong></span>
                <span>الجنس: <strong>{{ alert.patient_gender === 'M' || alert.patient_gender === 'ذكر' ? 'ذكر' : 'أنثى' }}</strong></span>
              </div>
            </div>

            <!-- رسالة التحذير السريرية -->
            <div class="flex flex-col gap-1">
              <h4 class="text-slate-800 font-black text-sm flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-rose-500" v-if="isCritical(alert)"></span>
                {{ alert.insight_type_display || 'مؤشر فسيولوجي غير طبيعي' }}
              </h4>
              <p class="text-slate-500 text-xs leading-relaxed font-bold">
                {{ alert.message || 'تم رصد تجاوز للحدود الآمنة لعلامات المريض الفسيولوجية.' }}
              </p>
            </div>

            <!-- الإجراء العلاجي المقترح من الباك إند (Action Template) -->
            <div v-if="alert.action_template" class="bg-teal-50 border border-teal-100 rounded-xl p-3 text-xs text-teal-800 font-bold flex items-start gap-2">
              <span class="text-base">📋</span>
              <div>
                <div class="text-[10px] text-teal-600 font-black uppercase tracking-wider mb-0.5">الإجراء السريري المقترح</div>
                {{ alert.action_template }}
              </div>
            </div>

            <!-- الإجراءات الطبية المتاحة للمعاينة والتصفية -->
            <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
              <button 
                @click="viewPatientDashboard(alert)"
                class="flex items-center justify-center gap-1 bg-[#0a2540] hover:bg-[#113254] text-white text-xs font-black py-2 rounded-xl transition-all shadow-sm shadow-slate-900/10 cursor-pointer active:scale-95"
              >
                <span>معاينة المريض</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              </button>
              
              <button 
                @click="resolveAlertLocally(alert.id)"
                class="flex items-center justify-center gap-1 bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 hover:border-slate-300 text-xs font-bold py-2 rounded-xl transition-all cursor-pointer active:scale-95"
              >
                <span>تم الحل والمعاينة</span>
              </button>
            </div>
          </div>
        </div>

        <!-- زر تحميل المزيد من التنبيهات التاريخية (50 تنبيهاً أخرى) -->
        <div v-if="hasMore" class="flex justify-center mt-8 select-none">
          <button 
            @click="loadMore"
            :disabled="loading"
            class="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 hover:border-slate-300 font-black text-xs px-6 py-3 rounded-2xl shadow-sm transition-all cursor-pointer active:scale-95 disabled:opacity-50"
          >
            <span v-if="loading" class="w-3.5 h-3.5 border-2 border-slate-600 border-t-transparent rounded-full animate-spin"></span>
            <span v-else>🔄 عرض 50 تنبيهاً أخرى</span>
          </button>
        </div>
      </div>

      <!-- لوحة في حالة عدم وجود قراءات مصفاة -->
      <div v-else class="py-24 text-center flex flex-col items-center justify-center select-none">
        <span class="text-5xl mb-4">💚</span>
        <h3 class="text-sm font-black text-slate-800 mb-1">لا توجد تنبيهات طارئة نشطة</h3>
        <p class="text-xs text-slate-400 max-w-xs leading-relaxed font-semibold">كافة المؤشرات الحيوية لجميع الحالات المراقبة تحت السيطرة السريرية التامة لشبكة الأمان.</p>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAlertsStore } from '../stores/alerts'
import { usePatientStore } from '../stores/patient'
import api from '../api'

const router = useRouter()
const alertsStore = useAlertsStore()
const patientStore = usePatientStore()

const loading = ref(false)
const selectedTab = ref('all')         // 'all' | 'threshold' | 'global' | 'patient_rule'
const selectedPatientId = ref('all')   // 'all' | patient_id
const selectedSeverity = ref('all')    // 'all' | 'CRITICAL' | 'HIGH' | 'MEDIUM'

const alertsHistory = ref([])
const limit = ref(50)
const offset = ref(0)
const hasMore = ref(true)

// 🟢 جلب البيانات المفلترة من قاعدة البيانات عبر الـ REST API المطور
// 🟢 جلب البيانات المفلترة من قاعدة البيانات عبر الـ REST API المطور مع تتبع دقيق للأخطاء
const fetchAlertsHistory = async (append = false) => {
  if (!append) {
    loading.value = true
    offset.value = 0
    alertsHistory.value = []
  }
  
  try {
    const params = {
      ordering: '-detected_at',
      limit: limit.value,
      offset: offset.value
    }

    // 1. فلترة المريض
    if (selectedPatientId.value !== 'all') {
      params.monitored_element = selectedPatientId.value
    }

    // 2. فلترة مستوى الخطورة
    if (selectedSeverity.value !== 'all') {
      params.severity = selectedSeverity.value
    }

    // 3. فلترة نوع ومصدر الإنذار
    if (selectedTab.value !== 'all') {
      params.alert_type = selectedTab.value
    }

    // طباعة البارامترات المرسلة للتفتيش
    console.log("📤 [Alerts.vue] إرسال بارامترات الفلترة للسيرفر:", params)

    const res = await api.get('/api/insights/', { params })
    
    // 🟢 طباعة الرد الفعلي الراجع من قاعدة البيانات لتفتيش المحتوى
    console.log("📥 [Alerts.vue] الرد الراجع من السيرفر بنجاح:", res.data)

    const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
    
    // التحقق من وجود المزيد من التنبيهات
    const nextUrl = res.data?.next || null
    hasMore.value = nextUrl !== null
    
    // استبعاد تنبؤات الذكاء الاصطناعي (ML) من شاشة التنبيهات الطبية
    const filteredData = data.filter(item => 
      item.source?.toLowerCase() !== 'ml' && 
      item.source?.toLowerCase() !== 'ml_model'
    )

    // دمج البيانات الفوقية للمريض (Demographics)
    const mapped = filteredData.map(item => {
      const patientId = item.monitored_element_id || item.monitored_element
      const patient = patientStore.patients?.find(p => Number(p.id) === Number(patientId))
      return {
        ...item,
        patient_name: patient ? patient.full_name : 'غير معروف',
        patient_age: patient ? patient.age : 'غير حدد',
        patient_gender: patient ? patient.gender : 'غير محدد',
        message: item.description || getAlertMessageFallback(item)
      }
    })

    if (append) {
      alertsHistory.value = [...alertsHistory.value, ...mapped]
    } else {
      alertsHistory.value = mapped
    }
  } catch (e) {
    console.error('🚨 [Alerts.vue] فشل جلب سجل الإشعارات الطبية:', e)
  } finally {
    loading.value = false
  }
}

// استنباط نص توضيحي في حالة عدم وجود تفاصيل من الباك إند
const getAlertMessageFallback = (item) => {
  const source = item.source?.toLowerCase()
  if (source === 'threshold') {
    return 'تم رصد تجاوز للحدود الحيوية السريرية الصارمة للمريض، يرجى التوجه الفوري للمعاينة السريرية.'
  }
  return 'تجاوز لأحد قواعد الرعاية الطبية أو البروتوكولات العلاجية الموضوعة للمريض.'
}

const isCritical = (alert) => {
  return ['CRITICAL', 'HIGH'].includes(String(alert.severity).toUpperCase())
}

const getSourceLabel = (alert) => {
  const src = alert.source?.toLowerCase()
  if (src === 'threshold') return 'تنبيه عتبة (النظام)'
  if (alert.is_global_rule) return 'بروتوكول عام (المدير)'
  return 'قاعدة طبيب (خاصة)'
}

const getSourceBadgeClass = (alert) => {
  const src = alert.source?.toLowerCase()
  if (src === 'threshold') return 'bg-rose-50 text-rose-800 border-rose-200'
  if (alert.is_global_rule) return 'bg-sky-50 text-sky-800 border-sky-200'
  return 'bg-amber-50 text-amber-800 border-amber-200'
}

// التصفية والترتيب تم تطبيقها كلياً على مستوى قاعدة البيانات الآن لسرعة استجابة هائلة للـ DOM
const filteredAlerts = computed(() => {
  return alertsHistory.value
})

// تصفية الفلاتر المنسدلة الثلاثة وإعادة تحميل التنبيهات من الصفر
const onFilterChange = () => {
  fetchAlertsHistory(false)
}

// 🟢 جلب 50 تنبيهاً إضافياً وزيادة الـ Offset
const loadMore = () => {
  offset.value += limit.value
  fetchAlertsHistory(true)
}

const formatDateTime = (ts) => {
  if (!ts) return ''
  const date = new Date(ts)
  return isNaN(date.getTime()) 
    ? '' 
    : date.toLocaleTimeString('ar-LY', { hour: '2-digit', minute: '2-digit', second: '2-digit', day: '2-digit', month: '2-digit' })
}

const viewPatientDashboard = (alert) => {
  const patientId = alert.monitored_element_id || alert.monitored_element
  const patient = patientStore.patients?.find(p => Number(p.id) === Number(patientId))
  if (patient) {
    patientStore.selectPatient(patient)
    router.push('/dashboard')
  }
}

const resolveAlertLocally = (alertId) => {
  alertsHistory.value = alertsHistory.value.filter(a => a.id !== alertId)
}

onMounted(() => {
  fetchAlertsHistory(false)
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #0d9488;
}
</style>