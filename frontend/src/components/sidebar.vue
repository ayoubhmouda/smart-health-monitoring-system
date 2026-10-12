<!-- src/components/sidebar.vue -->
<template>
  <aside
    class="flex flex-col overflow-hidden shadow-2xl transition-transform duration-300 border-l border-white/10
      fixed top-16 bottom-0 right-0 z-40 w-[245px] max-w-[90vw]
      lg:static lg:top-auto lg:bottom-auto lg:z-auto lg:w-[245px] lg:max-w-none lg:translate-x-0 lg:h-full select-none"
    :class="{
      'translate-x-full': !store.isSidebarOpen,
      'translate-x-0': store.isSidebarOpen
    }"
    dir="rtl"
  >
    <!-- Background Gradient -->
    <div class="absolute inset-0 -z-10 bg-gradient-to-b from-[#0a3742] via-[#0d4553] to-[#072a33]" />

    <div class="relative flex flex-col h-full min-h-0">
      
      <!-- 🟢 شريط الروابط الفردية يظهر فقط على الموبايل ويختفي تماماً على أجهزة اللابتوب (lg:hidden) -->
      <div class="px-2 py-2 border-b border-white/10 flex-shrink-0 lg:hidden select-none">
        <nav class="space-y-0.5">
          <router-link
            v-for="item in visibleNavigation"
            :key="item.to"
            :to="item.to"
            class="nav-link"
            active-class="nav-link-active"
          >
            <div class="flex items-center gap-2.5">
              <Icon :icon="item.icon" class="w-4 h-4" />
              <span class="text-xs font-medium">{{ item.label }}</span>
            </div>

            <!-- عداد الإشعارات الحمراء النشطة بالسايدبار على الموبايل -->
            <span
              v-if="item.to === '/alerts' && alertsStore.activeAlertsCount"
              class="px-1.5 py-0.2 rounded-full bg-rose-500 text-white text-[10px] font-black shadow-sm"
            >
              {{ alertsStore.activeAlertsCount }}
            </span>
          </router-link>
        </nav>
      </div>

      <!-- Primary Action: Add Patient (يظهر للطبيب والمشرف فقط) -->
      <div v-if="canAddPatient" class="px-3 py-2 flex-shrink-0">
        <router-link to="/patients/new" class="add-patient-btn">
          <Icon icon="mdi:plus" class="w-4 h-4" />
          <span>إضافة مريض جديد</span>
        </router-link>
      </div>

      <!-- Patient Section Header (ثابت) -->
      <div class="px-3 py-2 flex items-center justify-between border-y border-white/10 bg-black/10 flex-shrink-0">
        <h3 class="text-[10px] font-bold uppercase tracking-wider text-cyan-200/70">
          سجل المراقبة الحية
        </h3>
        <span class="patient-count-badge">{{ patients.length }}</span>
      </div>

      <!-- Patient List (الوحيد القابل للتمرير والمصنف فسيولوجياً بالأولوية التامة) -->
      <nav class="flex-1 min-h-0 overflow-y-auto px-2 py-1.5 custom-scrollbar space-y-0.5">
        <div
          v-for="patient in sortedPatients"
          :key="patient.id"
          @click="selectPatient(patient)"
          :class="patientClasses(patient)"
          class="relative overflow-hidden transition-all duration-300"
        >
          <div class="flex items-center justify-between w-full min-w-0">
            <div class="min-w-0 flex-1">
              <p class="text-[11px] font-bold truncate leading-tight flex items-center gap-1.5">
                <!-- الوميض النبضي الأحمر السريع لاسم المريض المصاب بخطر حرج حالياً -->
                <span v-if="alertsStore.patientAlertStates[patient.id] === 'CRITICAL'" class="flex h-2 w-2 relative shrink-0">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
                </span>
                <!-- الوميض النبضي البرتقالي الهادئ للخطر المتوسط -->
                <span v-else-if="alertsStore.patientAlertStates[patient.id] === 'HIGH'" class="flex h-2 w-2 relative shrink-0">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                </span>
                <span>{{ patient.full_name }}</span>
              </p>
              <p class="text-[10px] text-cyan-200/60 mt-0.5 truncate">
                {{ patient.age }} سنة <span class="opacity-40">•</span> {{ patient.element_type }}
              </p>
            </div>
            
            <!-- شارات التنبيه الرقمية الملونة بالدرجة المحددة سريرياً -->
            <span v-if="alertsStore.patientAlertStates[patient.id] === 'CRITICAL'" class="px-1.5 py-0.2 rounded bg-rose-500 text-white text-[9px] font-black shrink-0 ml-1.5 animate-pulse">
              إنذار حرج
            </span>
            <span v-else-if="alertsStore.patientAlertStates[patient.id] === 'HIGH'" class="px-1.5 py-0.2 rounded bg-amber-500 text-slate-900 text-[9px] font-black shrink-0 ml-1.5">
              انتباه
            </span>

            <Icon
              v-if="store.currentPatient?.id === patient.id && !alertsStore.patientAlertStates[patient.id]"
              icon="mdi:check"
              class="w-4 h-4 shrink-0 text-teal-300"
            />
          </div>
        </div>

        <div v-if="!patients.length" class="py-8 text-center text-xs text-cyan-200/40">
          لا يوجد مرضى حالياً
        </div>
      </nav>

      <!-- 🟢 Footer: Profile Card + زر تسجيل الخروج المضاف -->
      <footer class="p-2.5 border-t border-white/10 bg-black/15 flex-shrink-0 space-y-2">
        
        <!-- بطاقة الملف الشخصي -->
        <router-link
          to="/profile"
          class="group flex items-center gap-2.5 p-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-200"
        >
          <div class="shrink-0 flex items-center justify-center text-teal-300 group-hover:scale-105 transition-transform">
            <Icon :icon="roleIcon" class="w-6 h-6 shrink-0" />
          </div>

          <div class="min-w-0 flex-1">
            <p class="text-xs font-bold text-white truncate leading-tight">{{ doctorName }}</p>
            <p class="text-[10px] text-cyan-200/60 truncate mt-0.5">{{ roleLabel }}</p>
          </div>

          <Icon icon="mdi:chevron-left" class="w-4 h-4 shrink-0 text-cyan-200/40" />
        </router-link>

        <!-- 🟢 زر تسجيل الخروج المضاف أسفل الملف الشخصي -->
        <button
          @click="handleLogout"
          class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-rose-300/90 hover:text-white bg-rose-500/10 hover:bg-rose-500/25 border border-rose-500/20 hover:border-rose-500/40 transition-all duration-200 cursor-pointer text-xs font-bold shadow-xs"
        >
          <div class="flex items-center gap-2">
            <Icon icon="solar:logout-2-bold" class="w-4 h-4 text-rose-400" />
            <span>تسجيل الخروج</span>
          </div>
          <Icon icon="mdi:chevron-left" class="w-3.5 h-3.5 opacity-40" />
        </button>

      </footer>
    </div>
  </aside>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import api from '../api'
import { usePatientStore } from '../stores/patient'
import { useDoctorStore } from '../stores/doctor'
import { useAlertsStore } from '../stores/alerts'

const router = useRouter()
const store = usePatientStore()
const doctorStore = useDoctorStore()
const alertsStore = useAlertsStore()
const patients = ref([])

/* Doctor Details */
const doctorName = computed(() => doctorStore.name || 'طبيب')

const doctorInitials = computed(() => {
  const parts = doctorName.value.trim().split(' ')
  return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : doctorName.value.substring(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  if (isAdmin.value) return 'مشرف النظام'
  const role = doctorStore.role || ''
  if (role === 'doctor') return 'طبيب معالج'
  if (role === 'caregiver' || role === 'nurse') return 'مقدم رعاية'
  return 'طبيب'
})

const roleIcon = computed(() => {
  if (isAdmin.value) return 'solar:shield-user-bold'
  const role = doctorStore.role || ''
  if (role === 'doctor') return 'solar:stethoscope-bold'
  if (role === 'caregiver' || role === 'nurse') return 'boxicons:handshake-filled'
  return 'solar:user-bold'
})

/* Permissions */
const isAdmin = computed(() => {
  const role = doctorStore.role || localStorage.getItem('user_role')
  const superuser = doctorStore.is_superuser || localStorage.getItem('is_superuser') === 'true'
  return role === 'admin' || superuser === true
})

const canAddPatient = computed(() => {
  const role = doctorStore.role || localStorage.getItem('user_role') || ''
  return role === 'doctor' || role === 'admin' || isAdmin.value
})

/* Navigation Items */
const navigation = [
  {
    label: 'الكادر الطبي والأطباء',
    to: '/doctors',
    icon: 'grommet-icons:form-next',
    allowedRoles: ['admin', 'doctor'] 
  },
  {
    label: 'البروتوكولات السريرية',
    to: '/protocols',
    icon: 'grommet-icons:form-next',
    allowedRoles: ['admin', 'doctor'] 
  },
  {
    label: 'التنبيهات السريرية',
    to: '/alerts',
    icon: 'grommet-icons:form-next',
    allowedRoles: ['admin', 'doctor', 'caregiver', 'nurse']
  }
]

const visibleNavigation = computed(() => {
  const currentRole = doctorStore.role || localStorage.getItem('user_role') || 'doctor'
  return navigation.filter(item => {
    if (!item.allowedRoles) return true
    return item.allowedRoles.includes(currentRole) || (isAdmin.value && item.allowedRoles.includes('admin'))
  })
})

/* 🟢 تنفيذ عملية تسجيل الخروج بأمان */
const handleLogout = () => {
  // 1. مسح التوكن وبيانات المستخدم من المتصفح
  localStorage.removeItem('token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('is_superuser')
  localStorage.removeItem('user')

  // 2. تصفير الحالة في الـ Store
  store.isSidebarOpen = false
  store.currentPatient = null

  // 3. التوجيه المباشر للصفحة الرئيسية من البداية
  router.push('/')
}

/* Patient Handling */
const fetchPatients = async () => {
  try {
    const { data } = await api.get('/api/monitored-elements/')
    patients.value = Array.isArray(data) ? data : data.results || []
    store.patients = patients.value
    
    alertsStore.setupAllWebSockets(patients.value)
    
    patients.value.forEach(patient => alertsStore.updatePatientAlertState(patient.id))
  } catch (error) {
    console.error('فشل جلب المرضى:', error)
  }
}

const sortedPatients = computed(() => {
  return [...patients.value].sort((a, b) => {
    const aState = alertsStore.patientAlertStates[a.id]
    const bState = alertsStore.patientAlertStates[b.id]
    
    const aWeight = aState === 'CRITICAL' ? 2 : (aState === 'HIGH' ? 1 : 0)
    const bWeight = bState === 'CRITICAL' ? 2 : (bState === 'HIGH' ? 1 : 0)
    
    return bWeight - aWeight 
  })
})

const patientClasses = patient => {
  const selected = store.currentPatient?.id === patient.id
  const alertState = alertsStore.patientAlertStates[patient.id] 
  
  if (alertState === 'CRITICAL') {
    return [
      'patient-item',
      selected ? 'patient-item-alert-selected' : 'patient-item-alert'
    ]
  } else if (alertState === 'HIGH') {
    return [
      'patient-item',
      selected ? 'patient-item-alert-high-selected' : 'patient-item-alert-high'
    ]
  }
  
  return [
    'patient-item',
    selected ? 'patient-item-selected' : 'patient-item-default'
  ]
}

const selectPatient = patient => {
  store.selectPatient(patient)
  store.isSidebarOpen = false
  router.push('/dashboard')
}

if (store.isSidebarOpen === undefined) store.isSidebarOpen = false
if (store.showAddModal === undefined) store.showAddModal = false

onMounted(async () => {
  if (!doctorStore.role) {
    await doctorStore.fetchProfile()
  }
  fetchPatients()
})
</script>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border-radius: 0.5rem;
  color: rgba(207, 250, 254, 0.75);
  transition: all 150ms ease;
}
.nav-link:hover { color: #fff; background: rgba(255,255,255,0.08); }
.nav-link-active { color: #fff; background: rgba(255,255,255,0.12); }

.add-patient-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 0.875rem;
  border-radius: 0.5rem;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  background: #0d9488;
  border: 1px solid rgba(255,255,255,0.15);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: all 150ms ease;
}
.add-patient-btn:hover { background: #14b8a6; transform: translateY(-1px); }

.patient-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.65rem;
  border-radius: 0.5rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 150ms ease;
}
.patient-item-default { color: rgba(207,250,254,0.85); }
.patient-item-default:hover { color: #fff; background: rgba(255,255,255,0.06); }
.patient-item-selected { color: #fff; background: rgba(255,255,255,0.12); border-color: rgba(45,212,191,0.3); }

.patient-item-alert { color: #ffe4e6; background: rgba(225,29,72,0.15); border-color: rgba(244,63,94,0.3); }
.patient-item-alert-selected { color: #fff; background: rgba(225,29,72,0.35); border-color: rgba(244,63,94,0.6); }

.patient-item-alert-high { color: #fef3c7; background: rgba(245,158,11,0.15); border-color: rgba(245,158,11,0.3); }
.patient-item-alert-high:hover { color: #fff; background: rgba(245,158,11,0.25); }
.patient-item-alert-high-selected { color: #fff; background: rgba(245,158,11,0.35); border-color: rgba(245,158,11,0.6); }

.patient-count-badge {
  font-size: 10px;
  font-family: monospace;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(255,255,255,0.08);
  color: #cffafe;
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(103,232,249,0.2) transparent;
}
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(103,232,249,0.2); border-radius: 999px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(103,232,249,0.4); }
</style>