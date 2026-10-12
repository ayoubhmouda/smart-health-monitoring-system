// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import Register from '../views/register.vue'
import Dashboard from '../views/dashboard.vue'

const routes = [
  // 🟢 1. الصفحة الرئيسية (تفتح من الأعلى بشكل طبيعي)
  {
    path: '/',
    name: 'LandingPage',
    component: () => import('../views/LandingPage.vue')
  },

  // 🟢 2. تحويل أي طلب لـ /login إلى الصفحة الرئيسية مباشرة من بدايتها
  { 
    path: '/login', 
    redirect: '/' 
  },

  { path: '/register', component: Register },

  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/:id/medical-history',
    name: 'MedicalHistory',
    component: () => import('../views/MedicalHistory.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/doctors',
    name: 'DoctorManagement',
    component: () => import('../views/DoctorManagement.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/protocols',
    name: 'ClinicalProtocols',
    component: () => import('../views/ClinicalProtocols.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/protocols/new',
    name: 'CreateProtocol',
    component: () => import('../views/ProtocolBuilder.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/protocols/edit/:id',
    name: 'EditProtocol',
    component: () => import('../views/ProtocolBuilder.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/new',
    name: 'AddPatient',
    component: () => import('../views/AddPatient.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/:id/rules/new',
    name: 'CreatePatientRule',
    component: () => import('../views/PatientRuleBuilder.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/:id/rules/edit/:ruleId',
    name: 'EditPatientRule',
    component: () => import('../views/PatientRuleBuilder.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/Alerts.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return { 
        el: to.hash, 
        behavior: 'smooth',
        top: 80 
      }
    }
    // 🟢 العودة دائماً لأعلى الصفحة عند فتح أي صفحة جديدة
    return savedPosition || { top: 0 }
  }
})

// 🟢 حارس التنقل
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('user_role') || 'doctor'
  const isSuperuser = localStorage.getItem('is_superuser') === 'true'

  // 1. التوجيه لبداية الصفحة الرئيسية إذا لم يكن مسجلاً
  if (to.meta.requiresAuth && !token) {
    return '/'
  }
  
  // 2. إذا كان مسجلاً بالفعل وحاول الذهاب لـ /login حوّله للداشبورد
  if (to.path === '/login' && token) {
    return '/dashboard'
  }

  // 3. حماية صفحات الأدمن
  if (to.meta.requiresAdmin && userRole !== 'admin' && !isSuperuser) {
    console.warn('⚠️ هذه الصفحة مخصصة لمدير النظام والطبيب المشرف فقط!')
    return '/dashboard'
  }
  
  return true
})

router.afterEach(() => {
  try {
    const store = usePatientStore()
    store.isSidebarOpen = false
  } catch (e) {
  }
})

export default router