<!-- Login.vue -->
<template>
  <div class="min-h-screen w-full grid grid-cols-1 lg:grid-cols-12 bg-slate-50 font-sans" dir="rtl">
    
    <!-- الجانب الأيمن / الشريط العلوي للموبايل: الهوية البصرية -->
    <div class="col-span-1 lg:col-span-7 xl:col-span-8 bg-gradient-to-br from-teal-950 via-slate-900 to-emerald-950 text-white p-6 sm:p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden">
      
      <!-- خلفية جمالية مدمجة وشبكة بصرية -->
      <div class="absolute inset-0 opacity-15 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:20px_20px]"></div>
      <div class="absolute -top-24 -right-24 w-72 h-72 lg:w-96 lg:h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <!-- الهيدر العلوي للشعار -->
      <div class="relative z-10 flex items-center gap-3">
        <div class="w-9 h-9 lg:w-10 lg:h-10 rounded-xl bg-teal-500/20 border border-teal-400/30 flex items-center justify-center backdrop-blur-md shadow-lg shadow-teal-500/10">
          <span class="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-teal-400 animate-pulse"></span>
        </div>
        <div class="flex flex-col">
          <span class="text-lg lg:text-xl font-black tracking-wider text-white">
            Medi<span class="text-teal-400">Watch</span>
          </span>
          <span class="text-[9px] lg:text-[10px] text-teal-300/80 font-mono tracking-widest uppercase">Clinical Intelligence System</span>
        </div>
      </div>

      <!-- محتوى الهوية (يظهر بشكل مختصر على الموبايل وبكامل التفاصيل على الشاشات الكبيرة) -->
      <div class="relative z-10 max-w-2xl space-y-3 lg:space-y-6 my-4 lg:my-auto">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300 text-[11px] lg:text-xs font-semibold backdrop-blur-md">
          <Icon icon="mdi:shield-check-outline" class="w-3.5 h-3.5 text-emerald-400" />
          <span>منظومة مراقبة سريرية مدعومة بالذكاء الاصطناعي</span>
        </div>

        <h1 class="text-2xl sm:text-3xl lg:text-5xl font-black leading-tight text-white tracking-tight">
          إدارة سريرية ذكية.. <br class="hidden sm:inline" />
          <span class="text-transparent bg-clip-text bg-gradient-to-l from-teal-200 via-emerald-300 to-teal-400">
            لقرارات طبية حاسمة ولحظية
          </span>
        </h1>

        <p class="hidden sm:block text-slate-300 text-xs lg:text-base leading-relaxed max-w-xl">
          ربط شامل مع حساسات العلامات الحيوية (IoT)، تحليل لحظي للمخاطر السريرية، ومحرك قواعد مخصص لمساعدة الأطباء في اتخاذ القرارات العلاجية بدقة فائقة.
        </p>

        <!-- مؤشرات أداء النظام (تظهر في الشاشات المتوسطة والكبيرة) -->
        <div class="hidden sm:grid pt-2 lg:pt-6 grid-cols-2 gap-3 lg:gap-4 max-w-md">
          <div class="p-3 lg:p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
            <div class="flex items-center gap-2 text-teal-400 text-[10px] lg:text-xs font-bold mb-1">
              <Icon icon="mdi:chart-line" class="w-3.5 h-3.5" />
              <span>خوارزميات التنبؤ</span>
            </div>
            <div class="text-base lg:text-xl font-extrabold text-white">MIMIC-IV</div>
            <div class="text-[10px] lg:text-[11px] text-slate-400 mt-0.5">نماذج ذكاء مدربة سريرياً</div>
          </div>

          <div class="p-3 lg:p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
            <div class="flex items-center gap-2 text-emerald-400 text-[10px] lg:text-xs font-bold mb-1">
              <Icon icon="mdi:lightning-bolt-outline" class="w-3.5 h-3.5" />
              <span>الاستجابة الحيوية</span>
            </div>
            <div class="text-base lg:text-xl font-extrabold text-white">Real-Time</div>
            <div class="text-[10px] lg:text-[11px] text-slate-400 mt-0.5">معالجة بروتوكولات IoT لحظية</div>
          </div>
        </div>
      </div>

      <!-- الفوتر السفلية (تظهر فقط في الشاشات الكبيرة) -->
      <div class="hidden lg:flex relative z-10 text-xs text-slate-400 border-t border-white/10 pt-4 justify-between items-center font-mono">
        <span>MediWatch SHMS v2.4</span>
        <span>مشروع تخرج | هندسة البرمجيات</span>
      </div>
    </div>

    <!-- الجانب الأيسر: نموذج تسجيل الدخول -->
    <div class="col-span-1 lg:col-span-5 xl:col-span-4 flex items-center justify-center p-6 sm:p-10 bg-white relative">
      <div class="w-full max-w-sm space-y-6 lg:space-y-8">
        
        <div class="space-y-1.5">
          <h2 class="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight">تسجيل الدخول</h2>
          <p class="text-xs sm:text-sm text-slate-500">أدخل بيانات الاعتماد المعتمدة للوصول إلى اللوحة السريرية</p>
        </div>

        <!-- نموذج الدخول -->
        <form @submit.prevent="handleLogin" class="space-y-4 lg:space-y-5">
          
          <!-- حقل اسم المستخدم -->
          <div>
            <label for="username" class="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wider">
              اسم المستخدم
            </label>
            <div class="relative group">
              <Icon 
                icon="mdi:account-outline" 
                class="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-teal-600 transition-colors" 
              />
              <input
                v-model="username"
                type="text"
                id="username"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 pr-11 text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10 transition-all duration-200"
                placeholder="أدخل اسم المستخدم"
                required
              />
            </div>
          </div>

          <!-- حقل كلمة المرور -->
          <div>
            <label for="password" class="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wider">
              كلمة المرور
            </label>
            <div class="relative group">
              <Icon 
                icon="mdi:lock-outline" 
                class="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-teal-600 transition-colors" 
              />
              <input
                v-model="password"
                type="password"
                id="password"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 pr-11 text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10 transition-all duration-200"
                placeholder="أدخل كلمة المرور"
                required
              />
            </div>
          </div>

          <!-- زر تسجيل الدخول -->
          <button
            type="submit"
            class="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-200 active:scale-[0.99] shadow-lg shadow-teal-700/20 hover:shadow-teal-700/30 flex items-center justify-center gap-2 mt-2"
          >
            <span>دخول للنظام</span>
            <Icon icon="mdi:arrow-left" class="w-5 h-5" />
          </button>
        </form>

        <div class="border-t border-slate-100 pt-4 text-center">
          <p class="text-[11px] text-slate-400 font-medium">
            نظام مراقبة طبية ذكي | مشروع تخرج
          </p>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useDoctorStore } from '../stores/doctor'
import { Icon } from '@iconify/vue'

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

      const savedName = response.data.full_name || response.data.user?.full_name || username.value
      localStorage.setItem('username', username.value)
      localStorage.setItem('full_name', savedName)

      const userRole = response.data.role || response.data.user?.role || (response.data.is_superuser || response.data.user?.is_superuser ? 'admin' : 'doctor')
      const isSuperuser = response.data.is_superuser || response.data.user?.is_superuser ? 'true' : 'false'

      localStorage.setItem('user_role', userRole)
      localStorage.setItem('is_superuser', isSuperuser)

      await doctorStore.fetchProfile()
      
      if (doctorStore.role) {
        localStorage.setItem('user_role', doctorStore.role)
      }

      router.push('/dashboard')
    } else {
      alert('لم يتم استلام رمز الدخول من الخادم')
    }
  } catch (error) {
    console.error('Login error:', error)
    alert('اسم المستخدم أو كلمة المرور غير صحيحة')
  }
}
</script>