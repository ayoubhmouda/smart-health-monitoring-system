<!-- AddPatient.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- 🟢 الترويسة العلوية باللون التركوازي -->
    <header class="w-full rounded-3xl p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white select-none shrink-0">
      <div class="flex items-center gap-3">
        <!-- الأيقونة حرة بالكامل بدون صندوق وحاوية باللون الأبيض الناصع -->
        <Icon icon="solar:user-plus-bold" class="w-8 h-8 text-white shrink-0" />
        
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs text-teal-300 font-mono font-extrabold uppercase tracking-wider">لوحة إسكان المرضى</span>
            <span class="text-[10px] bg-white/10 text-teal-200 px-2.5 py-0.5 rounded-full font-bold">تسجيل ملف جديد</span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold text-white tracking-tight">تسجيل وإسكان مريض جديد بالمنظومة</h1>
          <p class="text-xs text-teal-200/70 mt-1 font-medium">تأسيس الملف الديموغرافي، السجل الطبي السريري، وربط أو إنشاء حساب مقدم الرعاية للمريض</p>
        </div>
      </div>

      <!-- الأزرار نصوص باللون الأبيض فقط بدون أي خلفيات أو مربعات -->
      <div class="flex items-center gap-6 w-full sm:w-auto justify-end select-none">
        <button 
          @click="discardChanges" 
          class="text-white hover:text-teal-200 font-bold text-xs transition-colors cursor-pointer bg-transparent p-0 border-0 outline-none"
        >
          إلغاء وتراجع
        </button>
        <button 
          @click="submitPatientForm" 
          class="text-white hover:text-teal-200 font-bold text-xs transition-colors cursor-pointer bg-transparent p-0 border-0 outline-none"
        >
          حفظ وتسجيل المريض
        </button>
      </div>
    </header>

    <!-- الأقسام الثلاثة اللوجستية الموزعة بوضوح وتباين عالٍ متجاوب -->
    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch w-full">
      
      <!-- القسم الأول والثاني في بطاقات مستقلة متجاورة -->
      <div class="lg:col-span-8 flex flex-col gap-6">
        
        <!-- 🟢 1. البيانات الشخصية والديموغرافية الأساسية للمريض -->
        <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="text-teal-300 font-mono font-bold text-sm select-none">1.</span>
              <span class="font-extrabold text-white text-xs">البيانات الشخصية والديموغرافية الأساسية للمريض</span>
            </div>
            <Icon icon="solar:user-bold" class="w-5 h-5 text-white shrink-0" />
          </div>

          <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">الاسم الكامل للمريض <span class="text-rose-500">*</span></label>
              <input 
                v-model="form.full_name" 
                type="text" 
                required 
                placeholder="أدخل الاسم الرباعي للمريض" 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 placeholder-slate-400" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">تاريخ الميلاد <span class="text-rose-500">*</span></label>
              <input 
                v-model="form.date_of_birth" 
                type="date" 
                required 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">الجنس <span class="text-rose-500">*</span></label>
              <select v-model="form.gender" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-900">
                <option value="M">ذكر (Male)</option>
                <option value="F">أنثى (Female)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">تصنيف الحالة الطبية</label>
              <select v-model="form.element_type" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-900">
                <option value="patient">مريض (Patient)</option>
                <option value="elderly">مسن رعاية (Elderly)</option>
                <option value="disabled">احتياجات خاصة (Disabled)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 🟢 2. التاريخ الطبي والأمراض المزمنة للمريض -->
        <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col"> 
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="text-teal-300 font-mono font-bold text-sm select-none">2.</span>
              <span class="font-extrabold text-white text-xs">التاريخ الطبي والمزمن الفعلي للمريض (MIMIC Co-morbidities)</span>
            </div>
            <Icon icon="solar:notes-bold" class="w-5 h-5 text-white shrink-0" />
          </div>

          <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- خيار أمراض القلب -->
            <label class="flex items-start gap-3 bg-slate-50/50 p-4 border border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-colors">
              <input 
                type="checkbox" 
                v-model="medicalHistoryFlags.heart_disease" 
                class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4 mt-0.5 cursor-pointer" 
              />
              <div>
                <p class="text-sm font-bold text-slate-750">التاريخ المرضي لأمراض القلب (Heart Disease)</p>
                <p class="text-[10px] text-slate-400 mt-0.5 font-medium">يشمل: قصور القلب، احتشاء عضلة القلب، أو الذبحة الصدرية السابقة</p>
              </div>
            </label>

            <!-- خيار الأمراض المزمنة العامة -->
            <label class="flex items-start gap-3 bg-slate-50/50 p-4 border border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-colors">
              <input 
                type="checkbox" 
                v-model="medicalHistoryFlags.chronic_conditions" 
                class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4 mt-0.5 cursor-pointer" 
              />
              <div>
                <p class="text-sm font-bold text-slate-750">الإصابة بأمراض مزمنة عامة (Chronic Conditions)</p>
                <p class="text-[10px] text-slate-400 mt-0.5 font-medium">يشمل: داء السكري (Type 2 Diabetes)، أو ارتفاع ضغط الدم (Hypertension)</p>
              </div>
            </label>
          </div>
        </div>

      </div>

      <!-- العمود الأيسر: 🟢 3. إسناد وإدارة مقدم الرعاية -->
      <div class="lg:col-span-4 bg-white rounded-3xl border border-slate-200/80 shadow-sm flex flex-col justify-between overflow-hidden gap-0">
        <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none shrink-0">
          <div class="flex items-center gap-2">
            <span class="text-teal-300 font-mono font-bold text-sm select-none">3.</span>
            <span class="font-extrabold text-white text-xs">إسناد وإدارة مقدم الرعاية (Caregiver)</span>
          </div>
          <Icon icon="solar:users-group-rounded-bold" class="w-5 h-5 text-white shrink-0" />
        </div>

        <div class="p-6 space-y-4 text-xs flex-1 flex flex-col justify-between gap-5">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">خيارات إشراك مقدم الرعاية</label>
              <select v-model="form.caregiver_option" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-900 cursor-pointer">
                <option value="none">بدون مقدم رعاية حالياً</option>
                <option value="existing">اختيار مقدم رعاية مسجّل مسبقاً</option>
                <option value="new">إنشاء حساب جديد كلياً لمقدم الرعاية</option>
              </select>
            </div>

            <!-- أ. في حال اختيار مقدم رعاية مسجل مسبقاً -->
            <div v-if="form.caregiver_option === 'existing'" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
              <label class="block font-bold text-slate-65">اختر مقدم الرعاية من قائمة المستشفى</label>
              <select v-model="form.existing_caregiver_id" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900 cursor-pointer">
                <option v-for="care in caregivers" :key="care.id" :value="care.id">
                  {{ care.full_name }}
                </option>
              </select>
            </div>

            <!-- ب. في حال إنشاء حساب جديد لمقدم الرعاية -->
            <div v-if="form.caregiver_option === 'new'" class="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
              <p class="font-bold text-slate-750 border-b border-slate-200/60 pb-1.5">بيانات الحساب الجديد لمقدم الرعاية:</p>
              
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-bold text-slate-700 mb-1.5">الاسم الكامل لمقدم الرعاية <span class="text-rose-500">*</span></label>
                  <input v-model="form.caregiver_full_name" type="text" required placeholder="مثال: فاطمة فتحي محمد" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 focus:border-teal-500 outline-none font-bold text-slate-900 placeholder-slate-400" />
                </div>

                <div>
                  <label class="block text-sm font-bold text-slate-700 mb-1.5">اسم المستخدم (Username) <span class="text-rose-500">*</span></label>
                  <input v-model="form.caregiver_username" type="text" required placeholder="fatima_f" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 focus:border-teal-500 outline-none font-bold text-slate-900 placeholder-slate-400 font-mono" />
                </div>

                <div>
                  <label class="block text-sm font-bold text-slate-700 mb-1.5">رقم هاتف مقدم الرعاية </label>
                  <input v-model="form.caregiver_phone_number" type="text" placeholder="مثال: 218900000000+" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 focus:border-teal-500 outline-none font-bold text-slate-900 placeholder-slate-400 font-mono" />
                </div>

                <div>
                  <label class="block text-sm font-bold text-slate-700 mb-1.5">كلمة المرور للدخول <span class="text-rose-500">*</span></label>
                  <input v-model="form.caregiver_password" type="password" required placeholder="••••••••" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 focus:border-teal-500 outline-none font-bold text-slate-900" />
                </div>
              </div>
            </div>
          </div>

          <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">
            * سيتم تعيين حسابك الحالي كـ "طبيب معالج مسؤول" عن الحالة تلقائياً، وسيتم تأسيس قنوات الحساسات الـ 8 وبث قراءاتها المباشرة فور الحفظ.
          </p>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import api from '../api'

const router = useRouter()

const caregivers = ref([])
const loading = ref(false)

const form = ref({
  full_name: '',
  date_of_birth: '',
  gender: 'M',
  element_type: 'patient',
  caregiver_option: 'none',
  existing_caregiver_id: null,
  caregiver_full_name: '',
  caregiver_username: '',
  caregiver_password: '',
  caregiver_phone_number: '' 
})

const medicalHistoryFlags = ref({
  heart_disease: false,
  chronic_conditions: false
})

const fetchCaregivers = async () => {
  try {
    const res = await api.get('/api/caregivers/')
    caregivers.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    if (caregivers.value.length > 0) {
      form.value.existing_caregiver_id = caregivers.value[0].id
    }
  } catch (e) {
    console.error('فشل جلب قائمة مقدمي الرعاية:', e)
  }
}

const discardChanges = () => {
  if (confirm('هل أنت متأكد من إلغاء الإسكان والعودة للوحة المراقبة؟')) {
    router.push('/dashboard')
  }
}

const submitPatientForm = async () => {
  if (!form.value.full_name || !form.value.date_of_birth) {
    alert('يرجى إدخال البيانات الأساسية للمريض أولاً')
    return
  }

  try {
    const chronic_conditions = []
    if (medicalHistoryFlags.value.heart_disease) {
      chronic_conditions.push({ name: 'heart_disease' })
    }
    if (medicalHistoryFlags.value.chronic_conditions) {
      chronic_conditions.push({ name: 'diabetes' })
    }

    const payload = {
      full_name: form.value.full_name,
      date_of_birth: form.value.date_of_birth,
      gender: form.value.gender,
      element_type: form.value.element_type,
      chronic_conditions: chronic_conditions,
      caregiver_option: form.value.caregiver_option,
      existing_caregiver_id: form.value.existing_caregiver_id,
      caregiver_full_name: form.value.caregiver_full_name,
      caregiver_username: form.value.caregiver_username,
      caregiver_password: form.value.caregiver_password,
      caregiver_phone_number: form.value.caregiver_phone_number 
    }

    await api.post('/api/monitored-elements/', payload)
    alert('تم تسجيل المريض بنجاح، وتأسيس الحساسات الـ 8 حياً في قاعدة البيانات!')
    router.push('/dashboard')
  } catch (e) {
    console.error('فشل تسجيل المريض وتأسيس الحساسات:', e)
    alert('فشل تسجيل المريض، يرجى التأكد من عدم تكرار اسم مستخدم مقدم الرعاية')
  }
}

onMounted(() => {
  fetchCaregivers()
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #0d9488;
}
</style>