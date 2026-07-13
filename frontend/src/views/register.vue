<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center text-blue-800">إنشاء حساب</h2>
      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="username">اسم المستخدم</label>
          <input
            v-model="username"
            type="text"
            id="username"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="أدخل اسم المستخدم"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="email">البريد الإلكتروني</label>
          <input
            v-model="email"
            type="email"
            id="email"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="أدخل البريد الإلكتروني"
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="password">كلمة المرور</label>
          <input
            v-model="password"
            type="password"
            id="password"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="أدخل كلمة المرور"
            required
          />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="role">الدور</label>
          <select
            v-model="role"
            id="role"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="doctor">طبيب</option>
            <option value="caregiver">مقدم رعاية</option>
          </select>
        </div>
        <div class="flex items-center justify-between mb-6">
          <button
            type="submit"
            class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline"
          >
            إنشاء حساب
          </button>
        </div>
        <p class="text-center text-gray-500 text-sm">
          لديك حساب بالفعل؟ <router-link to="/login" class="text-blue-500 hover:text-blue-700">تسجيل الدخول</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const email = ref('')
const password = ref('')
const role = ref('doctor')
const router = useRouter()

const handleRegister = async () => {
  try {
    await axios.post('http://localhost:8000/api/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      role: role.value,
    })
    alert('تم إنشاء الحساب بنجاح! سيتم توجيهك لصفحة تسجيل الدخول.')
    router.push('/login')
  } catch (error) {
    const msg = error.response?.data?.error || 'حدث خطأ أثناء إنشاء الحساب'
    alert(msg)
  }
}
</script>