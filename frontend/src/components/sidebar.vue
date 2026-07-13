<template>
  <!-- زر فتح الشريط الجانبي للشاشات الصغيرة -->
  <button 
    @click="store.isSidebarOpen = !store.isSidebarOpen" 
    class="lg:hidden fixed bottom-5 left-5 z-50 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#111c24] text-slate-200 border border-[#1e2d38] hover:border-cyan-500/50 shadow-2xl shadow-black/80 active:scale-95 transition-all duration-300"
  >
    <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path v-if="!store.isSidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
    <span class="text-xs font-medium">{{ store.isSidebarOpen ? 'إغلاق' : 'المرضى' }}</span>
  </button>

  <!-- خلفية شفافة للجوال عند فتح الشريط -->
  <div v-if="store.isSidebarOpen" @click="store.isSidebarOpen = false" class="lg:hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-40"></div>

  <!-- الشريط الجانبي الرئيسي -->
  <aside 
    :class="[
      store.isSidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0',
      'fixed inset-y-0 right-0 z-40 lg:static w-64 bg-[#13222c] border-l border-[#1e2d38] flex flex-col transition-transform duration-300 ease-in-out min-h-screen'
    ]" 
    dir="rtl"
  >
    <!-- 1. رأس الشريط (الشعار) -->
    <div class="p-5 pb-4 border-b border-[#1e2d38]">
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.7)]"></span>
        <h2 class="text-lg font-black bg-gradient-to-l from-white to-slate-400 bg-clip-text text-transparent tracking-wider font-mono">
          SMART HEALTH
        </h2>
      </div>
    </div>

    <!-- 2. ملف الطبيب -->
    <div class="px-5 py-3 border-b border-[#1e2d38]">
      <router-link to="/profile" class="flex items-center gap-3 group cursor-pointer">
        <div class="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold text-sm">
          {{ doctorInitials }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-200 group-hover:text-white truncate">{{ doctorName }}</p>
          <p class="text-[10px] text-slate-500 group-hover:text-cyan-400">طبيب معالج</p>
        </div>
        <svg class="w-4 h-4 text-slate-600 group-hover:text-cyan-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
    </div>

    <!-- 3. زر إضافة مريض جديد -->
    <div class="px-5 py-3">
      <button 
        @click="openAddPatient"
        class="w-full flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm py-2.5 px-4 rounded-xl transition-all duration-200 active:scale-[0.98] shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
        </svg>
        <span>إضافة مريض جديد</span>
      </button>
    </div>

    <!-- 4. قائمة المرضى (ثابتة الارتفاع وقابلة للتمرير) -->
    <div class="px-5 py-2 border-b border-[#1e2d38]">
      <h3 class="text-[10px] font-bold text-slate-500 tracking-widest uppercase font-mono mb-2">سجل الحالات المراقبة</h3>
    </div>
    <nav class="flex-1 px-3 overflow-y-auto max-h-[calc(100vh-380px)] custom-scrollbar">
      <ul class="space-y-1">
        <li v-for="patient in patients" :key="patient.id"
            @click="selectPatient(patient)"
            :class="[
              store.currentPatient?.id === patient.id 
                ? 'bg-cyan-500/10 border-cyan-500 text-white' 
                : 'border-transparent text-slate-400 hover:bg-[#1c2c35]/50 hover:text-slate-200'
            ]"
            class="group p-3 rounded-xl border-r-4 cursor-pointer transition-all duration-200 flex flex-col gap-1"
        >
          <div class="text-sm font-medium group-hover:text-cyan-400 transition-colors">
            {{ patient.full_name }}
          </div>
          <div class="text-[11px] flex items-center gap-1.5 opacity-80 group-hover:opacity-100">
            <span class="text-slate-400">{{ patient.element_type }}</span>
            <span class="text-slate-600 font-mono">•</span>
            <span class="text-cyan-500/80 font-mono">{{ patient.age }} سنة</span>
          </div>
        </li>
        <li v-if="patients.length === 0" class="text-center text-slate-500 text-xs py-4">لا يوجد مرضى بعد</li>
      </ul>
    </nav>

    <!-- 5. تذييل الشريط (اللغة والإعدادات) -->
    <div class="p-4 border-t border-[#1e2d38] space-y-2">
      <!-- زر تبديل اللغة -->
      <button 
        @click="toggleLanguage" 
        class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl bg-[#111c24] border border-[#16222f] hover:border-cyan-500/30 text-xs font-medium text-slate-400 hover:text-white transition-all duration-200"
      >
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-slate-500 group-hover:text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          <span>{{ locale === 'ar' ? 'English' : 'العربية' }}</span>
        </div>
        <span class="text-[9px] font-mono uppercase bg-[#16222f] px-1.5 py-0.5 rounded text-cyan-400 font-bold">{{ locale }}</span>
      </button>

      <!-- زر إنهاء الجلسة -->
      <button 
        @click="logout" 
        class="w-full flex items-center justify-center gap-2 bg-rose-500/5 hover:bg-rose-600/10 text-rose-400 font-bold text-xs py-2.5 px-4 rounded-xl border border-rose-500/10 hover:border-rose-500/20 shadow-sm active:scale-[0.98] transition-all duration-200"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        <span>إنهاء الجلسة</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '../api'
import { usePatientStore } from '../stores/patient'
import { useDoctorStore } from '../stores/doctor'

const router = useRouter()
const store = usePatientStore()
const doctorStore = useDoctorStore()
const { locale } = useI18n()
const patients = ref([])

// دوال مساعدة للحصول على بيانات الطبيب من Pinia Store
const doctorName = computed(() => doctorStore.name || 'طبيب')
const doctorInitials = computed(() => {
  const name = doctorName.value
  const parts = name.trim().split(' ')
  if (parts.length >= 2 && parts[1].length > 0) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
})

// تبديل اللغة
const toggleLanguage = () => {
  locale.value = locale.value === 'ar' ? 'en' : 'ar'
}

// فتح نموذج إضافة مريض جديد
const openAddPatient = () => {
  store.showAddModal = true
}

// جلب قائمة المرضى
const fetchPatients = async () => {
  try {
    const res = await api.get('/api/monitored-elements/')
    const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
    patients.value = data
    store.patients = data
  } catch (e) {
    console.error('فشل جلب المرضى:', e)
  }
}

// اختيار مريض
const selectPatient = (patient) => {
  store.selectPatient(patient)
  store.isSidebarOpen = false
  router.push('/dashboard')
}

// تسجيل الخروج
const logout = () => {
  localStorage.removeItem('token')
  doctorStore.clearProfile()
  router.push('/login')
}

// التأكد من وجود الخصائص
if (store.isSidebarOpen === undefined) store.isSidebarOpen = false
if (store.showAddModal === undefined) store.showAddModal = false

onMounted(fetchPatients)
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e2d38; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #06b6d4; }
</style>