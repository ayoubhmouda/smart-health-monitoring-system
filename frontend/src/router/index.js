import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// حارس التنقل - الأسلوب الجديد (return بدلاً من next())
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    // إرجاع المسار لتوجيه المستخدم
    return '/login'
  }
  
  if (to.path === '/login' && token) {
    return '/dashboard'
  }
  
  // السماح بالمرور (عدم إرجاع شيء أو إرجاع true)
  return true
})

export default router