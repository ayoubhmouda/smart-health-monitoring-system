<template>
  <div class="min-h-screen bg-[#0d161b] text-slate-200 p-4 md:p-6" dir="rtl">
    <!-- شريط علوي -->
    <header class="sticky top-0 z-30 bg-[#0d161b]/95 backdrop-blur border-b border-slate-800 px-4 py-3 mb-6 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button @click="$router.back()" class="text-slate-400 hover:text-white transition p-1">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>
        <div>
          <h1 class="text-xl font-bold text-white">{{ patientInfo.full_name || 'التاريخ الطبي' }}</h1>
          <p class="text-sm text-slate-400">تعديل المعلومات الشخصية والطبية</p>
        </div>
      </div>
      <button @click="saveAll" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm transition">
        حفظ التغييرات
      </button>
    </header>

    <!-- مؤشر تحميل -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-10 w-10 border-2 border-blue-400 border-t-transparent"></div>
    </div>

    <!-- النموذج المتكامل -->
    <div v-else class="max-w-4xl mx-auto space-y-6">
      
      <!-- ========== قسم المعلومات الشخصية ========== -->
      <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
        <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
          المعلومات الشخصية
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-slate-400">الاسم الكامل</label>
            <input v-model="patientInfo.full_name" type="text" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="text-xs text-slate-400">تاريخ الميلاد</label>
            <input v-model="patientInfo.date_of_birth" type="date" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="text-xs text-slate-400">الجنس</label>
            <select v-model="patientInfo.gender" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500">
              <option value="M">ذكر</option>
              <option value="F">أنثى</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400">نوع العنصر</label>
            <select v-model="patientInfo.element_type" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500">
              <option value="patient">مريض</option>
              <option value="elderly">مسن</option>
              <option value="disabled">ذو إعاقة</option>
            </select>
          </div>
        </div>
      </section>

      <!-- ========== قسم الأمراض المزمنة ========== -->
      <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
        <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
          الأمراض المزمنة
        </h2>
        <div v-for="(condition, index) in form.chronic_conditions" :key="index" class="flex flex-col sm:flex-row gap-3 mb-3">
          <input v-model="condition.name" placeholder="اسم المرض" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
          <input v-model="condition.diagnosed" placeholder="سنة التشخيص" class="w-full sm:w-32 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
          <input v-model="condition.status" placeholder="الحالة" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
          <input v-model="condition.medication" placeholder="الدواء" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
          <button @click="removeItem('chronic_conditions', index)" class="text-rose-400 hover:text-rose-300 p-1">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <button @click="addItem('chronic_conditions', { name: '', diagnosed: '', status: '', medication: '' })" class="text-blue-400 hover:text-blue-300 text-sm mt-2 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          إضافة مرض
        </button>
      </section>

      <!-- ========== قسم الحساسية ========== -->
      <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
        <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
          الحساسية
        </h2>
        <div class="flex flex-wrap gap-2 mb-3">
          <span v-for="(allergy, idx) in form.allergies" :key="idx" class="bg-rose-900/30 text-rose-300 text-xs px-3 py-1 rounded-full flex items-center gap-1">
            {{ allergy }}
            <button @click="removeItem('allergies', idx)" class="hover:text-white">&times;</button>
          </span>
        </div>
        <div class="flex gap-2">
          <input v-model="newAllergy" placeholder="أضف حساسية" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" @keyup.enter="addAllergy" />
          <button @click="addAllergy" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">إضافة</button>
        </div>
      </section>

      <!-- ========== قسم الأدوية ========== -->
      <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
        <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
          الأدوية الحالية
        </h2>
        <div class="flex flex-wrap gap-2 mb-3">
          <span v-for="(med, idx) in form.medications" :key="idx" class="bg-blue-900/30 text-blue-300 text-xs px-3 py-1 rounded-full flex items-center gap-1">
            {{ med }}
            <button @click="removeItem('medications', idx)" class="hover:text-white">&times;</button>
          </span>
        </div>
        <div class="flex gap-2">
          <input v-model="newMedication" placeholder="أضف دواء" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" @keyup.enter="addMedication" />
          <button @click="addMedication" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">إضافة</button>
        </div>
      </section>

      <!-- ========== قسم نمط الحياة ========== -->
      <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
        <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          نمط الحياة
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label class="text-xs text-slate-400">التدخين</label>
            <select v-model="form.lifestyle.smoking" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500">
              <option value="never">لا يدخن</option>
              <option value="former">سابقاً</option>
              <option value="current">حالياً</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400">الكحول</label>
            <select v-model="form.lifestyle.alcohol" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500">
              <option value="never">لا يشرب</option>
              <option value="former">سابقاً</option>
              <option value="current">حالياً</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400">الرياضة</label>
            <select v-model="form.lifestyle.exercise" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500">
              <option value="low">منخفضة</option>
              <option value="moderate">متوسطة</option>
              <option value="high">عالية</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400">مؤشر كتلة الجسم (BMI)</label>
            <input v-model.number="form.lifestyle.bmi" type="number" step="0.1" class="w-full bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:border-blue-500" />
          </div>
        </div>
      </section>

      <!-- ========== قسم التاريخ العائلي والعمليات ========== -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
          <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            التاريخ العائلي
          </h2>
          <div class="flex flex-wrap gap-2 mb-3">
            <span v-for="(fh, idx) in form.family_history" :key="idx" class="bg-cyan-900/30 text-cyan-300 text-xs px-3 py-1 rounded-full flex items-center gap-1">
              {{ fh }}
              <button @click="removeItem('family_history', idx)" class="hover:text-white">&times;</button>
            </span>
          </div>
          <div class="flex gap-2">
            <input v-model="newFamilyHistory" placeholder="أضف مرض وراثي" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" @keyup.enter="addFamilyHistory" />
            <button @click="addFamilyHistory" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">إضافة</button>
          </div>
        </section>

        <section class="bg-[#13222c] rounded-xl border border-slate-700/50 p-5">
          <h2 class="text-base font-semibold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
            العمليات السابقة
          </h2>
          <div class="flex flex-wrap gap-2 mb-3">
            <span v-for="(surgery, idx) in form.previous_surgeries" :key="idx" class="bg-amber-900/30 text-amber-300 text-xs px-3 py-1 rounded-full flex items-center gap-1">
              {{ surgery }}
              <button @click="removeItem('previous_surgeries', idx)" class="hover:text-white">&times;</button>
            </span>
          </div>
          <div class="flex gap-2">
            <input v-model="newSurgery" placeholder="أضف عملية" class="flex-1 bg-[#0d161b] border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" @keyup.enter="addSurgery" />
            <button @click="addSurgery" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">إضافة</button>
          </div>
        </section>
      </div>

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

// التاريخ الطبي
const form = reactive({
  chronic_conditions: [],
  allergies: [],
  medications: [],
  lifestyle: { smoking: 'never', alcohol: 'never', exercise: 'low', bmi: 22 },
  family_history: [],
  previous_surgeries: []
})

// متغيرات الإدخال الجديدة
const newAllergy = ref('')
const newMedication = ref('')
const newFamilyHistory = ref('')
const newSurgery = ref('')

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
      Object.keys(form).forEach(key => {
        if (h[key] !== undefined) form[key] = h[key]
      })
      if (!form.lifestyle) form.lifestyle = { smoking: 'never', alcohol: 'never', exercise: 'low', bmi: 22 }
    }
  } catch (e) {
    console.error('فشل جلب البيانات:', e)
  } finally {
    loading.value = false
  }
})

// دوال الإضافة والحذف
const addItem = (field, template) => form[field].push(template)
const removeItem = (field, index) => form[field].splice(index, 1)

const addAllergy = () => { if (newAllergy.value.trim()) { form.allergies.push(newAllergy.value.trim()); newAllergy.value = '' } }
const addMedication = () => { if (newMedication.value.trim()) { form.medications.push(newMedication.value.trim()); newMedication.value = '' } }
const addFamilyHistory = () => { if (newFamilyHistory.value.trim()) { form.family_history.push(newFamilyHistory.value.trim()); newFamilyHistory.value = '' } }
const addSurgery = () => { if (newSurgery.value.trim()) { form.previous_surgeries.push(newSurgery.value.trim()); newSurgery.value = '' } }

// حفظ جميع التغييرات
const saveAll = async () => {
  try {
    // 1. تحديث بيانات المريض الشخصية
    await api.patch(`/api/monitored-elements/${patientId}/`, {
      full_name: patientInfo.full_name,
      date_of_birth: patientInfo.date_of_birth,
      gender: patientInfo.gender,
      element_type: patientInfo.element_type
    })

    // 2. تحديث أو إنشاء التاريخ الطبي
    const checkRes = await api.get('/api/medical-histories/', { params: { monitored_element: patientId } })
    const existing = Array.isArray(checkRes.data) ? checkRes.data : (checkRes.data.results || [])

    const payload = {
      monitored_element: parseInt(patientId),
      chronic_conditions: form.chronic_conditions || [],
      allergies: form.allergies || [],
      medications: form.medications || [],
      lifestyle: form.lifestyle || { smoking: 'never', alcohol: 'never', exercise: 'low', bmi: 22 },
      family_history: form.family_history || [],
      previous_surgeries: form.previous_surgeries || [],
    }

    if (existing.length > 0) {
      await api.put(`/api/medical-histories/${existing[0].id}/`, payload)
    } else {
      await api.post('/api/medical-histories/', payload)
    }

    alert('تم حفظ جميع التغييرات بنجاح')
    router.push('/dashboard')
  } catch (e) {
    console.error('فشل الحفظ:', e)
    const msg = e.response?.data?.detail || 'حدث خطأ أثناء الحفظ'
    alert(msg)
  }
}
</script>