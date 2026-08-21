<!-- DoctorManagement.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'">
    
    <!-- هيدر الشاشة البارز بتدرج تركوازي داكن -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <Shield :size="16" class="text-teal-300" />
          <span class="text-xs text-teal-200 font-mono font-extrabold uppercase tracking-wider">لوحة الإدارة الطبية</span>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">سجل الأطباء والكادر الطبي والمعالج</h1>
        <p class="text-xs text-teal-200/70 mt-1">عرض السجلات الطبية للأطباء والمدراء ومتابعة أعداد المرضى وإدارة وتعديل الحسابات</p>
      </div>

      <!-- زر إضافة حساب جديد (للمدير فقط) -->
      <button 
        v-if="currentUserIsAdmin"
        @click="openAddModal" 
        class="bg-teal-500/20 hover:bg-teal-500/30 text-teal-200 border border-teal-400/20 font-bold text-xs px-5 py-3 rounded-2xl backdrop-blur-sm transition-all flex items-center gap-2 shadow-lg shadow-teal-900/10"
      >
        <Plus :size="16" stroke-width="2.5" />
        <span>إضافة طبيب معالج جديد</span>
      </button>
    </header>

    <!-- البطاقات الإحصائية المصغرة (فاتحة) -->
    <section class="grid grid-cols-1 sm:grid-cols-3 gap-5">
      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs text-slate-400 font-bold uppercase">إجمالي الكادر والمدراء</p>
          <p class="text-2xl font-black text-slate-800 font-mono mt-1">{{ doctors.length }}</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center">
          <Users :size="24" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs text-slate-400 font-bold uppercase">الحسابات النشطة حالياً</p>
          <p class="text-2xl font-black text-emerald-600 font-mono mt-1">{{ activeDoctorsCount }}</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
          <CheckCircle :size="24" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs text-slate-400 font-bold uppercase">إجمالي المرضى المتابَعين</p>
          <p class="text-2xl font-black text-sky-600 font-mono mt-1">{{ totalManagedPatients }}</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center">
          <HeartPulse :size="24" />
        </div>
      </div>
    </section>

    <!-- 🟢 جدول سجلات الأطباء مع تصميم داكن لرأس الجدول -->
    <main class="w-full bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div v-if="loading" class="w-full text-center py-12">
        <span class="text-sm font-bold text-slate-400 animate-pulse">جاري تحميل السجلات...</span>
      </div>

      <div v-else-if="doctors.length === 0" class="w-full text-center py-12 p-6">
        <p class="text-sm text-slate-500 font-bold">لا يوجد أطباء مسجلون في النظام حالياً.</p>
      </div>

      <div v-else class="w-full overflow-x-auto">
        <table class="w-full text-right border-collapse text-xs">
          <thead>
            <tr class="bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white font-extrabold select-none">
              <th class="p-4 pr-6">الاسم واللقب الطبي</th>
              <th class="p-4">اسم المستخدم</th>
              <th class="p-4">رقم الهاتف</th>
              <th class="p-4 text-center">الدور والصلاحية</th>
              <th class="p-4 text-center">المرضى المتابَعون</th>
              <th class="p-4 text-center">حالة الحساب</th>
              <!-- عمود الإجراءات يظهر فقط للمدير -->
              <th v-if="currentUserIsAdmin" class="p-4 text-left pl-6">الإجراءات</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr 
              v-for="doc in doctors" 
              :key="doc.id" 
              class="hover:bg-slate-50/50 transition-colors group"
            >
              <!-- الطبيب واللقب مع أيقونة الدور -->
              <td class="p-4 pr-6">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center shadow-inner flex-shrink-0">
                    <component :is="getDoctorRoleIcon(doc)" :size="18" stroke-width="2" />
                  </div>
                  <div>
                    <p class="font-extrabold text-slate-800 text-sm">{{ doc.full_name || doc.username }}</p>
                    <p class="text-[10px] text-slate-400 font-medium">
                      {{ doc.role === 'admin' || doc.is_superuser ? 'مدير النظام  ' : 'طبيب معالج ' }}
                    </p>
                  </div>
                </div>
              </td>

              <!-- اسم المستخدم -->
              <td class="p-4 font-mono font-bold text-slate-700">
                @{{ doc.username }}
              </td>

              <!-- رقم الهاتف -->
              <td class="p-4 font-mono font-bold text-slate-700">
                {{ doc.phone_number || 'غير مضاف' }}
              </td>

              <!-- الدور والصلاحية (نص حر) -->
              <td class="p-4 text-center font-bold text-slate-700">
                {{ doc.role === 'admin' || doc.is_superuser ? 'مدير نظام' : 'طبيب معالج' }}
              </td>

              <!-- عدد المرضى المتابعين (نص حر) -->
              <td class="p-4 text-center font-bold text-slate-700">
                {{ doc.assigned_patients_count || 0 }} 
              </td>

              <!-- حالة الحساب (نص ملون فقط) -->
              <td class="p-4 text-center font-bold">
                <span :class="doc.is_active !== false ? 'text-emerald-600' : 'text-rose-500'">
                  {{ doc.is_active !== false ? 'نشط' : 'موقف' }}
                </span>
              </td>

              <!-- أزرار الإجراءات تظهر فقط للمدير -->
              <td v-if="currentUserIsAdmin" class="p-4 text-left pl-6">
                <div class="flex items-center justify-end gap-1.5">
                  <button 
                    @click="openEditModal(doc)" 
                    class="p-2 rounded-lg bg-sky-50 hover:bg-sky-100 border border-sky-200 text-sky-600 transition-all"
                    title="تعديل البيانات"
                  >
                    <Pencil :size="14" stroke-width="2" />
                  </button>

                  <button 
                    @click="toggleDoctorStatus(doc)" 
                    class="p-2 rounded-lg border transition-all"
                    :class="doc.is_active !== false ? 'bg-amber-50 hover:bg-amber-100 border-amber-200 text-amber-600' : 'bg-emerald-50 hover:bg-emerald-100 border-emerald-200 text-emerald-600'"
                    :title="doc.is_active !== false ? 'تجميد الحساب' : 'تفعيل الحساب'"
                  >
                    <ToggleLeft v-if="doc.is_active !== false" :size="14" stroke-width="2" />
                    <ToggleRight v-else :size="14" stroke-width="2" />
                  </button>

                  <button 
                    @click="deleteDoctor(doc.id)" 
                    class="p-2 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-600 transition-all"
                    title="حذف الحساب"
                  >
                    <Trash2 :size="14" stroke-width="2" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- 1. النافذة المنبثقة لإضافة حساب جديد (داكنة) -->
    <Teleport to="body">
      <div v-if="showAddModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl w-full max-w-lg p-6 space-y-5 text-cyan-100" :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'">
          <div class="flex items-center justify-between border-b border-slate-700 pb-3">
            <h3 class="text-lg font-extrabold text-white">إضافة طبيب معالج جديد</h3>
            <button @click="closeAddModal" class="text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/5">
              <X :size="18" />
            </button>
          </div>

          <form @submit.prevent="submitDoctorForm" class="space-y-4 text-xs">
            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">الاسم واللقب الطبي</label>
              <input 
                v-model="addForm.full_name" 
                type="text" 
                required 
                placeholder="مثال: د. أحمد الفيتوري" 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200 placeholder-slate-500" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">اسم المستخدم</label>
              <input 
                v-model="addForm.username" 
                type="text" 
                required 
                placeholder="dr_ahmed" 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200 font-mono placeholder-slate-500" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">الدور والصلاحيات</label>
              <select v-model="addForm.role" class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-200">
                <option value="doctor">طبيب معالج</option>
                <option value="admin">مدير نظام</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">رقم هاتف الاتصال</label>
              <input 
                v-model="addForm.phone_number" 
                type="text" 
                placeholder="+218900000000" 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200 font-mono placeholder-slate-500" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">كلمة المرور الأوليّة</label>
              <input 
                v-model="addForm.password" 
                type="password" 
                required 
                placeholder="••••••••" 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200" 
              />
            </div>

            <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-700">
              <button type="button" @click="closeAddModal" class="px-4 py-2.5 rounded-xl text-slate-400 font-bold hover:bg-slate-800 transition-colors">إلغاء</button>
              <button type="submit" class="bg-teal-600 hover:bg-teal-500 text-white font-bold px-5 py-2.5 rounded-xl transition-colors">حفظ وإنشاء الحساب</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- 2. النافذة المنبثقة لتعديل البيانات (داكنة) -->
    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl w-full max-w-lg p-6 space-y-5 text-cyan-100" :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'">
          <div class="flex items-center justify-between border-b border-slate-700 pb-3">
            <h3 class="text-lg font-extrabold text-white">تعديل بيانات الحساب</h3>
            <button @click="closeEditModal" class="text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/5">
              <X :size="18" />
            </button>
          </div>

          <form @submit.prevent="submitEditDoctorForm" class="space-y-4 text-xs">
            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">الاسم واللقب الطبي</label>
              <input 
                v-model="editForm.full_name" 
                type="text" 
                required 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">اسم المستخدم</label>
              <input 
                v-model="editForm.username" 
                type="text" 
                required 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200 font-mono" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">الدور والصلاحية</label>
              <select v-model="editForm.role" class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-200">
                <option value="doctor">طبيب معالج</option>
                <option value="admin">مدير نظام</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">رقم هاتف الاتصال</label>
              <input 
                v-model="editForm.phone_number" 
                type="text" 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200 font-mono" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-cyan-200/80 mb-1.5">كلمة المرور <span class="text-slate-400 font-normal">(اتركها فارغة إن لم ترد تغييرها)</span></label>
              <input 
                v-model="editForm.password" 
                type="password" 
                placeholder="••••••••" 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-bold text-slate-200" 
              />
            </div>

            <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-700">
              <button type="button" @click="closeEditModal" class="px-4 py-2.5 rounded-xl text-slate-400 font-bold hover:bg-slate-800 transition-colors">إلغاء</button>
              <button type="submit" class="bg-sky-600 hover:bg-sky-500 text-white font-bold px-5 py-2.5 rounded-xl transition-colors">تحديث وحفظ</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import { 
  Shield, Plus, Users, CheckCircle, HeartPulse, 
  Pencil, ToggleLeft, ToggleRight, Trash2, X,
  Stethoscope
} from 'lucide-vue-next'

const { t } = useI18n()

const doctors = ref([])
const loading = ref(true)
const showAddModal = ref(false)
const showEditModal = ref(false)

const addForm = ref({
  full_name: '',
  username: '',
  phone_number: '',
  password: '',
  role: 'doctor'
})

const editForm = ref({
  id: null,
  full_name: '',
  username: '',
  phone_number: '',
  role: 'doctor',
  password: ''
})

// --- صلاحية المدير ---
const currentUserIsAdmin = computed(() => {
  const role = localStorage.getItem('user_role')
  const superuser = localStorage.getItem('is_superuser') === 'true'
  return role === 'admin' || superuser === true
})

const activeDoctorsCount = computed(() => {
  return doctors.value.filter(d => d.is_active !== false).length
})

const totalManagedPatients = computed(() => {
  return doctors.value.reduce((acc, d) => acc + (d.assigned_patients_count || 0), 0)
})

const getDoctorRoleIcon = (doc) => {
  if (doc.role === 'admin' || doc.is_superuser) return Shield
  if (doc.role === 'doctor') return Stethoscope
  if (doc.role === 'caregiver' || doc.role === 'nurse') return HeartPulse
  return Users
}

const fetchDoctors = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/doctors/')
    doctors.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('فشل جلب قائمة الأطباء:', e)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  addForm.value = { full_name: '', username: '', phone_number: '', password: '', role: 'doctor' }
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
}

const submitDoctorForm = async () => {
  try {
    await api.post('/api/doctors/', addForm.value)
    closeAddModal()
    fetchDoctors()
  } catch (e) {
    console.error('فشل إضافة الطبيب:', e)
    alert('فشل إضافة الطبيب، يرجى التأكد من عدم تكرار اسم المستخدم')
  }
}

const openEditModal = (doc) => {
  editForm.value = {
    id: doc.id,
    full_name: doc.full_name || '',
    username: doc.username || '',
    phone_number: doc.phone_number || '',
    role: doc.role || 'doctor',
    password: ''
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const submitEditDoctorForm = async () => {
  try {
    const payload = { ...editForm.value }
    if (!payload.password) delete payload.password 

    await api.patch(`/api/doctors/${editForm.value.id}/`, payload)
    closeEditModal()
    fetchDoctors()
  } catch (e) {
    console.error('فشل تعديل البيانات:', e)
    alert('فشل تعديل البيانات، يرجى التأكد من عدم تكرار اسم المستخدم')
  }
}

const toggleDoctorStatus = async (doc) => {
  try {
    await api.patch(`/api/doctors/${doc.id}/`, { is_active: !doc.is_active })
    fetchDoctors()
  } catch (e) {
    console.error('فشل تغيير حالة الطبيب:', e)
  }
}

const deleteDoctor = async (id) => {
  if (!confirm('هل أنت متأكد من رغبتك في حذف هذا الحساب؟')) return
  try {
    await api.delete(`/api/doctors/${id}/`)
    fetchDoctors()
  } catch (e) {
    console.error('فشل حذف الطبيب:', e)
  }
}

onMounted(() => {
  fetchDoctors()
})
</script>