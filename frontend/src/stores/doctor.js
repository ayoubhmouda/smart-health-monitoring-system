import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useDoctorStore = defineStore('doctor', () => {
  const name = ref('')
  const role = ref('')
  const id = ref(null)

  const fetchProfile = async () => {
    try {
      const res = await api.get('/api/user/profile/')
      name.value = res.data.full_name || res.data.username
      role.value = res.data.role
      id.value = res.data.id
    } catch (e) {
      console.error('فشل جلب بيانات الطبيب:', e)
    }
  }

  const clearProfile = () => {
    name.value = ''
    role.value = ''
    id.value = null
  }

  return { name, role, id, fetchProfile, clearProfile }
})