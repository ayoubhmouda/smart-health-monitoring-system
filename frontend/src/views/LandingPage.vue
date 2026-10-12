<!-- frontend/src/views/LandingPage.vue -->
<template>
  <div 
    class="min-h-screen bg-white text-slate-900 font-sans selection:bg-teal-700 selection:text-white" 
    :dir="locale === 'ar' ? 'rtl' : 'ltr'"
  >
    
   <!-- 🟢 1. النافبار العلوي (متجاوب وذكي للشاشات الصغيرة والكبيرة) -->
    <header class="sticky top-0 z-50 bg-slate-100/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
      <div class="w-full px-4 sm:px-8 lg:px-14 h-20 sm:h-22 flex items-center justify-between gap-2">
        
        <!-- 1. الشعار والاسم -->
        <router-link to="/" class="flex items-center gap-2 sm:gap-3.5 group shrink-0">
          <img 
            src="/images/thelogo.png" 
            alt="Brumaura Logo" 
            class="h-14 sm:h-13 w-auto object-contain"
          />

          <div class="flex flex-col justify-center">

  <!-- 1. العنوان الرئيسي بخط Lora ولونين -->
  <span class="text-2xl sm:text-3xl font-extrabold tracking-tight leading-none">
    <span class="text-[#0a3d48]">Brume</span><span class="text-teal-500">aura</span>
  </span>

  <!-- 2. العنوان الفرعي بخط Lora -->
  <span class="text-[7px] sm:text-[8px] text-slate-800 font-bold tracking-[0.24em] mt-1">
    Context-Aware Healthcare System
  </span>

</div>
        </router-link>

        <!-- 2. روابط الأقسام (مخفية في الموبايل وتظهر فقط على الشاشات الكبيرة) -->
        <nav class="hidden xl:flex items-center gap-8 lg:gap-10 text-[14px] font-medium text-slate-700">
          <a href="#context-awareness" class="flex items-center gap-1.5 hover:text-[#0a3d48] transition-colors py-2">
            <span>{{ $t('nav.context_awareness') }}</span>
            <Icon icon="lucide:chevron-down" class="w-4 h-4 text-slate-400" />
          </a>
          <a href="#proactive-engine" class="flex items-center gap-1.5 hover:text-[#0a3d48] transition-colors py-2">
            <span>{{ $t('nav.proactive_monitoring') }}</span>
            <Icon icon="lucide:chevron-down" class="w-4 h-4 text-slate-400" />
          </a>
          <a href="#fog-computing" class="flex items-center gap-1.5 hover:text-[#0a3d48] transition-colors py-2">
            <span>{{ $t('nav.fog_architecture') }}</span>
            <Icon icon="lucide:chevron-down" class="w-4 h-4 text-slate-400" />
          </a>
          <a href="#roles-management" class="flex items-center gap-1.5 hover:text-[#0a3d48] transition-colors py-2">
            <span>{{ $t('nav.system_roles') }}</span>
            <Icon icon="lucide:chevron-down" class="w-4 h-4 text-slate-400" />
          </a>
        </nav>

        <!-- 3. الأزرار (أيقونات مصغرة في الموبايل ومكتملة في الكمبيوتر) -->
        <div class="flex items-center gap-2 sm:gap-4 shrink-0">
          
          <!-- زر تبديل اللغة -->
          <button 
            @click="toggleLanguage" 
            class="p-2 sm:px-3 sm:py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1 cursor-pointer"
            :title="locale === 'ar' ? 'English' : 'عربي'"
          >
            <Icon icon="lucide:globe" class="w-4 h-4 text-slate-600" />
            <span class="hidden sm:inline">{{ locale === 'ar' ? 'English' : 'عربي' }}</span>
          </button>

          <!-- زر لوحة التحكم / تسجيل الدخول -->
          <router-link 
            v-if="isLoggedIn" 
            to="/dashboard"
            class="flex items-center gap-1.5 bg-[#0a3d48] hover:bg-[#08323c] text-white p-2 sm:px-4 sm:py-2 rounded-lg transition-colors font-medium text-xs shadow-xs"
          >
            <Icon icon="lucide:layout-dashboard" class="w-4 h-4 text-teal-300" />
            <span class="hidden sm:inline">{{ $t('nav.dashboard') }}</span>
          </router-link>

          <a 
            v-else 
            href="#login-section"
            class="flex items-center gap-1.5 bg-[#0a3d48] hover:bg-[#08323c] text-white p-2 sm:px-4 sm:py-2 rounded-lg transition-colors font-medium text-xs shadow-xs"
          >
            <Icon icon="lucide:user" class="w-4 h-4 text-teal-300" />
            <span class="hidden sm:inline">{{ $t('nav.login') }}</span>
          </a>

        </div>

      </div>
    </header>

    <!-- 🟢 2. قسم الهيرو -->
    <!-- 🟢 2. قسم الهيرو (موقع متوازن على الموبايل وممتاز في الأسفل على اللابتوب) -->
    <section 
      class="relative w-full h-[calc(100vh-5rem)] sm:h-[calc(100vh-5.5rem)] min-h-[520px] sm:min-h-[580px] max-h-[850px] select-none flex flex-col justify-center sm:justify-end items-center bg-cover bg-center overflow-hidden"
      :style="{ 
        backgroundImage: `linear-gradient(to bottom, rgba(2, 8, 14, 0.2) 0%, rgba(2, 8, 14, 0.25) 40%, rgba(3, 11, 18, 0.8) 75%, rgba(2, 6, 12, 0.98) 100%), url('/images/hero-bg.svg')` 
      }"
    >
      <!-- حاوية العنوان: متوازنة في الموبايل ومستقرة في الأسفل على الشاشات الكبيرة -->
      <div class="max-w-5xl w-full mx-auto px-6 sm:px-8 pt-12 sm:pt-0 pb-10 sm:pb-16 lg:pb-20 text-center flex flex-col items-center gap-6 sm:gap-8">
        
        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-normal text-white tracking-normal leading-tight max-w-4xl drop-shadow-md">
          {{ $t('hero.title') }}
        </h1>

        <div class="flex items-center justify-center pt-1">
          <a 
            href="#login-section"
            class="rounded-full border border-white/80 text-white hover:bg-white hover:text-slate-950 px-8 sm:px-10 py-2.5 sm:py-3 text-sm sm:text-base font-normal tracking-wide transition-all duration-200 backdrop-blur-xs shadow-sm"
          >
            {{ $t('hero.cta_button') }}
          </a>
        </div>

      </div>
    </section>

    <!-- 🟢 3. قسم الميزات الأربع -->
    <main class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 py-24 flex flex-col gap-32 sm:gap-40">

      <!-- الميزة 1: تقليل الإنذارات الكاذبة وإدراك السياق -->
      <section id="context-awareness" class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center scroll-mt-28">
        
        <div class="lg:col-span-7 flex flex-col">
          <h2 class="text-3xl sm:text-4xl font-bold text-slate-900 leading-tight mb-4 tracking-tight">
            {{ $t('features.context.title') }}
          </h2>

          <p class="text-base sm:text-lg text-slate-900 leading-relaxed font-normal mb-8">
            {{ $t('features.context.subtitle') }}
          </p>

          <div class="space-y-6">
            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-800 mb-1.5">
                {{ $t('features.context.physiological_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.context.physiological_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.context.activity_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.context.activity_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.context.environment_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.context.environment_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.context.custom_rules_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.context.custom_rules_desc') }}
              </p>
            </div>
          </div>
        </div>

        <div class="lg:col-span-5 flex items-center justify-center">
          <div class="w-full aspect-[4/5] max-h-[560px] rounded-2xl overflow-hidden bg-slate-100 shadow-sm">
            <img 
              src="/images/feature-1-context.png" 
              :alt="$t('features.context.title')"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

      </section>

      <!-- الميزة 2: الاستباقية في الرصد والتنبؤ -->
      <section id="proactive-engine" class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center scroll-mt-28">
        
        <div class="lg:col-span-5 order-2 lg:order-1 flex items-center justify-center">
          <div class="w-full aspect-[4/5] max-h-[560px] rounded-2xl overflow-hidden bg-slate-100 shadow-sm">
            <img 
              src="/images/feature-2-proactive.png" 
              :alt="$t('features.proactive.title')"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

        <div class="lg:col-span-7 order-1 lg:order-2 flex flex-col">
          <h2 class="text-3xl sm:text-4xl font-bold text-slate-900 leading-tight mb-4 tracking-tight">
            {{ $t('features.proactive.title') }}
          </h2>

          <p class="text-base sm:text-lg text-slate-900 leading-relaxed font-normal mb-8">
            {{ $t('features.proactive.subtitle') }}
          </p>

          <div class="space-y-6">
            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.proactive.ai_model_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.proactive.ai_model_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.proactive.safety_rules_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.proactive.safety_rules_desc') }}
              </p>
            </div>
          </div>
        </div>

      </section>

      <!-- الميزة 3: المعالجة اللحظية وتوزيع طبقة الضباب -->
      <section id="fog-computing" class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center scroll-mt-28">
        
        <div class="lg:col-span-7 flex flex-col">
          <h2 class="text-3xl sm:text-4xl font-bold text-slate-900 leading-tight mb-4 tracking-tight">
            {{ $t('features.fog.title') }}
          </h2>

          <p class="text-base sm:text-lg text-slate-900 leading-relaxed font-normal mb-8">
            {{ $t('features.fog.subtitle') }}
          </p>

          <div class="space-y-6">
            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.fog.pipeline_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.fog.pipeline_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.fog.mobile_node_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.fog.mobile_node_desc') }}
              </p>
            </div>
          </div>
        </div>

        <div class="lg:col-span-5 flex items-center justify-center">
          <div class="w-full aspect-[4/5] max-h-[560px] rounded-2xl overflow-hidden bg-slate-100 shadow-sm">
            <img 
              src="/images/feature-3-fog.png" 
              :alt="$t('features.fog.title')"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

      </section>

      <!-- الميزة 4: إدارة أدوار المستخدمين والكادر الطبي -->
      <section id="roles-management" class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center scroll-mt-28">
        
        <div class="lg:col-span-5 order-2 lg:order-1 flex items-center justify-center">
          <div class="w-full aspect-[4/5] max-h-[560px] rounded-2xl overflow-hidden bg-slate-100 shadow-sm">
            <img 
              src="/images/feature-4-roles.png" 
              :alt="$t('features.roles.title')"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

        <div class="lg:col-span-7 order-1 lg:order-2 flex flex-col">
          <h2 class="text-3xl sm:text-4xl font-bold text-slate-900 leading-tight mb-4 tracking-tight">
            {{ $t('features.roles.title') }}
          </h2>

          <p class="text-base sm:text-lg text-slate-900 leading-relaxed font-normal mb-8">
            {{ $t('features.roles.subtitle') }}
          </p>

          <div class="space-y-6">
            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.roles.doctor_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.roles.doctor_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.roles.caregiver_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.roles.caregiver_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.roles.patient_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.roles.patient_desc') }}
              </p>
            </div>

            <div>
              <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-1.5">
                {{ $t('features.roles.admin_title') }}
              </h3>
              <p class="text-base sm:text-lg text-slate-900 font-normal leading-relaxed">
                {{ $t('features.roles.admin_desc') }}
              </p>
            </div>
          </div>
        </div>

      </section>

      <!-- 🟢 4. قسم تسجيل الدخول المسطح -->
      <section id="login-section" class="scroll-mt-28 pt-12 border-t border-slate-200">
        <div class="w-full max-w-sm mx-auto py-8">
          
          <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-slate-900 tracking-tight">{{ $t('login.title') }}</h2>
            <p class="text-xs text-slate-900 mt-2 font-normal">{{ $t('login.subtitle') }}</p>
          </div>

          <!-- رسالة الخطأ -->
          <div v-if="loginError" class="mb-5 p-3 rounded-lg border border-rose-200 bg-rose-50 text-rose-800 text-xs font-medium flex items-center gap-2">
            <Icon icon="lucide:alert-circle" class="w-4 h-4 text-rose-600 shrink-0" />
            <span>{{ loginError }}</span>
          </div>

          <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">{{ $t('login.username_label') }}</label>
              <input 
                v-model="loginForm.username"
                type="text" 
                required
                :placeholder="$t('login.username_placeholder')"
                class="w-full bg-white border border-slate-300 focus:border-slate-900 text-slate-900 text-sm font-normal rounded-lg py-2.5 px-3.5 outline-none transition-colors"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">{{ $t('login.password_label') }}</label>
              <input 
                v-model="loginForm.password"
                type="password" 
                required
                :placeholder="$t('login.password_placeholder')"
                class="w-full bg-white border border-slate-300 focus:border-slate-900 text-slate-900 text-sm font-normal rounded-lg py-2.5 px-3.5 outline-none transition-colors"
              />
            </div>

            <button 
              type="submit"
              :disabled="loginLoading"
              class="w-full mt-3 rounded-full bg-[#08323c] hover:bg-[#0a3d48] text-white font-medium text-sm py-3 px-4 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
            >
              <span v-if="loginLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span v-else>{{ $t('login.submit_button') }}</span>
            </button>
          </form>

        </div>
      </section>

    </main>

    <!-- 🟢 5. الفوتر الأكاديمي والطبي -->
    <footer class="bg-[#0a3d48] text-slate-300 pt-14 pb-10 px-6 sm:px-10 lg:px-16 border-t border-cyan-950 select-none text-xs">
      <div class="max-w-7xl mx-auto">
        
        <!-- الهوية في الفوتر بخط الشعار الموحد -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8 mb-12">
          <div class="lg:col-span-2 flex flex-col items-start gap-3">
            <div class="flex items-center gap-3">
              <img 
                src="/images/thelogo.png" 
                :alt="$t('footer.brand_title')" 
                class="h-9 w-auto object-contain brightness-0 invert opacity-95"
              />
              <!-- 1. العنوان الرئيسي بخط الشعار ولونين متناسقين مع الفوتر -->
              <span class="text-xl font-extrabold tracking-tight leading-none font-brand">
                <span class="text-white">Brume</span><span class="text-teal-400">aura</span>
              </span>

            </div>

            <p class="text-xs text-slate-300 leading-relaxed max-w-sm mt-1">
              {{ $t('footer.brand_description') }}
            </p>
          </div>

          <!-- الأساس العلمي -->
          <div class="flex flex-col gap-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-white">{{ $t('footer.scientific_basis') }}</h4>
            <ul class="space-y-2 text-slate-300 text-xs font-normal">
              <li>
                <a 
                  href="https://arxiv.org/abs/2008.10341" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  class="hover:text-white transition-colors duration-150 inline-flex items-center gap-1 text-cyan-300 font-medium"
                >
                  <span>{{ $t('footer.reference_paper') }}</span>
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </li>
              <li>{{ $t('footer.supervision') }}</li>
              <li>
                <a 
                  href="https://physionet.org/content/mimiciv/" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  class="hover:text-white transition-colors duration-150 inline-flex items-center gap-1"
                >
                  <span>{{ $t('footer.mimic_data') }}</span>
                  <svg class="w-3 h-3 text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </li>
              <li>{{ $t('footer.mapek_loop') }}</li>
            </ul>
          </div>

          <!-- معمارية المنظومة -->
          <div class="flex flex-col gap-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-white">{{ $t('footer.architecture') }}</h4>
            <ul class="space-y-2 text-slate-300 text-xs font-normal">
              <li>{{ $t('footer.context_item') }}</li>
              <li>{{ $t('footer.reasoning_item') }}</li>
              <li>{{ $t('footer.rule_engine_item') }}</li>
              <li>{{ $t('footer.fog_nodes_item') }}</li>
            </ul>
          </div>

          <!-- بوابات المراقبة -->
          <div class="flex flex-col gap-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-white">{{ $t('footer.portals') }}</h4>
            <ul class="space-y-2 text-slate-300 text-xs font-normal">
              <li>{{ $t('footer.duty_portal') }}</li>
              <li>{{ $t('footer.caregiver_portal') }}</li>
              <li>{{ $t('footer.websockets_item') }}</li>
              <li>{{ $t('footer.recovery_item') }}</li>
            </ul>
          </div>

          <!-- بيانات الاعتماد الأكاديمي -->
          <div class="flex flex-col gap-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-white">{{ $t('footer.project_details') }}</h4>
            <ul class="space-y-2 text-slate-300 text-xs font-normal">
              <li class="text-cyan-200 font-medium">{{ $t('footer.degree') }}</li>
              <li class="text-white font-medium">{{ $t('footer.author') }}</li>
              <li>{{ $t('footer.faculty') }}</li>
              <li>{{ $t('footer.university') }}</li>
              <li class="text-slate-400">{{ $t('footer.term') }}</li>
            </ul>
          </div>

        </div>

        <div class="w-full h-px bg-slate-700/50 mb-6"></div>

        <!-- الحقوق والروابط -->
        <div class="flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-normal text-slate-400">
          <div>
            {{ $t('footer.copyright') }}
          </div>

          <div class="flex items-center gap-1 text-slate-300">
            <span class="hover:text-white cursor-pointer transition-colors">{{ $t('footer.user_guide') }}</span>
            <span class="mx-2 text-slate-600">|</span>
            <span class="hover:text-white cursor-pointer transition-colors">{{ $t('footer.privacy_policy') }}</span>
            <span class="mx-2 text-slate-600">|</span>
            <span class="hover:text-white cursor-pointer transition-colors">{{ $t('footer.terms_of_use') }}</span>
          </div>
        </div>

      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import api from '../api'
import { useDoctorStore } from '../stores/doctor'

const router = useRouter()
const doctorStore = useDoctorStore()
const { t, locale } = useI18n()

const toggleLanguage = () => {
  locale.value = locale.value === 'ar' ? 'en' : 'ar'
  localStorage.setItem('user_lang', locale.value)
}

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('token')
})

const loginForm = ref({
  username: '',
  password: ''
})

const loginLoading = ref(false)
const loginError = ref('')

const handleLogin = async () => {
  loginError.value = ''
  loginLoading.value = true

  try {
    const res = await api.post('/api/login/', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })

    if (res.data?.token) {
      localStorage.setItem('token', res.data.token)

      try {
        await doctorStore.fetchProfile()
      } catch (err) {
        console.error('فشل جلب الملف الشخصي:', err)
      }

      router.push('/dashboard')
    } else {
      loginError.value = t('login.invalid_error')
    }
  } catch (err) {
    console.error('خطأ تسجيل الدخول:', err)
    loginError.value = err.response?.data?.non_field_errors?.[0] || 
                       err.response?.data?.error || 
                       t('login.invalid_error')
  } finally {
    loginLoading.value = false
  }
}
</script>

<style scoped>
html {
  scroll-behavior: smooth;
}
</style>