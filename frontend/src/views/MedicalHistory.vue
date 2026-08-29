<!-- MedicalHistory.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- 🟢 الترويسة العلوية باللون التركوازي الغامق الموحد لهوية نظام MediWatch -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white select-none shrink-0">
      <div class="flex items-center gap-3">
        <!-- أيقونة الملف الطبي الموحدة من إيكونيفاي داخل غلاف زجاجي ناعم -->
        <div class="w-10 h-10 shrink-0 rounded-xl bg-white/10 border border-white/5 flex items-center justify-center text-teal-300">
          <Icon icon="solar:document-text-bold" class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs text-teal-300 font-mono font-extrabold uppercase tracking-wider">سجل الملف الطبي</span>
            <span class="text-[10px] bg-white/10 text-teal-200 border border-white/5 px-2.5 py-0.5 rounded-full font-bold">صلاحيات الطبيب المعالج</span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold text-white tracking-tight">إدارة الملف الطبي للمريض: {{ patientName }}</h1>
          <p class="text-xs text-teal-200/70 mt-1 font-medium">تحديث البيانات الديموغرافية، التاريخ المرضي، إدارة مقدمي الرعاية، والتحكم بالقواعد السريرية الخاصة</p>
        </div>
      </div>

      <!-- أزرار الرجوع وحفظ التغييرات الشاملة للملف الشخصي والسريري بالهوية الزجاجية المتناسقة -->
      <div class="flex items-center gap-2.5 w-full sm:w-auto justify-end select-none">
        <button 
          @click="router.push('/dashboard')" 
          class="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-bold text-xs backdrop-blur-sm transition-all cursor-pointer"
        >
          لوحة المراقبة
        </button>
        <button 
          @click="saveAllChanges" 
          class="bg-teal-500/20 hover:bg-teal-500/30 text-teal-200 border border-teal-400/20 font-bold text-xs px-6 py-2.5 rounded-xl backdrop-blur-sm transition-all shadow-lg shadow-teal-900/10 cursor-pointer"
        >
          حفظ التغييرات السريرية
        </button>
      </div>
    </header>

    <!-- الهيكل المنظم للملف الطبي -->
    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start w-full">
      
      <!-- العمود الأيمن: السوابق الطبية وإدارة كادر مقدمي الرعاية -->
      <div class="lg:col-span-5 flex flex-col gap-6">
        
        <!-- 🟢 1. البيانات الديموغرافية الأساسية للمريض (ترويسة تركوازية وأيقونة بيضاء مقابلة لليسار) -->
        <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">1</span>
              <span class="font-extrabold text-white text-xs">البيانات الديموغرافية الأساسية للمريض</span>
            </div>
            <Icon icon="solar:user-bold" class="w-5 h-5 text-white shrink-0" />
          </div>

          <div class="p-6 space-y-3.5 text-xs">
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">الاسم الكامل للمريض <span class="text-rose-500">*</span></label>
              <input 
                v-model="patientForm.full_name" 
                type="text" 
                required 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">تاريخ الميلاد <span class="text-rose-500">*</span></label>
              <input 
                v-model="patientForm.date_of_birth" 
                type="date" 
                required 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900" 
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-1.5">الجنس <span class="text-rose-500">*</span></label>
                <select v-model="patientForm.gender" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 outline-none font-bold text-slate-900">
                  <option value="M">ذكر (Male)</option>
                  <option value="F">أنثى (Female)</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-bold text-slate-700 mb-1.5">تصنيف الحالة</label>
                <select v-model="patientForm.element_type" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 outline-none font-bold text-slate-900">
                  <option value="patient">مريض (Patient)</option>
                  <option value="elderly">مسن رعاية (Elderly)</option>
                  <option value="disabled">احتياجات خاصة (Disabled)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 🟢 2. بطاقة السوابق الطبية والأمراض المزمنة (ترويسة تركوازية وأيقونة بيضاء مقابلة لليسار) -->
        <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">2</span>
              <span class="font-extrabold text-white text-xs">التاريخ الطبي والمزمن الفعلي للمريض</span>
            </div>
            <Icon icon="solar:notes-bold" class="w-5 h-5 text-white shrink-0" />
          </div>

          <div class="p-6 space-y-3">
            <label class="flex items-start gap-3 bg-slate-50/50 p-4 border border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-colors">
              <input type="checkbox" v-model="medicalHistoryFlags.heart_disease" class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4 mt-0.5 cursor-pointer" />
              <div>
                <p class="text-sm font-bold text-slate-750">التاريخ المرضي لأمراض القلب (Heart Disease)</p>
                <p class="text-[10px] text-slate-400 mt-0.5 font-medium">قصور القلب، احتشاء عضلة القلب، أو الذبحة الصدرية السابقة</p>
              </div>
            </label>

            <label class="flex items-start gap-3 bg-slate-50/50 p-4 border border-slate-200 rounded-2xl cursor-pointer hover:bg-slate-50 transition-colors">
              <input type="checkbox" v-model="medicalHistoryFlags.chronic_conditions" class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4 mt-0.5 cursor-pointer" />
              <div>
                <p class="text-xs font-bold text-slate-750">الإصابة بأمراض مزمنة عامة (Chronic Conditions)</p>
                <p class="text-[10px] text-slate-400 mt-0.5 font-medium">داء السكري (Type 2 Diabetes)، أو ارتفاع ضغط الدم (Hypertension)</p>
              </div>
            </label>
          </div>
        </div>

        <!-- 🟢 3. بطاقة إدارة الكادر لمقدمي الرعاية (ترويسة تركوازية وزر الإضافة وأيقونة العائلة على اليسار المقابل) -->
        <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">3</span>
              <span class="font-extrabold text-white text-xs">مقدمو الرعاية المتابعون للحالة</span>
            </div>
            <!-- زر الإسناد وأيقونة العائلة على اليسار المقابل تماماً -->
            <div class="flex items-center gap-3 select-none">
              <button 
                @click="openAssignCaregiverModal" 
                class="text-[9px] font-bold text-teal-200 bg-white/10 hover:bg-white/20 border border-white/10 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer"
              >
                + إسناد مقدم رعاية
              </button>
              <Icon icon="solar:users-group-rounded-bold" class="w-5 h-5 text-white shrink-0" />
            </div>
          </div>

          <div class="p-6 space-y-4">
            <div v-if="loadingCaregivers" class="text-center py-6 text-xs text-slate-400 font-bold animate-pulse">
              جاري تحميل كادر مقدمي الرعاية...
            </div>

            <div v-else-if="assignedCaregivers.length === 0" class="text-center py-6 text-xs text-slate-400 font-bold border border-dashed border-slate-200 rounded-2xl select-none">
              لا يوجد مقدمو رعاية مسندون لمتابعة هذا المريض حالياً.
            </div>

            <!-- جدول السجلات لمقدمي الرعاية المتابعين -->
            <div v-else class="w-full overflow-hidden border border-slate-200 rounded-2xl select-none">
              <table class="w-full text-right border-collapse text-[11px]">
                <thead class="bg-slate-50 border-b border-slate-200">
                  <tr class="text-slate-500 font-bold">
                    <th class="p-2.5 pr-4">الاسم</th>
                    <th class="p-2.5">اسم المستخدم</th> 
                    <th class="p-2.5">رقم الهاتف</th>
                    <th class="p-2.5 text-left pl-4">الإجراءات</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="care in assignedCaregivers" :key="care.id" class="hover:bg-slate-50/50">
                    <td class="p-2.5 pr-4 font-bold text-slate-800">{{ care.full_name }}</td>
                    <td class="p-2.5 font-mono text-slate-500 font-bold">@{{ care.username }}</td> 
                    <td class="p-2.5 font-mono text-slate-600 font-bold">{{ care.phone_number || 'غير مضاف' }}</td>
                    <td class="p-2.5 text-left pl-4">
                      <div class="flex items-center justify-end gap-1.5">
                        <button @click="openEditCaregiverModal(care)" class="text-[9px] font-bold text-sky-700 bg-sky-50 border border-sky-100 px-2.5 py-1 rounded-lg cursor-pointer">تعديل</button>
                        <button @click="removeCaregiver(care.id)" class="text-[9px] font-bold text-rose-600 bg-rose-50 border border-rose-100 px-2.5 py-1 rounded-lg cursor-pointer">حذف</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- العمود الأيسر: 4. القواعد والبروتوكولات السريرية الخاصة والمخصصة للمريض حصراً (ترويسة تركوازية وأيقونة بيضاء وزر الإضافة على اليسار) -->
      <div class="lg:col-span-7 bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
        <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
          <div class="flex items-center gap-2">
            <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">4</span>
            <span class="font-extrabold text-white text-xs">البروتوكولات السريرية الخاصة بالمريض</span>
          </div>
          <!-- زر باني القواعد وأيقونة التحكم على اليسار المقابل تماماً للعنوان -->
          <div class="flex items-center gap-3 select-none">
            <button 
              @click="router.push(`/patients/${patientId}/rules/new`)" 
              class="text-[9px] font-bold text-teal-200 bg-white/10 hover:bg-white/20 border border-white/10 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              + إضافة قاعدة فسيولوجية مخصصة
            </button>
            <Icon icon="solar:tuning-2-bold" class="w-5 h-5 text-white shrink-0" />
          </div>
        </div>

        <div class="p-6 flex-1 flex flex-col gap-4">
          <div v-if="loadingRules" class="text-center py-6 text-xs text-slate-400 font-bold animate-pulse">
            جاري جلب القواعد المخصصة للمريض...
          </div>

          <div v-else-if="customRules.length === 0" class="text-center py-12 text-xs text-slate-400 font-bold border border-dashed border-slate-200 rounded-3xl select-none">
            لا توجد قواعد مخصصة مضافة لهذا المريض حالياً، يطبق النظام البروتوكولات العامة للمستشفى فقط.
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="rule in customRules" 
              :key="rule.id" 
              class="p-4 bg-slate-50/50 border border-slate-200 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div>
                <div class="flex items-center gap-2 mb-1.5">
                  <span class="text-[10px] bg-rose-50 text-rose-700 font-extrabold px-2.5 py-0.5 rounded-full border border-rose-200 font-mono">
                    {{ rule.severity }}
                  </span>
                  <h4 class="font-extrabold text-slate-800 text-xs">{{ rule.name }}</h4>
                </div>
                <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">التوصية: {{ rule.action_template }}</p>
              </div>

              <!-- أزرار الإجراءات الخاصة بقاعدة المريض الفردي -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <button 
                  @click="router.push(`/patients/${patientId}/rules/edit/${rule.id}`)"
                  class="text-[11px] font-bold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 px-3 py-1.5 rounded-xl transition-all cursor-pointer"
                >
                  تعديل
                </button>
                <button 
                  @click="deleteCustomRule(rule.id)"
                  class="text-[11px] font-bold text-rose-600 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-3 py-1.5 rounded-xl transition-all cursor-pointer"
                >
                  حذف
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- منبثقة إسناد أو إنشاء حساب مقدم رعاية معتمد -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-55 flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl border border-slate-200 shadow-xl w-full max-w-md p-6 space-y-4" dir="rtl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="text-sm font-extrabold text-slate-800">إسناد أو إنشاء حساب مقدم رعاية للمريض</h3>
          <button @click="showAssignModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl cursor-pointer">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-slate-600 mb-1.5">خيارات مقدم الرعاية</label>
            <select v-model="caregiverForm.option" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900 cursor-pointer">
              <option value="existing">اختيار مقدم رعاية مسجّل مسبقاً</option>
              <option value="new">إنشاء حساب جديد كلياً لمقدم الرعاية</option>
            </select>
          </div>

          <!-- أ. في حال اختيار مقدم رعاية مسجل مسبقاً -->
          <div v-if="caregiverForm.option === 'existing'" class="space-y-2">
            <label class="block font-bold text-slate-600 mb-1">اختر مقدم الرعاية من القائمة</label>
            <select v-model="caregiverForm.existing_id" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900 cursor-pointer">
              <option v-for="care in allCaregivers" :key="care.id" :value="care.id">
                {{ care.full_name }} (@{{ care.username }})
              </option>
            </select>
          </div>

          <!-- ب. في حال إنشاء حساب جديد لمقدم الرعاية -->
          <div v-if="caregiverForm.option === 'new'" class="space-y-3 p-3 bg-slate-50 rounded-2xl border border-slate-100">
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">الاسم الكامل لمقدم الرعاية</label>
              <input v-model="caregiverForm.full_name" type="text" required class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">اسم المستخدم (Username)</label>
              <input v-model="caregiverForm.username" type="text" required class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold font-mono text-slate-900" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">رقم هاتف مقدم الرعاية</label>
              <input v-model="caregiverForm.phone_number" type="text" placeholder="+218900000000" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold font-mono text-slate-900" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">كلمة المرور</label>
              <input v-model="caregiverForm.password" type="password" required placeholder="••••••••" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900" />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="showAssignModal = false" class="px-4 py-2 rounded-xl text-slate-500 font-bold hover:bg-slate-100 cursor-pointer">إلغاء</button>
            <button @click="submitAssignCaregiver" class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-5 py-2 rounded-xl shadow-xs cursor-pointer">حفظ وإسناد مقدم الرعاية</button>
          </div>
        </div>
      </div>
    </div>

    <!-- منبثقة تعديل بيانات مقدم الرعاية (Edit Caregiver Modal) -->
    <div v-if="showEditCaregiverModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-55 flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl border border-slate-200 shadow-xl w-full max-w-md p-6 space-y-4" dir="rtl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="text-sm font-extrabold text-slate-800">تعديل بيانات حساب مقدم الرعاية</h3>
          <button @click="showEditCaregiverModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl cursor-pointer">✕</button>
        </div>

        <form @submit.prevent="submitEditCaregiver" class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-slate-600 mb-1">الاسم الكامل لمقدم الرعاية</label>
            <input v-model="editCaregiverForm.full_name" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900" />
          </div>
          <div>
            <label class="block font-bold text-slate-600 mb-1">اسم المستخدم (Username)</label>
            <input v-model="editCaregiverForm.username" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 font-mono" />
          </div>
          <div>
            <label class="block font-bold text-slate-600 mb-1">رقم الهاتف للتواصل والـ SMS</label>
            <input v-model="editCaregiverForm.phone_number" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 font-mono" />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="showEditCaregiverModal = false" class="px-4 py-2 rounded-xl text-slate-500 font-bold hover:bg-slate-100 cursor-pointer">إلغاء</button>
            <button type="submit" class="bg-sky-600 hover:bg-sky-700 text-white font-bold px-5 py-2 rounded-xl shadow-xs cursor-pointer">حفظ التعديلات</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue' // 🟢 دمج مستورد الأيقونة الفردي والمثالي لمنع التكرار والكراش
import api from '../api'

const router = useRouter()
const route = useRoute()
const patientId = ref(route.params.id)

const patientName = ref('المريض')
const patientData = ref({})
const loading = ref(true)
const loadingRules = ref(true)
const loadingCaregivers = ref(true)

const assignedCaregivers = ref([])
const allCaregivers = ref([])
const showAssignModal = ref(false)
const showEditCaregiverModal = ref(false)

// استمارة بيانات المريض الشخصية الأساسية القابلة للتعديل والتحكم بالكامل
const patientForm = ref({
  full_name: '',
  date_of_birth: '',
  gender: 'M',
  element_type: 'patient'
})

const caregiverForm = ref({
  option: 'existing',
  existing_id: null,
  full_name: '',
  username: '',
  phone_number: '',
  password: ''
})

const editCaregiverForm = ref({ id: null, full_name: '', username: '', phone_number: '' })
const customRules = ref([])

const medicalHistoryFlags = ref({
  heart_disease: false,
  chronic_conditions: false
})

const patientInitials = computed(() => {
  const name = patientName.value
  const parts = name.trim().split(' ')
  if (parts.length >= 2 && parts[1].length > 0) return parts[0][0] + parts[1][0]
  return name.substring(0, 2)
})

const fetchPatientDetails = async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/monitored-elements/${patientId.value}/`)
    patientData.value = res.data
    patientName.value = res.data.full_name

    // تعبئة حقول تعديل البيانات الأساسية لـ patientForm بدقة
    patientForm.value = {
      full_name: res.data.full_name || '',
      date_of_birth: res.data.date_of_birth || '',
      gender: res.data.gender || 'M',
      element_type: res.data.element_type || 'patient'
    }

    // استرداد السجل الطبي الفعلي
    const medRes = await api.get('/api/medical-histories/', {
      params: { monitored_element: patientId.value }
    })
    const history = medRes.data?.[0] || (medRes.data.results?.[0])
    
    if (history) {
      const conditions = history.chronic_conditions || []
      
      // دالة الخيارات الطبية الفسلوجية المقاومة للأخطاء
      const condNames = conditions.map(c => {
        if (typeof c === 'string') return c.toLowerCase()
        if (c && typeof c === 'object') return (c.name || '').toLowerCase()
        return ''
      })
      
      medicalHistoryFlags.value = {
        heart_disease: condNames.includes('heart_disease'),
        chronic_conditions: condNames.includes('diabetes')
      }
    }
  } catch (e) {
    console.error('فشل استعادة السجل الطبي وتفاصيل المريض:', e)
  } finally {
    loading.value = false
  }
}

// جلب مقدمي الرعاية المسندين للمريض حالياً عبر الـ ManyToMany
const fetchAssignedCaregivers = async () => {
  loadingCaregivers.value = true
  try {
    const res = await api.get('/api/caregivers/', {
      params: { monitored_element: patientId.value }
    })
    assignedCaregivers.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('فشل جلب مقدمي الرعاية المسندين:', e)
  } finally {
    loadingCaregivers.value = false
  }
}

const fetchAllCaregiversList = async () => {
  try {
    const res = await api.get('/api/caregivers/')
    allCaregivers.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    if (allCaregivers.value.length > 0) {
      caregiverForm.value.existing_id = allCaregivers.value[0].id
    }
  } catch (e) {
    console.error('فشل جلب قائمة كافة مقدمي الرعاية:', e)
  }
}

// جلب القواعد المخصصة والخاصة بهذا المريض حصراً
const fetchCustomRules = async () => {
  loadingRules.value = true
  try {
    const res = await api.get('/api/rules/', {
      params: { monitored_element: patientId.value }
    })
    const allRules = Array.isArray(res.data) ? res.data : (res.data.results || [])
    customRules.value = allRules.filter(r => r.monitored_element === Number(patientId.value))
  } catch (e) {
    console.error('فشل جلب القواعد المخصصة للمريض:', e)
  } finally {
    loadingRules.value = false
  }
}

const openAssignCaregiverModal = async () => {
  caregiverForm.value = { option: 'existing', existing_id: null, full_name: '', username: '', phone_number: '', password: '' }
  await fetchAllCaregiversList()
  showAssignModal.value = true
}

// إسناد مقدم الرعاية الجديد أو المسجل مسبقاً
const submitAssignCaregiver = async () => {
  try {
    if (caregiverForm.value.option === 'new') {
      // أ. إنشاء حساب جديد لمقدم الرعاية وربطه بالمريض تلقائياً في الـ ManyToMany بالباك إند
      await api.post('/api/caregivers/', {
        username: caregiverForm.value.username,
        password: caregiverForm.value.password,
        full_name: caregiverForm.value.full_name,
        phone_number: caregiverForm.value.phone_number,
        monitored_element: patientId.value
      })
    } else {
      // ب. تجميع المعرفات الحالية وإلحاق المعرف الجديد وتحديث حقل الـ ManyToMany بـ PATCH
      const currentIds = assignedCaregivers.value.map(c => c.id)
      const newId = caregiverForm.value.existing_id
      
      if (newId && !currentIds.includes(newId)) {
        currentIds.push(newId)
      }

      await api.patch(`/api/monitored-elements/${patientId.value}/`, {
        caregivers: currentIds
      })
    }

    showAssignModal.value = false
    alert('تم إسناد وربط مقدم الرعاية للحالة بنجاح!')
    await fetchPatientDetails()
    await fetchAssignedCaregivers()
  } catch (e) {
    console.error('فشل إسناد مقدم الرعاية المعدد:', e)
    alert('تعذر إتمام العملية، يرجى التأكد من عدم تكرار اسم مستخدم مقدم الرعاية')
  }
}

// فتح نافذة تعديل بيانات مقدم الرعاية
const openEditCaregiverModal = (care) => {
  editCaregiverForm.value = {
    id: care.id,
    full_name: care.full_name || '',
    username: care.username || '',
    phone_number: care.phone_number || ''
  }
  showEditCaregiverModal.value = true
}

const submitEditCaregiver = async () => {
  try {
    await api.patch(`/api/caregivers/${editCaregiverForm.value.id}/`, {
      full_name: editCaregiverForm.value.full_name,
      username: editCaregiverForm.value.username,
      phone_number: editCaregiverForm.value.phone_number
    })
    showEditCaregiverModal.value = false
    alert('تم تحديث بيانات حساب مقدم الرعاية بنجاح!')
    await fetchAssignedCaregivers()
  } catch (e) {
    console.error('فشل تعديل بيانات مقدم الرعاية:', e)
  }
}

// فك ارتباط مقدم الرعاية عن المريض عبر الـ ManyToMany بـ PATCH
const removeCaregiver = async (caregiverId) => {
  if (!confirm('هل أنت متأكد من فك ارتباط وإلغاء إسناد مقدم الرعاية عن المريض؟')) return
  try {
    const remainingIds = assignedCaregivers.value
      .map(c => c.id)
      .filter(id => id !== caregiverId)

    await api.patch(`/api/monitored-elements/${patientId.value}/`, {
      caregivers: remainingIds
    })

    alert('تم إلغاء إسناد وفك ارتباط مقدم الرعاية عن المريض.')
    await fetchPatientDetails()
    await fetchAssignedCaregivers()
  } catch (e) {
    console.error('فشل إلغاء إسناد مقدم الرعاية المعدد:', e)
  }
}

const deleteCustomRule = async (id) => {
  if (!confirm('هل أنت متأكد من رغبتك في حذف هذا البروتوكول المخصص للمريض؟')) return
  try {
    await api.delete(`/api/rules/${id}/`)
    fetchCustomRules()
  } catch (e) {
    console.error('فشل حذف القاعدة المخصصة:', e)
  }
}

// الحفظ المشترك والمزدوج لكافة التعديلات الشخصية والسريرية معاً
const saveAllChanges = async () => {
  try {
    // 1. تحديث وحفظ بيانات المريض الشخصية الأساسية بـ patientForm
    await api.patch(`/api/monitored-elements/${patientId.value}/`, {
      full_name: patientForm.value.full_name,
      date_of_birth: patientForm.value.date_of_birth,
      gender: patientForm.value.gender,
      element_type: patientForm.value.element_type
    })

    // 2. تحديث وحفظ السجل الفسيولوجي للأمراض المزمنة
    const chronic_conditions = []
    if (medicalHistoryFlags.value.heart_disease) {
      chronic_conditions.push({ name: 'heart_disease' })
    }
    if (medicalHistoryFlags.value.chronic_conditions) {
      chronic_conditions.push({ name: 'diabetes' })
    }

    const medRes = await api.get('/api/medical-histories/', {
      params: { monitored_element: patientId.value }
    })
    const history = medRes.data?.[0] || (medRes.data.results?.[0])

    if (history) {
      await api.patch(`/api/medical-histories/${history.id}/`, {
        chronic_conditions: chronic_conditions
      })
    }

    alert('تم تحديث وحفظ السجل الشخصي والفسيولوجي المكتمل للمريض بنجاح!')
    fetchPatientDetails()
  } catch (e) {
    console.error('فشل حفظ التعديلات الطبية الشاملة:', e)
    alert('تعذر حفظ التعديلات، يرجى مراجعة البيانات')
  }
}

// مراقبة تغير معرف المريض في الرابط لإعادة جلب كافة البيانات فوراً عند التبديل بـ F5 و URL
watch(() => route.params.id, (newId) => {
  if (newId) {
    patientId.value = newId
    
    patientName.value = 'المريض'
    patientData.value = {}
    patientForm.value = { full_name: '', date_of_birth: '', gender: 'M', element_type: 'patient' }
    assignedCaregivers.value = []
    customRules.value = []
    
    fetchPatientDetails()
    fetchAssignedCaregivers()
    fetchCustomRules()
  }
}, { immediate: true })

onMounted(() => {
  fetchPatientDetails()
  fetchAssignedCaregivers()
  fetchCustomRules()
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
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