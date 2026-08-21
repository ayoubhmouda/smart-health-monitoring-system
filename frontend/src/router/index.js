// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { usePatientStore } from '../stores/patient' // استيراد متجر المريض للإغلاق التلقائي
import Login from '../views/login.vue'       // 🟢 تم تصحيح حرف l الصغير
import Register from '../views/register.vue' // 🟢 تم تصحيح حرف r الصغير
import Dashboard from '../views/dashboard.vue' // 🟢 تم تصحيح حرف d الصغير لمطابقة اسم الملف على القرص

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  {
    path: '/dashboard',
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
    meta: { requiresAuth: true } // تم إزالة شرط الأدمن للسماح للأطباء بالدخول وتصفح الكادر الطبي (قراءة فقط)
  },
  {
    path: '/protocols',
    name: 'ClinicalProtocols',
    component: () => import('../views/ClinicalProtocols.vue'),
    meta: { requiresAuth: true } // تم إزالة شرط الأدمن للسماح للأطباء بالدخول وقراءة البروتوكولات السريرية
  },
  {
    path: '/protocols/new',
    name: 'CreateProtocol',
    component: () => import('../views/ProtocolBuilder.vue'),
    meta: { requiresAuth: true, requiresAdmin: true } // حصر إضافة بروتوكول جديد لمدير النظام فقط
  },
  {
    path: '/protocols/edit/:id',
    name: 'EditProtocol',
    component: () => import('../views/ProtocolBuilder.vue'),
    meta: { requiresAuth: true, requiresAdmin: true } // حصر تعديل بروتوكول قائم لمدير النظام فقط
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  // مسار إضافة مريض جديد
  {
    path: '/patients/new',
    name: 'AddPatient',
    component: () => import('../views/AddPatient.vue'),
    meta: { requiresAuth: true }
  },
  // مسارات قواعد المريض المخصصة
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
  // مسار الإشعارات الطارئة
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/Alerts.vue'),
    meta: { requiresAuth: true }
  },
  // إضافة مسار صفحة الإعدادات (Settings) إلى الراوتر
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// حارس التنقل - الأسلوب الجديد (return بدلاً من next())
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('user_role') || 'doctor'
  const isSuperuser = localStorage.getItem('is_superuser') === 'true'

  if (to.meta.requiresAuth && !token) {
    return '/login'
  }
  
  if (to.path === '/login' && token) {
    return '/dashboard'
  }

  // طرد المستخدم إذا حاول الدخول لصفحات الصيانة والإضافة ( requiresAdmin ) وهو ليس مديراً
  if (to.meta.requiresAdmin && userRole !== 'admin' && !isSuperuser) {
    console.warn('⚠️ هذه الصفحة مخصصة لمدير النظام والطبيب المشرف فقط!')
    return '/dashboard'
  }
  
  return true
})

// الحل السحري للجوال: إغلاق السايدبار بأمان تام وتلقائياً بعد نجاح تحويل الصفحة
router.afterEach(() => {
  try {
    const store = usePatientStore()
    store.isSidebarOpen = false
  } catch (e) {
    // تجاهل الأخطاء الصامتة في الجلسات الأولى قبل تحميل المتجر
  }
})

export default router