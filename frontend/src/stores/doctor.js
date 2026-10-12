import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useDoctorStore = defineStore('doctor', () => {
  const name = ref('')
  const role = ref(localStorage.getItem('user_role') || '') // 🟢 قراءة القيمة الأولية فوراً
  const id = ref(null)
  const is_superuser = ref(localStorage.getItem('is_superuser') === 'true') // 🟢 إضافة حقل الأدمن المفقود

  // 🟢 خاصية مساعدة جاهزة لمعرفة هل المستخدم أدمن بسهولة في أي صفحة
  const isAdmin = computed(() => {
    return role.value === 'admin' || is_superuser.value === true
  })

  const fetchProfile = async () => {
    try {
      const res = await api.get('/api/user/profile/')
      const data = res.data

      name.value = data.full_name || data.username
      role.value = data.role
      id.value = data.id
      is_superuser.value = Boolean(data.is_superuser) // 🟢 حفظ السوبر أدمن

      // 🟢 1. الحفظ التلقائي في localStorage ليقرأه حارس الـ Router فوراً
      localStorage.setItem('user_role', data.role)
      localStorage.setItem('is_superuser', String(data.is_superuser))
    } catch (e) {
      console.error('فشل جلب بيانات الطبيب:', e)
    }
  }

  const clearProfile = () => {
    name.value = ''
    role.value = ''
    id.value = null
    is_superuser.value = false

    // 🟢 مسح البيانات عند تسجيل الخروج
    localStorage.removeItem('user_role')
    localStorage.removeItem('is_superuser')
  }

  return { 
    name, 
    role, 
    id, 
    is_superuser, 
    isAdmin, 
    fetchProfile, 
    clearProfile 
  }
})