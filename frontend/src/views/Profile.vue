<!-- Profile.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- هيدر الصفحة -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <Icon icon="mdi:account-cog-outline" class="w-4 h-4 text-teal-300" />
          <span class="text-xs text-teal-200 font-mono font-extrabold uppercase tracking-wider">سجل الحساب الشخصي</span>
          <span class="text-[10px] bg-teal-500/20 text-teal-200 px-2.5 py-0.5 rounded-full font-bold border border-teal-400/20">ملف الطبيب المعالج</span>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">إعدادات الملف الشخصي للاتصال</h1>
        <p class="text-xs text-teal-200/70 mt-1">تعديل بيانات الحساب، تخصصك الطبي، ومعاينة الحالات الحيوية المسندة لرقابتك</p>
      </div>
    </header>

    <!-- بطاقة تعريف المستخدم (داكنة) -->
    <div class="rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col items-center text-center gap-3 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white">
      <!-- الدائرة أصبحت بيضاء والأيقونة داكنة -->
      <div class="w-20 h-20 rounded-full bg-white text-[#0a3d48] flex items-center justify-center shadow-lg">
        <Icon :icon="roleIcon" class="w-10 h-10" />
      </div>
      <div>
        <h2 class="text-lg font-black text-white">{{ displayName }}</h2>
        <p class="text-xs text-teal-200/70 font-mono font-bold mt-1">@{{ profile.username }}</p>
      </div>
      
      <span class="px-3 py-1 bg-teal-500/20 text-teal-200 border border-teal-400/30 rounded-full text-xs font-bold">
        {{ roleLabel }}
      </span>
    </div>

    <!-- تحديث البيانات الشخصية -->
    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white p-4 flex items-center gap-2">
        <Icon icon="mdi:account-edit-outline" class="w-5 h-5 text-teal-300" />
        <h3 class="font-extrabold text-sm">تحديث البيانات والملفات السريرية</h3>
      </div>
      
      <div class="p-6">
        <form @submit.prevent="updateProfile" class="space-y-4 text-xs">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">الاسم الأول</label>
              <input v-model="form.first_name" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 transition-all" />
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">اسم العائلة</label>
              <input v-model="form.last_name" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 transition-all" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-slate-700 mb-1.5">اسم المستخدم (Username) <span class="text-rose-500">*</span></label>
            <input v-model="form.username" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 font-mono" />
          </div>

          <div>
            <label class="block text-sm font-bold text-slate-700 mb-1.5">رقم هاتف الاتصال والـ SMS</label>
            <input 
              v-model="form.phone_number" 
              type="text" 
              placeholder="مثال: 218900000000+" 
              class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 font-mono placeholder-slate-400" 
            />
          </div>

          <div class="pt-3 border-t border-slate-100">
            <label class="block text-sm font-bold text-slate-700 mb-1.5">تغيير كلمة المرور <span class="text-slate-400 font-normal">(اتركها فارغة إذا لم ترد التغيير)</span></label>
            <input v-model="form.password" type="password" placeholder="أدخل كلمة مرور جديدة للاتصال" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900" />
          </div>

          <div class="pt-4 border-t border-slate-100 flex items-center justify-end">
            <button type="submit" class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-6 py-2.5 rounded-2xl shadow-sm hover:shadow transition-all">
              حفظ وتحديث البيانات الشخصية
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- الحالات المسندة -->
    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white p-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon icon="mdi:clipboard-list-outline" class="w-5 h-5 text-teal-300" />
          <h3 class="font-extrabold text-sm">الحالات المسندة لرقابتك</h3>
        </div>
        <span class="bg-teal-500/20 text-teal-200 font-mono text-xs font-black px-2.5 py-1 rounded-xl border border-teal-400/20">
          {{ profile.assigned_patients_count || 0 }} حالات نشطة
        </span>
      </div>
      
      <div class="p-6">
        <div v-if="loading" class="text-center py-6 text-xs text-slate-400 font-bold animate-pulse">
          جاري تحميل قائمة المرضى...
        </div>

        <div v-else-if="!profile.assigned_patients || profile.assigned_patients.length === 0" class="text-center py-6 text-xs text-slate-400 font-bold">
          لا توجد حالات مسندة لحسابك حالياً.
        </div>

        <div v-else class="space-y-2 overflow-y-auto custom-scrollbar max-h-[260px] pr-1">
          <div 
            v-for="pat in limitedAssignedPatients" 
            :key="pat.id" 
            class="flex items-center justify-between p-3 bg-slate-50 border border-slate-200/80 rounded-2xl hover:bg-slate-100/50 transition-colors"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-xl bg-white border border-slate-200 text-slate-500 flex items-center justify-center">
                <Icon icon="mdi:user" class="w-5 h-5 text-slate-500" />
              </div>
              <div>
                <h4 class="font-bold text-slate-800 text-xs">{{ pat.full_name }}</h4>
                <p class="text-[10px] text-slate-400 font-semibold">{{ getElementTypeArabic(pat.element_type) }} • {{ pat.age }} سنة</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDoctorStore } from '../stores/doctor'
import api from '../api'
import { Icon } from '@iconify/vue'

const doctorStore = useDoctorStore()
const { locale } = useI18n()

const profile = ref({})
const loading = ref(true)

const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  phone_number: '',
  password: ''
})

const roleLabel = computed(() => {
  if (profile.value.role === 'admin' || profile.value.is_superuser) return 'مدير نظام وطبيب مشرف'
  if (profile.value.role === 'doctor') return 'طبيب معالج - عناية مركزة'
  if (profile.value.role === 'caregiver' || profile.value.role === 'nurse') return 'مقدم رعاية صحية'
  return 'طبيب معالج'
})

// أيقونة الدور
const roleIcon = computed(() => {
  if (profile.value.role === 'admin' || profile.value.is_superuser) return 'eos-icons:admin'
  if (profile.value.role === 'doctor') return 'maki:doctor'
  if (profile.value.role === 'caregiver' || profile.value.role === 'nurse') return 'mdi:hand-heart'
  return 'mdi:account'
})

// عرض الاسم مع البادئة د. / Dr. حسب اللغة والدور
const displayName = computed(() => {
  const name = profile.value.full_name || 'طبيب'
  const role = profile.value.role || ''
  if (role === 'doctor') {
    return locale.value === 'ar' ? `د. ${name}` : `Dr. ${name}`
  }
  return name
})

const limitedAssignedPatients = computed(() => {
  const list = profile.value.assigned_patients || []
  return list.slice(0, 5)
})

const getElementTypeArabic = (type) => {
  if (type === 'patient') return 'مريض'
  if (type === 'elderly') return 'مسن رعاية'
  if (type === 'disabled') return 'احتياجات خاصة'
  return 'حالة تحت المراقبة'
}

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/user/profile/')
    profile.value = res.data
    
    form.value = {
      first_name: res.data.first_name || '',
      last_name: res.data.last_name || '',
      username: res.data.username || '',
      phone_number: res.data.phone_number || '',
      password: ''
    }

    if (res.data.full_name) {
      doctorStore.name = res.data.full_name
      localStorage.setItem('full_name', res.data.full_name)
    }
  } catch (e) {
    console.error('فشل استعادة البروفايل الشخصي:', e)
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  try {
    const payload = { ...form.value }
    if (!payload.password) delete payload.password 

    await api.patch(`/api/doctors/${profile.value.id}/`, payload)
    alert('تم تحديث وحفظ بيانات الملف الشخصي بنجاح!')
    fetchProfile()
  } catch (e) {
    console.error('فشل تعديل البروفايل:', e)
    alert('فشل التعديل، يرجى التأكد من عدم تكرار اسم المستخدم')
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(100, 116, 139, 0.3) transparent;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.3);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.5);
}
</style>