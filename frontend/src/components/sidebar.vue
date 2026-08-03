<!-- sidebar.vue -->
<template>
  <!-- 🟢 زر فتح الشريط الجانبي للشاشات الصغيرة مبرمج بنفس لون الـ Sidebar تماماً #0D9488 -->
  <button 
    @click="store.isSidebarOpen = !store.isSidebarOpen" 
    class="lg:hidden fixed bottom-5 left-5 z-55 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0d9488] text-white border border-white/10 hover:border-white/30 shadow-2xl shadow-teal-950/40 active:scale-95 transition-all duration-300"
  >
    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path v-if="!store.isSidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
    <span class="text-xs font-bold">{{ store.isSidebarOpen ? 'إغلاق' : 'المرضى' }}</span>
  </button>

  <!-- خلفية شفافة ومظللة للجوال عند فتح الشريط الجانبي -->
  <div v-if="store.isSidebarOpen" @click="store.isSidebarOpen = false" class="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-xs z-30"></div>

  <!-- 🟢 الشريط الجانبي الرئيسي الفخم باللون التركوازي الطبي المميز #0D9488 -->
  <aside 
    :class="[
      store.isSidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0',
      'fixed inset-y-0 right-0 z-40 lg:static w-64 bg-[#0d9488] border-l border-white/10 flex flex-col transition-transform duration-300 ease-in-out min-h-screen shadow-xl'
    ]" 
    dir="rtl"
  >
    <!-- 🟢 1. رأس الشريط الأنيق والمنقح (تم حذف عبارة SMART HEALTH ووضع مؤشر أمان ناعم بدلها) -->
    <div class="p-5 pb-4 border-b border-white/10 flex items-center justify-between">
      <div class="flex items-center gap-2 select-none">
        <!-- نقطة الهوية الطبية النابضة باللون الأبيض المضيء -->
        <span class="w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)] animate-pulse"></span>
        <span class="text-xs font-bold text-white/90">مراقب الحالات الحيوية</span>
      </div>
      <span class="text-[9px] bg-white/20 text-white border border-white/20 px-2 py-0.5 rounded-full font-bold font-mono">V2.0</span>
    </div>

    <!-- 2. ملف الطبيب المعالج بتنسيق عالي التباين متناسق مع الخلفية التركوازية -->
    <div class="px-5 py-3 border-b border-white/10">
      <router-link to="/profile" class="flex items-center gap-3 group cursor-pointer">
        <div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white font-extrabold text-sm">
          {{ doctorInitials }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-white group-hover:underline truncate">{{ doctorName }}</p>
          <p class="text-[10px] text-teal-100/80 font-medium">طبيب معالج</p>
        </div>
        <svg class="w-3.5 h-3.5 text-white/70 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
    </div>

    <!-- 🟢 3. زر إضافة مريض جديد باللون الأزرق الفاخر والبارز #2563EB تماشياً مع طلبك -->
    <div class="px-5 py-3.5">
      <button 
        @click="openAddPatient"
        class="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs py-3 px-4 rounded-xl transition-all duration-200 active:scale-[0.98] shadow-md shadow-blue-900/20 hover:shadow-blue-900/30"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
        </svg>
        <span>إضافة مريض جديد</span>
      </button>
    </div>

    <!-- 4. قائمة سجل الحالات المراقبة بالتأثيرات البيئية المضيئة عالية المقروئية لخط الـ IBM -->
    <div class="px-5 py-2 border-b border-white/10">
      <h3 class="text-[10px] font-bold text-teal-100/60 tracking-widest uppercase mb-1">سجل الحالات المراقبة</h3>
    </div>
    
    <nav class="flex-1 px-3 py-2 overflow-y-auto max-h-[calc(100vh-380px)] custom-scrollbar space-y-1">
      <ul class="space-y-1.5">
        <li v-for="patient in patients" :key="patient.id"
            @click="selectPatient(patient)"
            :class="[
              store.currentPatient?.id === patient.id 
                ? 'bg-white text-teal-900 shadow-md border-white' 
                : 'border-transparent text-teal-50 hover:bg-white/10 hover:text-white'
            ]"
            class="group p-3 rounded-xl border-r-4 cursor-pointer transition-all duration-200 flex flex-col gap-1.5 relative overflow-hidden"
        >
          <!-- خط الجاذبية الداخلي عند تحديد المريض النشط -->
          <div v-if="store.currentPatient?.id === patient.id" class="absolute top-0 bottom-0 right-0 w-1 bg-teal-600"></div>
          
          <div class="text-sm font-bold transition-colors">
            {{ patient.full_name }}
          </div>
          <div class="text-[11px] flex items-center gap-1.5 opacity-80 group-hover:opacity-100 font-medium">
            <span :class="store.currentPatient?.id === patient.id ? 'text-slate-500' : 'text-teal-100/80'">{{ patient.element_type }}</span>
            <span :class="store.currentPatient?.id === patient.id ? 'text-slate-300' : 'text-teal-700'" class="font-mono">•</span>
            <span :class="store.currentPatient?.id === patient.id ? 'text-teal-700' : 'text-teal-200'" class="font-mono font-bold">{{ patient.age }} سنة</span>
          </div>
        </li>
        <li v-if="patients.length === 0" class="text-center text-teal-100/50 text-xs py-6">لا يوجد مرضى بعد</li>
      </ul>
    </nav>

    <!-- 5. تذييل الشريط (تغيير اللغة وإنهاء الجلسة) بتناسق تام -->
    <div class="p-4 border-t border-white/10 space-y-2 bg-black/10">
      <!-- زر تبديل اللغة المشرق والشفاف -->
      <button 
        @click="toggleLanguage" 
        class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl bg-white/10 border border-white/10 hover:border-white/30 text-xs font-semibold text-teal-50 hover:text-white transition-all duration-200"
      >
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-teal-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          <span>{{ locale === 'ar' ? 'English' : 'العربية' }}</span>
        </div>
        <span class="text-[9px] font-mono uppercase bg-white/20 px-1.5 py-0.5 rounded text-white font-bold">{{ locale }}</span>
      </button>

      <!-- زر إنهاء الجلسة بلون الورد الناعم عالي التباين -->
      <button 
        @click="logout" 
        class="w-full flex items-center justify-center gap-2 bg-rose-500/20 hover:bg-rose-600/30 text-white font-bold text-xs py-2.5 px-4 rounded-xl border border-white/10 shadow-sm active:scale-[0.98] transition-all duration-200"
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

const doctorName = computed(() => doctorStore.name || 'طبيب')
const doctorInitials = computed(() => {
  const name = doctorName.value
  const parts = name.trim().split(' ')
  if (parts.length >= 2 && parts[1].length > 0) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
})

const toggleLanguage = () => {
  locale.value = locale.value === 'ar' ? 'en' : 'ar'
}

const openAddPatient = () => {
  store.showAddModal = true
}

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

const selectPatient = (patient) => {
  store.selectPatient(patient)
  store.isSidebarOpen = false
  router.push('/dashboard')
}

const logout = () => {
  localStorage.removeItem('token')
  doctorStore.clearProfile()
  router.push('/login')
}

if (store.isSidebarOpen === undefined) store.isSidebarOpen = false
if (store.showAddModal === undefined) store.showAddModal = false

onMounted(fetchPatients)
</script>

<style scoped>
/* شريط التمرير مخصص للمقروئية داخل الخلفية التركوازية */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.4); }
</style>