<!-- MedicalHistory.vue -->
<template>
  <div class="min-h-screen bg-[#F0F6F5] text-slate-600 p-4 md:p-6" dir="rtl">
    
    <!-- هيدر الاستمارة السريرية المشرق والعائم -->
    <header class="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-slate-100 px-6 py-4 mb-6 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm shadow-slate-100/30">
      <div class="flex items-center gap-4">
        <button @click="$router.back()" class="text-slate-400 hover:text-teal-600 transition-colors p-1.5 bg-slate-50 hover:bg-slate-100 rounded-xl border border-slate-100">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 class="text-xl font-extrabold text-slate-800 tracking-tight">{{ patientInfo.full_name || 'الملف الطبي للمريض' }}</h1>
          <p class="text-xs text-slate-400 font-medium mt-1">تحديث البيانات الديموغرافية والطبية التي تؤثر على نموذج التنبؤ</p>
        </div>
      </div>
      
      <!-- زر حفظ التغييرات المتناسق -->
      <button @click="saveAll" class="bg-[#0D9488] hover:bg-[#0f766e] text-white text-xs font-bold px-6 py-3 rounded-xl shadow-md shadow-teal-900/10 transition-all duration-200">
        حفظ التغييرات السريرية
      </button>
    </header>

    <!-- مؤشر التحميل المضيء والناعم -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-teal-500 border-t-transparent"></div>
    </div>

    <!-- النموذج الرشيق والمبسط المتطابق مع النموذج الرياضي -->
    <div v-else class="max-w-3xl mx-auto space-y-6">
      
      <!-- ========== 1. قسم المعلومات الشخصية (تؤثر على السن والجنس في الموديل) ========== -->
      <section class="bg-white rounded-3xl border border-slate-100 p-6 shadow-sm shadow-slate-100/50 space-y-4">
        <h2 class="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
          <div class="w-7 h-7 rounded-full bg-teal-50 flex items-center justify-center text-teal-600">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
          </div>
          <span>المعلومات الشخصية والديموغرافية</span>
        </h2>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-[10px] font-bold text-slate-400 uppercase">الاسم الكامل</label>
            <input v-model="patientInfo.full_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-bold text-slate-700 mt-1 focus:outline-none focus:border-teal-500" />
          </div>
          <div>
            <label class="text-[10px] font-bold text-slate-400 uppercase">تاريخ الميلاد</label>
            <input v-model="patientInfo.date_of_birth" type="date" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-bold text-slate-700 mt-1 focus:outline-none focus:border-teal-500" />
          </div>
          <div>
            <label class="text-[10px] font-bold text-slate-400 uppercase">الجنس</label>
            <select v-model="patientInfo.gender" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-bold text-slate-700 mt-1 focus:outline-none focus:border-teal-500 cursor-pointer">
              <option value="M">ذكر</option>
              <option value="F">أنثى</option>
            </select>
          </div>
          <div>
            <label class="text-[10px] font-bold text-slate-400 uppercase">تصنيف الحالة</label>
            <select v-model="patientInfo.element_type" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-bold text-slate-700 mt-1 focus:outline-none focus:border-teal-500 cursor-pointer">
              <option value="patient">مريض (Patient)</option>
              <option value="elderly">مسن (Elderly)</option>
              <option value="disabled">ذو إعاقة (Disabled)</option>
            </select>
          </div>
        </div>
      </section>

      <!-- ========== 2. قسم التاريخ الطبي الفعلي (يؤثر على السكر والضغط والقلب في الموديل) ========== -->
      <section class="bg-white rounded-3xl border border-slate-100 p-6 shadow-sm shadow-slate-100/50 space-y-5">
        <h2 class="text-sm font-bold text-slate-800 mb-2 flex items-center gap-2">
          <div class="w-7 h-7 rounded-full bg-rose-50 flex items-center justify-center text-rose-500">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
          </div>
          <span>التاريخ الطبي والمزمن الفعلي للمريض</span>
        </h2>
        
        <div class="space-y-4 pt-2">
          <!-- 🟢 خيار 1: أمراض القلب والشرايين (has_heart_disease) -->
          <label class="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-150 cursor-pointer hover:bg-slate-100/50 transition-colors select-none">
            <input v-model="hasHeartDisease" type="checkbox" class="w-4 h-4 text-teal-600 border-slate-300 rounded focus:ring-teal-500 cursor-pointer" />
            <div class="flex flex-col">
              <span class="text-xs font-bold text-slate-700">التاريخ المرضي لأمراض القلب (Heart Disease)</span>
              <span class="text-[10px] text-slate-400 mt-0.5">يشمل: قصور القلب، احتشاء عضلة القلب، أو الذبحة الصدرية السابقة</span>
            </div>
          </label>

          <!-- 🟢 خيار 2: الأمراض المزمنة الأخرى (has_chronic_condition) -->
          <label class="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-150 cursor-pointer hover:bg-slate-100/50 transition-colors select-none">
            <input v-model="hasChronicCondition" type="checkbox" class="w-4 h-4 text-teal-600 border-slate-300 rounded focus:ring-teal-500 cursor-pointer" />
            <div class="flex flex-col">
              <span class="text-xs font-bold text-slate-700">الإصابة بأمراض مزمنة عامة (Chronic Conditions)</span>
              <span class="text-[10px] text-slate-400 mt-0.5">يشمل: داء السكري (Type 2 Diabetes)، أو ارتفاع ضغط الدم (Hypertension)</span>
            </div>
          </label>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const patientId = route.params.id
const loading = ref(true)

// معلومات المريض الشخصية
const patientInfo = reactive({
  full_name: '',
  date_of_birth: '',
  gender: 'M',
  element_type: 'patient'
})

// 🟢 متغيرات التحكم الثنائية البسيطة المتوافقة مع منطق الـ ML والـ 22 ميزة
const hasHeartDisease = ref(false)
const hasChronicCondition = ref(false)

onMounted(async () => {
  try {
    // جلب بيانات المريض الشخصية
    const patientRes = await api.get(`/api/monitored-elements/${patientId}/`)
    Object.assign(patientInfo, {
      full_name: patientRes.data.full_name,
      date_of_birth: patientRes.data.date_of_birth,
      gender: patientRes.data.gender,
      element_type: patientRes.data.element_type
    })

    // جلب التاريخ الطبي
    const historyRes = await api.get('/api/medical-histories/', { params: { monitored_element: patientId } })
    const data = Array.isArray(historyRes.data) ? historyRes.data : (historyRes.data.results || [])
    
    if (data.length > 0) {
      const h = data[0]
      const conditions = h.chronic_conditions || []
      
      // 🟢 فك وتوزيع الميزات من الـ JSON المخزن في قاعدة البيانات لتفعيل خانات الاختيار
      const condNames = conditions.map(c => typeof c === 'string' ? c.toLowerCase() : String(c.name || '').toLowerCase())
      hasHeartDisease.value = condNames.some(c => ['heart_disease', 'heart_failure', 'cardiac', '410', '428', 'i50', 'i21'].includes(c))
      hasChronicCondition.value = condNames.some(c => ['diabetes', 'hypertension', 'copd', '401', '250', 'e11', 'i10'].includes(c))
    }
  } catch (e) {
    console.error('فشل جلب الملف الطبي:', e)
  } finally {
    loading.value = false
  }
})

// حفظ وإرسال التغييرات ومزامنتها بدقة فسيولوجية
const saveAll = async () => {
  try {
    // 1. تحديث بيانات المريض الشخصية
    await api.patch(`/api/monitored-elements/${patientId}/`, {
      full_name: patientInfo.full_name,
      date_of_birth: patientInfo.date_of_birth,
      gender: patientInfo.gender,
      element_type: patientInfo.element_type
    })

    // 2. تحديث أو إنشاء التاريخ الطبي الفعلي لربط الخواص لـ الـ ML
    const checkRes = await api.get('/api/medical-histories/', { params: { monitored_element: patientId } })
    const existing = Array.isArray(checkRes.data) ? checkRes.data : (checkRes.data.results || [])

    // 🟢 تجميع الميزات المختارة محلياً وصياغتها كـ JSON متوافق مع فك الترميز في الباك إند
    const conditions = []
    if (hasHeartDisease.value) {
      conditions.push({ name: 'heart_disease' })
    }
    if (hasChronicCondition.value) {
      conditions.push({ name: 'diabetes' }) // يُفسر في الـ ML كـ has_chronic_condition
    }

    const payload = {
      monitored_element: parseInt(patientId),
      chronic_conditions: conditions,
      allergies: [],
      medications: [],
      lifestyle: { smoking: 'never', alcohol: 'never', exercise: 'low', bmi: 22 },
      family_history: [],
      previous_surgeries: []
    }

    if (existing.length > 0) {
      await api.put(`/api/medical-histories/${existing[0].id}/`, payload)
    } else {
      await api.post('/api/medical-histories/', payload)
    }

    alert('تم حفظ وتحديث ملف المريض وتاريخه الطبي بنجاح!')
    router.push('/dashboard')
  } catch (e) {
    console.error('فشل الحفظ التكاملي:', e)
    const msg = e.response?.data?.detail || 'حدث خطأ أثناء حفظ الملف الطبي'
    alert(msg)
  }
}
</script>