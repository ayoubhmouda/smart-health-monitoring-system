<!-- Settings.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- هيدر الصفحة -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <Icon icon="mdi:cog-outline" class="w-5 h-5 text-teal-300" />
          <span class="text-xs text-teal-200 font-mono font-extrabold uppercase tracking-wider">إعدادات النظام</span>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">تفضيلات الحساب والتطبيق</h1>
        <p class="text-xs text-teal-200/70 mt-1">إدارة اللغة، معلومات النظام، وخيارات تسجيل الخروج</p>
      </div>
    </header>

    <!-- بطاقة اللغة -->
    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white p-4 flex items-center gap-2">
        <Icon icon="mdi:translate" class="w-5 h-5 text-teal-300" />
        <h3 class="font-extrabold text-sm">اللغة</h3>
      </div>
      
      <div class="p-6 flex flex-col sm:flex-row items-center gap-4">
        <p class="text-xs text-slate-500 font-semibold flex-1">
          اختر لغة واجهة التطبيق المناسبة لك.
        </p>
        <div class="flex items-center gap-2">
          <button 
            @click="setLocale('ar')" 
            class="px-4 py-2 rounded-xl font-bold text-xs transition-all cursor-pointer"
            :class="locale === 'ar' ? 'bg-teal-600 text-white shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
          >
            العربية
          </button>
          <button 
            @click="setLocale('en')" 
            class="px-4 py-2 rounded-xl font-bold text-xs transition-all cursor-pointer"
            :class="locale === 'en' ? 'bg-teal-600 text-white shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
          >
            English
          </button>
        </div>
      </div>
    </div>

    <!-- بطاقة حول النظام -->
    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white p-4 flex items-center gap-2">
        <Icon icon="mdi:information-outline" class="w-5 h-5 text-teal-300" />
        <h3 class="font-extrabold text-sm">حول النظام</h3>
      </div>
      
      <div class="p-6 space-y-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center border border-teal-100">
            <Icon icon="mdi:heart-pulse" class="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <p class="font-extrabold text-slate-800 text-sm">MediWatch</p>
            <p class="text-[10px] text-slate-400 font-semibold">نظام المراقبة الذكية للمرضى</p>
          </div>
        </div>
        
        <p class="text-xs text-slate-600 leading-relaxed font-semibold">
          منصة متطورة لمراقبة العلامات الحيوية للمرضى في الزمن الحقيقي، مع محاكاة السيناريوهات السريرية وتنبؤات ذكاء اصطناعي.
        </p>
        
        <div class="pt-2 border-t border-slate-100 text-[10px] text-slate-400 font-mono font-bold">
          الإصدار 1.0.0 - جميع الحقوق محفوظة © 2026
        </div>
      </div>
    </div>

    <!-- تسجيل الخروج -->
    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="p-6">
        <button 
          @click="logout" 
          class="w-full flex items-center justify-center gap-2 py-3 rounded-2xl bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-600 font-bold text-sm transition-all cursor-pointer"
        >
          <Icon icon="mdi:logout" class="w-5 h-5" />
          تسجيل الخروج
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useDoctorStore } from '../stores/doctor'
import { Icon } from '@iconify/vue'

const { locale } = useI18n()
const router = useRouter()
const doctorStore = useDoctorStore()

const setLocale = (lang) => {
  locale.value = lang
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('is_superuser')
  localStorage.removeItem('full_name')

  doctorStore.clearProfile()

  router.push('/login')
}
</script>