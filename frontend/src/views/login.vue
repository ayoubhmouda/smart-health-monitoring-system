<template>
  <div class="min-h-screen flex items-center justify-center bg-[#0b1319] p-4">
    <div class="w-full max-w-md bg-[#111c24] border border-[#1e2d38] rounded-2xl shadow-2xl shadow-black/50 p-8">
      
      <!-- الشعار والهوية -->
      <div class="text-center mb-8">
        <div class="flex items-center justify-center gap-2 mb-3">
          <span class="w-3 h-3 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.6)]"></span>
          <h1 class="text-2xl font-black bg-gradient-to-l from-white to-slate-400 bg-clip-text text-transparent tracking-wider font-mono">
            SMART HEALTH
          </h1>
        </div>
        <p class="text-xs text-slate-500 font-mono tracking-wide">نظام المراقبة الطبية الذكي</p>
      </div>

      <!-- خط فاصل -->
      <div class="border-t border-[#1e2d38] mb-6"></div>

      <!-- نموذج تسجيل الدخول -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <!-- حقل اسم المستخدم -->
        <div>
          <label for="username" class="block text-xs font-bold text-slate-400 mb-1.5 uppercase tracking-wider">اسم المستخدم</label>
          <div class="relative">
            <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <input
              v-model="username"
              type="text"
              id="username"
              class="w-full bg-[#0b1319] border border-[#1e2d38] rounded-xl px-4 py-3 pr-10 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all duration-200"
              placeholder="أدخل اسم المستخدم"
              required
            />
          </div>
        </div>

        <!-- حقل كلمة المرور -->
        <div>
          <label for="password" class="block text-xs font-bold text-slate-400 mb-1.5 uppercase tracking-wider">كلمة المرور</label>
          <div class="relative">
            <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <input
              v-model="password"
              type="password"
              id="password"
              class="w-full bg-[#0b1319] border border-[#1e2d38] rounded-xl px-4 py-3 pr-10 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all duration-200"
              placeholder="أدخل كلمة المرور"
              required
            />
          </div>
        </div>

        <!-- زر تسجيل الدخول -->
        <button
          type="submit"
          class="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-3 px-4 rounded-xl transition-all duration-200 active:scale-[0.98] shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20"
        >
          دخول
        </button>
      </form>

      <!-- خط فاصل -->
      <div class="border-t border-[#1e2d38] mt-6 pt-4 text-center">
        <p class="text-[10px] text-slate-600 font-mono tracking-wide">
          نظام مراقبة طبية ذكي | مشروع تخرج
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useDoctorStore } from '../stores/doctor'

const username = ref('')
const password = ref('')
const router = useRouter()
const doctorStore = useDoctorStore()

const handleLogin = async () => {
  try {
    const response = await api.post('/api/login/', {
      username: username.value,
      password: password.value
    })
    
    if (response.data.token) {
      localStorage.setItem('token', response.data.token)
      // جلب بيانات الطبيب من الخادم وتخزينها في Pinia
      await doctorStore.fetchProfile()
      router.push('/dashboard')
    } else {
      alert('لم يتم استلام رمز الدخول من الخادم')
    }
  } catch (error) {
    alert('اسم المستخدم أو كلمة المرور غير صحيحة')
  }
}
</script>