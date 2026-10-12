<!-- src/components/Navbar.vue -->
<template>
  <nav
    class="sticky top-0 z-50 h-16 bg-slate-100/95 border-b border-slate-200/80 shadow-sm flex items-center justify-between px-4 sm:px-6 select-none"
    :dir="locale === 'ar' ? 'rtl' : 'ltr'"
  >
    <!-- 🟢 1. الشعار جهة اليمين -->
    <router-link to="/dashboard" class="flex items-center gap-2.5 sm:gap-3 group shrink-0">
      <img
        src="/images/thelogo.png"
        alt="Logo"
        class="h-11 sm:h-13 w-auto object-contain transition-transform duration-200 group-hover:scale-105"
      />
    </router-link>

    <!-- 🟢 2. شريط الروابط الأفقي بالمنتصف (تم حذف الإعدادات وبقي الأساسي فقط) -->
    <div class="hidden lg:flex items-center gap-1 select-none">
      <router-link
        v-for="item in visibleNavigation"
        :key="item.to"
        :to="item.to"
        class="nav-link-horizontal"
        active-class="nav-link-horizontal-active"
      >
        <Icon :icon="item.icon" class="w-4.5 h-4.5 shrink-0" />
        <span class="text-xs font-bold leading-none">{{ item.label }}</span>

        <!-- شارة عداد الإشعارات النشطة بالأعلى -->
        <span
          v-if="item.to === '/alerts' && alertsStore.activeAlertsCount"
          class="px-1.5 py-0.2 rounded-full bg-rose-500 text-white text-[10px] font-black shadow-sm shrink-0"
        >
          {{ alertsStore.activeAlertsCount }}
        </span>
      </router-link>
    </div>

    <!-- 🟢 3. الجهة المقابلة: زر تبديل اللغة وزر القائمة للموبايل -->
    <div class="flex items-center gap-2.5 sm:gap-3">
      
      <!-- زر تبديل اللغة (عربي / English) -->
      <button 
        @click="toggleLanguage" 
        class="px-2.5 sm:px-3 py-1.5 rounded-xl border border-slate-300/80 bg-white/90 hover:bg-white text-slate-700 text-xs font-bold transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
        :title="locale === 'ar' ? 'Switch to English' : 'التحويل للعربية'"
      >
        <Icon icon="lucide:globe" class="w-4 h-4 text-teal-700" />
        <span>{{ locale === 'ar' ? 'English' : 'عربي' }}</span>
      </button>

      <!-- زر الهامبرغر يظهر فقط على الموبايل -->
      <button
        @click="store.isSidebarOpen = !store.isSidebarOpen"
        class="lg:hidden p-2 rounded-xl text-teal-800 hover:bg-teal-50 transition-colors cursor-pointer"
        :title="store.isSidebarOpen ? 'إغلاق القائمة' : 'فتح القائمة'"
      >
        <Menu v-if="!store.isSidebarOpen" :size="22" stroke-width="2.5" />
        <X v-else :size="22" stroke-width="2.5" />
      </button>

    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Menu, X } from 'lucide-vue-next'
import { Icon } from '@iconify/vue'
import { usePatientStore } from '../stores/patient'
import { useDoctorStore } from '../stores/doctor'
import { useAlertsStore } from '../stores/alerts'

const store = usePatientStore()
const doctorStore = useDoctorStore()
const alertsStore = useAlertsStore()
const { locale } = useI18n()

// 🟢 دالة تبديل اللغة وحفظ الخيار
const toggleLanguage = () => {
  locale.value = locale.value === 'ar' ? 'en' : 'ar'
  localStorage.setItem('user_lang', locale.value)
}

/* Permissions */
const isAdmin = computed(() => {
  const role = doctorStore.role || localStorage.getItem('user_role')
  const superuser = doctorStore.is_superuser || localStorage.getItem('is_superuser') === 'true'
  return role === 'admin' || superuser === true
})

/* Navigation Items (تم استبعاد الإعدادات تماماً) */
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
</script>

<style scoped>
/* تنسيق أزرار الملاحة الأفقية بالهوية المعتمدة */
.nav-link-horizontal {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.5rem 0.8rem;
  border-radius: 0.75rem;
  color: #64748b; /* slate-500 */
  font-weight: 700;
  transition: all 200ms ease;
  border: 1px solid transparent;
}
.nav-link-horizontal:hover {
  color: #0d9488; /* teal-600 */
  background-color: #f0fdfa; /* teal-50 */
}
.nav-link-horizontal-active {
  color: #ffffff;
  background-color: #0d9488; /* teal-600 */
  border-color: #0f766e;
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.12);
}
</style>