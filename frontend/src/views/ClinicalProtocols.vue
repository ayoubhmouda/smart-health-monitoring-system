<!-- ClinicalProtocols.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- هيدر الصفحة بتدرج تركوازي داكن -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <FileText :size="16" class="text-teal-300" />
          <span class="text-xs text-teal-200 font-mono font-extrabold uppercase tracking-wider">لوحة الإدارة السريرية اللوجستية</span>
          <span v-if="currentUserIsAdmin" class="text-[10px] bg-teal-500/20 text-teal-200 px-2.5 py-0.5 rounded-full font-bold border border-teal-400/20">صلاحيات المدير</span>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">إدارة البروتوكولات والقواعد السريرية العامة</h1>
        <p class="text-xs text-teal-200/70 mt-1">عرض السجلات وتوجيه محرك القواعد ببروتوكولات الأمان الطبية</p>
      </div>

      <router-link 
        v-if="currentUserIsAdmin"
        to="/protocols/new" 
        class="bg-teal-500/20 hover:bg-teal-500/30 text-teal-200 border border-teal-400/20 font-bold text-xs px-5 py-3 rounded-2xl backdrop-blur-sm transition-all flex items-center gap-2 shadow-lg shadow-teal-900/10"
      >
        <Plus :size="16" stroke-width="2.5" />
        <span>إضافة بروتوكول سريري مركّب</span>
      </router-link>
    </header>

    <!-- البطاقات الإحصائية -->
    <section class="grid grid-cols-1 sm:grid-cols-3 gap-5">
      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs text-slate-400 font-bold uppercase">إجمالي البروتوكولات المعتمدة</p>
          <p class="text-2xl font-black text-slate-800 font-mono mt-1">{{ rules.length }}</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center">
          <ClipboardList :size="24" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs text-slate-400 font-bold uppercase">البروتوكولات النشطة حالياً</p>
          <p class="text-2xl font-black text-emerald-600 font-mono mt-1">{{ activeRulesCount }}</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
          <CheckCircle :size="24" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs text-slate-400 font-bold uppercase">بروتوكولات الخطورة العالية والحرجة</p>
          <p class="text-2xl font-black text-rose-600 font-mono mt-1">{{ criticalRulesCount }}</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center">
          <AlertTriangle :size="24" />
        </div>
      </div>
    </section>

    <!-- جدول السجلات -->
    <main class="w-full bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
      <div v-if="loading" class="w-full text-center py-12">
        <span class="text-sm font-bold text-slate-400 animate-pulse">جاري تحميل السجلات والبروتوكولات...</span>
      </div>

      <div v-else-if="rules.length === 0" class="w-full text-center py-12 p-6">
        <p class="text-sm text-slate-500 font-bold">لا يوجد بروتوكولات سريرية مسجلة حالياً.</p>
      </div>

      <div v-else class="w-full overflow-x-auto">
        <table class="w-full text-right border-collapse text-xs">
          <thead>
            <tr class="bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white font-extrabold select-none">
              <th class="p-4 pr-6">اسم البروتوكول السريري</th>
              <th class="p-4">الشروط الفسيولوجية والسياقية</th>
              <th class="p-4">التوصية وقناة التواصل</th>
              <th class="p-4 text-center">المستهدف بالإشعار</th>
              <th class="p-4 text-center">الخطورة</th>
              <th class="p-4 text-center">الحالة</th>
              <th v-if="currentUserIsAdmin" class="p-4 text-left pl-6">الإجراءات</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-100">
            <tr 
              v-for="rule in rules" 
              :key="rule.id" 
              class="hover:bg-slate-50/50 transition-colors group"
            >
              <!-- اسم البروتوكول -->
              <td class="p-4 pr-6">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center shadow-inner flex-shrink-0">
                    <FileText :size="18" stroke-width="2" />
                  </div>
                  <div>
                    <p class="font-extrabold text-slate-800 text-sm">{{ rule.name }}</p>
                  </div>
                </div>
              </td>

              <!-- الشروط مع فواصل "و" -->
              <td class="p-4">
                <div class="flex flex-wrap items-center gap-1.5">
                  <template v-for="(cond, idx) in extractConditions(rule.condition)" :key="idx">
                    <!-- فاصل "و" -->
                    <span v-if="idx > 0" class="text-[10px] font-bold text-slate-400 uppercase px-1">و</span>
                    <!-- بطاقة الشرط -->
                    <span class="inline-flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-mono">
                      <span class="text-teal-600 font-bold">{{ cond.field }}</span>
                      <span class="text-slate-400">{{ cond.op }}</span>
                      <span class="text-slate-800 font-bold">{{ cond.value }}</span>
                    </span>
                  </template>
                </div>
              </td>

              <!-- التوصية والقناة -->
              <td class="p-4 text-slate-700">
                <p class="font-bold text-slate-800 truncate max-w-xs">{{ rule.action_template || 'إبلاغ الطبيب' }}</p>
                <div class="flex items-center gap-1 mt-1">
                  <span v-for="ch in getRuleChannels(rule.condition)" :key="ch" class="text-[9px] bg-sky-50 text-sky-700 px-1.5 py-0.5 rounded border border-sky-100 font-mono">
                    {{ ch }}
                  </span>
                </div>
              </td>

              <!-- المستهدف -->
              <td class="p-4 text-center">
                <span class="font-bold text-slate-700 text-[11px]">{{ getRecipientText(rule.condition) }}</span>
              </td>

              <!-- الخطورة -->
              <td class="p-4 text-center font-bold text-[11px]" :class="getSeverityTextColor(rule.severity)">
                {{ getSeverityText(rule.severity) }}
              </td>

              <!-- الحالة: Toggle زر -->
              <td class="p-4 text-center">
                <button 
                  @click="toggleRuleStatus(rule)" 
                  class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out outline-none"
                  :class="rule.is_active ? 'bg-teal-600' : 'bg-slate-300'"
                  :title="rule.is_active ? 'إلغاء التفعيل' : 'تفعيل القاعدة'"
                >
                  <span 
                    class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
                    :class="rule.is_active ? 'translate-x-4 rtl:-translate-x-4' : 'translate-x-0'"
                  ></span>
                </button>
              </td>

              <!-- أزرار الإجراءات (أيقونات حرة) -->
              <td v-if="currentUserIsAdmin" class="p-4 text-left pl-6">
                <div class="flex items-center justify-end gap-1.5">
                  <button 
                    @click="router.push(`/protocols/edit/${rule.id}`)" 
                    class="p-1.5 rounded-lg text-slate-400 hover:text-sky-600 hover:bg-sky-50 transition-all"
                    title="تعديل البروتوكول"
                  >
                    <Pencil :size="16" stroke-width="2" />
                  </button>
                  <button 
                    @click="deleteRule(rule.id)" 
                    class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all"
                    title="حذف البروتوكول"
                  >
                    <Trash2 :size="16" stroke-width="2" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { 
  FileText, Plus, ClipboardList, CheckCircle, AlertTriangle,
  Pencil, Trash2
} from 'lucide-vue-next'

const router = useRouter()
const rules = ref([])
const loading = ref(true)

const currentUserIsAdmin = computed(() => {
  const role = localStorage.getItem('user_role')
  const superuser = localStorage.getItem('is_superuser') === 'true'
  return role === 'admin' || superuser === true
})

const activeRulesCount = computed(() => rules.value.filter(r => r.is_active).length)
const criticalRulesCount = computed(() => rules.value.filter(r => r.severity === 'critical' || r.severity === 'high').length)

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/rules/')
    rules.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('فشل جلب قائمة القواعد:', e)
  } finally {
    loading.value = false
  }
}

const extractConditions = (condObj) => {
  if (!condObj) return []
  if (Array.isArray(condObj.conditions)) return condObj.conditions
  return []
}

const getRuleChannels = (condObj) => {
  if (condObj && Array.isArray(condObj.channels)) return condObj.channels
  return ['UI Alert']
}

const getRecipientText = (condObj) => {
  const rec = condObj?.recipient || 'treating_doctor_only'
  if (rec === 'treating_doctor_only') return 'الطبيب المعالج فقط'
  if (rec === 'caregiver_only') return 'مقدم الرعاية فقط'
  if (rec === 'doctor_and_caregiver') return 'الطبيب ومقدم الرعاية'
  return 'الطبيب المعالج'
}

const getSeverityText = (sev) => {
  if (sev === 'critical') return 'حرج'
  if (sev === 'high') return 'عالي'
  return 'متوسط'
}

const getSeverityTextColor = (sev) => {
  if (sev === 'critical') return 'text-rose-600'
  if (sev === 'high') return 'text-amber-600'
  return 'text-yellow-600'
}

const toggleRuleStatus = async (rule) => {
  const newStatus = !rule.is_active
  rule.is_active = newStatus
  try {
    await api.patch(`/api/rules/${rule.id}/`, { is_active: newStatus })
  } catch (e) {
    rule.is_active = !newStatus
    console.error('فشل تغيير حالة القاعدة:', e)
  }
}

const deleteRule = async (id) => {
  if (!confirm('هل أنت تأكد من رغبتك في حذف هذا البروتوكول السريري؟')) return
  try {
    await api.delete(`/api/rules/${id}/`)
    fetchRules()
  } catch (e) {
    console.error('فشل حذف القاعدة:', e)
  }
}

onMounted(() => {
  fetchRules()
})
</script>

<style scoped>
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