<!-- ProtocolBuilder.vue -->
<template>
  <div class="w-full min-h-screen bg-slate-100 text-slate-700 font-sans antialiased p-4 md:p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- الهيدر العلوي باللون التركوازي (متجاوب بالكامل) -->
    <header class="w-full rounded-3xl border border-white/10 p-5 md:p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <FileText :size="16" class="text-teal-300" />
          <span class="text-xs text-teal-200 font-mono font-extrabold uppercase tracking-wider">باني البروتوكولات السريرية</span>
        </div>
        <h1 class="text-xl md:text-2xl font-extrabold text-white tracking-tight">محرك قواعد ديناميكي متعدد الشروط</h1>
        <p class="text-xs text-teal-200/70 mt-1">إصدار التنبيهات السريرية الآلية بناءً على شروط مخصصة</p>
      </div>

      <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
        <button 
          @click="discardChanges" 
          class="bg-white/10 hover:bg-white/20 text-white border border-white/20 font-bold text-xs px-4 md:px-5 py-2.5 md:py-3 rounded-2xl backdrop-blur-sm transition-all flex items-center gap-2 cursor-pointer"
        >
          <X :size="14" />
          <span>إلغاء</span>
        </button>
        <button 
          @click="submitRuleForm" 
          class="bg-[#0d9488]/30 hover:bg-[#0d9488]/50 text-teal-200 border border-teal-400/20 font-bold text-xs px-4 md:px-5 py-2.5 md:py-3 rounded-2xl backdrop-blur-sm transition-all flex items-center gap-2 shadow-lg shadow-teal-900/10 cursor-pointer"
        >
          <Save :size="14" />
          <span>حفظ البروتوكول</span>
        </button>
      </div>
    </header>

    <!-- شبكة الأقسام متجاوبة (Stack عمودي على الموبايل، وبجوار بعضها على الشاشات الكبيرة) -->
    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch w-full">
      
      <!-- القسم 1: هوية القاعدة (بطاقة بيضاء) -->
      <div class="lg:col-span-4 bg-white rounded-2xl border border-slate-200 p-5 md:p-6 shadow-sm flex flex-col justify-between gap-5">
        <div class="space-y-5">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 bg-teal-50 text-teal-700 font-black rounded-full flex items-center justify-center border border-teal-100 text-xs font-mono">1</span>
            <span class="font-extrabold text-slate-800 text-sm">هوية البروتوكول السريري</span>
          </div>

          <div class="space-y-4 text-xs">
            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">اسم البروتوكول</label>
              <input 
                v-model="ruleForm.name" 
                type="text" 
                required 
                placeholder="مثال: إنذار مبكر للإنتان" 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:border-teal-500 outline-none font-semibold text-slate-700 placeholder-slate-400" 
              />
            </div>

            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">درجة الخطورة السريرية</label>
              <div class="grid grid-cols-3 gap-2 bg-slate-50 p-1 border border-slate-200 rounded-xl">
                <button 
                  type="button"
                  @click="ruleForm.severity = 'medium'"
                  :class="ruleForm.severity === 'medium' ? 'bg-yellow-500 text-white shadow-sm border border-yellow-600' : 'bg-transparent text-slate-400 hover:text-slate-600'"
                  class="py-2 text-[10px] font-bold rounded-lg transition-all cursor-pointer"
                >
                  متوسط
                </button>
                <button 
                  type="button"
                  @click="ruleForm.severity = 'high'"
                  :class="ruleForm.severity === 'high' ? 'bg-orange-500 text-white shadow-sm border border-orange-600' : 'bg-transparent text-slate-400 hover:text-slate-600'"
                  class="py-2 text-[10px] font-bold rounded-lg transition-all cursor-pointer"
                >
                  مرتفع
                </button>
                <button 
                  type="button"
                  @click="ruleForm.severity = 'critical'"
                  :class="ruleForm.severity === 'critical' ? 'bg-red-500 text-white shadow-sm border border-red-600' : 'bg-transparent text-slate-400 hover:text-slate-600'"
                  class="py-2 text-[10px] font-bold rounded-lg transition-all cursor-pointer"
                >
                  حالة حرجّة
                </button>
              </div>
            </div>

            <!-- 🟢 أداة اختيار طريقة احتساب المهل الحصرية الجديدة -->
            <div class="space-y-1.5">
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">
                طريقة احتساب مهلة الإنذار السريري
              </label>
              <div class="grid grid-cols-2 gap-1 bg-slate-50 p-1 border border-slate-200 rounded-xl select-none">
                <button 
                  type="button"
                  @click="setDurationMode('global')"
                  :class="ruleForm.duration_mode === 'global' ? 'bg-[#0d9488] text-white shadow-sm border border-teal-600' : 'bg-transparent text-slate-400 hover:text-slate-600'"
                  class="py-2 text-[9px] font-black rounded-lg transition-all cursor-pointer"
                >
                  مهلة موحدة للقاعدة
                </button>
                <button 
                  type="button"
                  @click="setDurationMode('custom')"
                  :class="ruleForm.duration_mode === 'custom' ? 'bg-[#0d9488] text-white shadow-sm border border-teal-600' : 'bg-transparent text-slate-400 hover:text-slate-600'"
                  class="py-2 text-[9px] font-black rounded-lg transition-all cursor-pointer"
                >
                  مهل مخصصة للحساسات
                </button>
              </div>
            </div>

            <!-- حقل استدامة الخطر العام (يفتح ويغلق حركياً) -->
            <div class="space-y-1.5 transition-all duration-300" :class="{ 'opacity-40 pointer-events-none': ruleForm.duration_mode === 'custom' }">
              <label class="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                مهلة الاستدامة العامة للبروتوكول
              </label>
              <select 
                v-model.number="ruleForm.duration_seconds" 
                :disabled="ruleForm.duration_mode === 'custom'"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-700 font-mono text-center cursor-pointer focus:bg-white focus:border-[#0d9488] disabled:opacity-40"
              >
                <option :value="0">0 ثانية (إنذار فوري)</option>
                <option :value="30">30 ثانية (دورة واحدة)</option>
                <option :value="60">60 ثانية (دقيقة واحدة)</option>
                <option :value="90">90 ثانية (دقيقة ونصف)</option>
                <option :value="120">120 ثانية (دقيقتان)</option>
                <option :value="180">180 ثانية (3 دقائق)</option>
                <option :value="300">300 ثانية (5 دقائق)</option>
                <option :value="600">600 ثانية (10 دقائق)</option>
              </select>
              <p class="text-[9px] text-slate-400 mt-1 leading-relaxed">
                المهلة المطبقة على شروط القاعدة ككل، تم حصر الخيارات بمضاعفات الـ 30 ثانية لتتوافق مع بث الحساسات.
              </p>
            </div>

          </div>
        </div>

        <!-- مفتاح التفعيل المنزلق -->
        <div class="flex items-center justify-between pt-4 border-t border-slate-100 text-xs select-none">
          <span class="font-extrabold text-[10px] text-slate-400 uppercase tracking-wider">نشط</span>
          <button 
            @click="ruleForm.is_active = !ruleForm.is_active" 
            class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out outline-none"
            :class="ruleForm.is_active ? 'bg-teal-600' : 'bg-slate-300'"
          >
            <span 
              class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
              :class="ruleForm.is_active ? 'translate-x-4 rtl:-translate-x-4' : 'translate-x-0'"
            ></span>
          </button>
        </div>
      </div>

      <!-- القسم 2: شروط التفعيل (متجاوب مع الموبايل بالكامل) -->
      <div class="lg:col-span-8 bg-white rounded-2xl border border-slate-200 p-5 md:p-6 shadow-sm flex flex-col justify-between gap-4">
        <div class="space-y-4">
          <div class="flex items-center justify-between pb-1">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 bg-teal-50 text-teal-700 font-black rounded-full flex items-center justify-center border border-teal-100 text-xs font-mono">2</span>
              <span class="font-extrabold text-slate-800 text-sm">شروط التفعيل المنطقية</span>
            </div>
            <button 
              type="button" 
              @click="addCondition" 
              class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1 transition-colors cursor-pointer"
            >
              <Plus :size="12" stroke-width="2.5" />
              <span>إضافة شرط</span>
            </button>
          </div>

          <!-- 🟢 كروت الشروط: متراكمة عمودياً على الموبايل كلياً لسهولة اللمس وتتحول لصف متناسق على الكمبيوتر -->
          <div class="space-y-3 overflow-y-auto max-h-[380px] lg:max-h-[280px] custom-scrollbar pr-1">
            <div 
              v-for="(cond, index) in ruleForm.conditions" 
              :key="index" 
              class="flex flex-col md:grid md:grid-cols-12 gap-3 md:gap-2 items-stretch md:items-center bg-slate-50/70 p-4 md:p-3 border border-slate-200 rounded-2xl md:rounded-xl relative"
            >
              <!-- أداة الربط المنطقي (Col: 2) -->
              <div class="col-span-2">
                <span 
                  v-if="index === 0" 
                  class="w-full inline-flex justify-center bg-teal-50 border border-teal-200 text-teal-700 font-bold px-2 py-1.5 rounded-lg text-[10px] uppercase font-mono"
                >
                  إذا
                </span>
                <select 
                  v-else 
                  v-model="cond.connector" 
                  class="w-full bg-white border border-slate-200 text-slate-700 font-bold font-mono text-[10px] px-2 py-1.5 rounded-lg outline-none cursor-pointer text-center"
                >
                  <option value="AND">و</option>
                  <option value="OR">أو</option>
                </select>
              </div>

              <!-- الحساس / الحقل (Col: 3) -->
              <div class="col-span-3">
                <select v-model="cond.field" class="w-full bg-white border border-slate-200 rounded-xl px-2.5 py-1.5 text-xs outline-none text-slate-700">
                  <option value="severity">خطورة الذكاء الاصطناعي (AI)</option>
                  <option value="heart_rate">نبض القلب (HR)</option>
                  <option value="oxygen_saturation">أكسجين الدم (SpO2)</option>
                  <option value="body_temperature">درجة الحرارة (Temp)</option>
                  <option value="blood_pressure_systolic">الضغط الانقباضي</option>
                  <option value="blood_pressure_diastolic">الضغط الانبساطي</option>
                  <option value="respiratory_rate">معدل التنفس (RR)</option>
                  <option value="activity_level">النشاط الحركي</option>
                  <option value="room_temperature">حرارة الغرفة</option>
                </select>
              </div>

              <!-- المعامل المنطقي (Col: 1) -->
              <div class="col-span-1">
                <select v-model="cond.op" class="w-full bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-xs font-mono font-bold outline-none text-center text-slate-700">
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<=">&lt;=</option>
                  <option value="==">==</option>
                  <option value="!=">!=</option>
                </select>
              </div>

              <!-- القيمة (Col: 2) -->
              <div class="col-span-2">
                <select 
                  v-if="cond.field === 'severity'" 
                  v-model="cond.value" 
                  class="w-full bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-xs font-bold outline-none text-slate-700"
                >
                  <option value="critical">حرج</option>
                  <option value="high">مرتفع</option>
                  <option value="medium">متوسط</option>
                </select>
                <input 
                  v-else
                  v-model="cond.value" 
                  type="number" 
                  step="0.1" 
                  required 
                  class="w-full bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-xs font-mono font-bold outline-none text-center text-slate-700" 
                />
              </div>

              <!-- 🟢 حقل مهلة استدامة اختيارية للحساس نفسه بمضاعفات الـ 30 (يغلق في الوضع الموحد) (Col: 3) -->
              <div class="col-span-3 transition-all duration-300" :class="{ 'opacity-35 pointer-events-none select-none': ruleForm.duration_mode === 'global' }">
                <select 
                  v-model="cond.duration_seconds" 
                  :disabled="ruleForm.duration_mode === 'global'"
                  class="w-full bg-white border border-[#0d9488]/40 focus:border-[#0d9488] rounded-xl px-2 py-1.5 text-[10px] font-bold outline-none text-center font-mono cursor-pointer disabled:bg-slate-100 disabled:text-slate-400"
                >
                  <option :value="null">حسب القاعدة (الافتراضي)</option>
                  <option :value="0">0 ثانية (فوري)</option>
                  <option :value="30">30 ثانية</option>
                  <option :value="60">60 ثانية (دقيقة)</option>
                  <option :value="90">90 ثانية</option>
                  <option :value="120">120 ثانية (دقيقتان)</option>
                  <option :value="180">180 ثانية (3 دقائق)</option>
                  <option :value="300">300 ثانية (5 دقائق)</option>
                  <option :value="600">600 ثانية (10 دقائق)</option>
                </select>
              </div>

              <!-- زر الحذف (متحرك في الزاوية العلوية اليسرى على الموبايل لعدم تشويه المظهر وبمكان طبيعي على الكمبيوتر) (Col: 1) -->
              <div class="col-span-1 text-left md:text-center absolute top-3.5 left-3.5 md:static select-none">
                <button 
                  type="button" 
                  @click="removeCondition(index)" 
                  class="text-slate-400 hover:text-rose-600 transition-colors p-1.5 bg-slate-100 md:bg-transparent rounded-lg cursor-pointer"
                  v-if="ruleForm.conditions.length > 1"
                >
                  <Trash2 :size="14" stroke-width="1.8" />
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>

      <!-- القسم 3: الإجراء والتوصية وقنوات التواصل (بطاقة بيضاء) -->
      <div class="lg:col-span-12 bg-white rounded-2xl border border-slate-200 p-5 md:p-6 shadow-sm space-y-4">
        <h4 class="font-extrabold text-slate-700 text-xs flex items-center gap-2">
          <span class="w-5 h-5 bg-teal-50 text-teal-700 font-bold rounded-lg flex items-center justify-center border border-teal-100 font-mono">3</span>
          <span>الإجراء وقنوات التواصل (Action & Notification)</span>
        </h4>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
          <div class="md:col-span-8 space-y-1.5 text-xs">
            <label class="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">التوصية والبروتوكول الطبي المقترح</label>
            <textarea 
              v-model="ruleForm.action_template" 
              rows="3" 
              required 
              placeholder="مثال: البدء العاجل ببروتوكول السيبس وسحب عينات الدم..." 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 focus:border-teal-500 outline-none transition-all font-medium text-slate-700 placeholder-slate-400"
            ></textarea>
          </div>

          <div class="md:col-span-4 flex flex-col justify-between gap-3 text-xs">
            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">توجيه التنبيه للمستلم</label>
              <select v-model="ruleForm.recipient" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none font-bold text-slate-700">
                <option value="treating_doctor_only">الطبيب المعالج فقط</option>
                <option value="caregiver_only">مقدم الرعاية فقط</option>
                <option value="doctor_and_caregiver">الطبيب المعالج ومقدم الرعاية معاً</option>
              </select>
            </div>

            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">قناة التنبيه</label>
              <div class="flex items-center gap-4 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">
                <label class="flex items-center gap-2 cursor-pointer font-bold select-none text-slate-600">
                  <input type="checkbox" value="UI Alert" v-model="ruleForm.channels" class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4" />
                  <span>تنبيه بالواجهة (UI)</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer font-bold select-none text-slate-600">
                  <input type="checkbox" value="SMS" v-model="ruleForm.channels" class="rounded text-teal-600 w-4 h-4" />
                  <span>رسالة نصية (SMS)</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'
import { FileText, Save, X, Plus, Trash2 } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const isEditing = ref(false)
const currentRuleId = ref(null)

const ruleForm = ref({
  name: '',
  conditions: [
    { field: 'heart_rate', op: '>', value: 110, connector: 'AND', duration_seconds: null },
    { field: 'activity_level', op: '==', value: 0, connector: 'AND', duration_seconds: null }
  ],
  severity: 'high',
  duration_mode: 'global', // 🟢 تحديد وضع الاحتساب: 'global' (موحد للقاعدة) أو 'custom' (مخصص لكل حساس)
  duration_seconds: 0,
  action_template: '',
  channels: ['UI Alert'],
  recipient: 'treating_doctor_only',
  is_active: true
})

// 🟢 تبديل وضع الاحتساب وقفل الحقول المقابلة بذكاء سريري لمنع التداخل البصري والبرمجي
const setDurationMode = (mode) => {
  ruleForm.value.duration_mode = mode
  if (mode === 'global') {
    ruleForm.value.conditions.forEach(c => {
      c.duration_seconds = null
    })
  } else if (mode === 'custom') {
    ruleForm.value.duration_seconds = 0
  }
}

const addCondition = () => {
  ruleForm.value.conditions.push({ field: 'room_temperature', op: '>=', value: 37.5, connector: 'AND', duration_seconds: null })
}

const removeCondition = (index) => {
  if (ruleForm.value.conditions.length > 1) {
    ruleForm.value.conditions.splice(index, 1)
  }
}

const discardChanges = () => {
  if (confirm('هل أنت متأكد من رغبتك في إلغاء التعديلات والرجوع للقائمة؟')) {
    router.push('/protocols')
  }
}

const loadRuleForEdit = async (id) => {
  try {
    const res = await api.get(`/api/rules/${id}/`)
    const rule = res.data
    const condObj = rule.condition || {}
    
    // فحص ما إذا كان هناك أي حساس يحمل مهلة مخصصة لتحديد وضع الواجهة تلقائياً
    const hasCustomDurations = Array.isArray(condObj.conditions) && condObj.conditions.some(c => c.duration_seconds !== null)
    const mode = hasCustomDurations ? 'custom' : 'global'

    ruleForm.value = {
      name: rule.name || '',
      conditions: Array.isArray(condObj.conditions) && condObj.conditions.length > 0 
        ? JSON.parse(JSON.stringify(condObj.conditions)) 
        : [{ field: 'heart_rate', op: '>', value: 110, connector: 'AND', duration_seconds: null }],
      severity: rule.severity || 'medium',
      duration_mode: mode, // تحميل وضع الاحتساب التاريخي
      duration_seconds: condObj.duration_seconds || rule.duration_seconds || 0,
      action_template: rule.action_template || '',
      channels: condObj.channels || ['UI Alert'],
      recipient: condObj.recipient || 'treating_doctor_only',
      is_active: rule.is_active !== false
    }
  } catch (e) {
    console.error('فشل تحميل تفاصيل القاعدة:', e)
  }
}

const submitRuleForm = async () => {
  if (!ruleForm.value.name || !ruleForm.value.action_template) {
    alert('يرجى ملء جميع الحقول الإجبارية أولاً')
    return
  }

  try {
    const payload = {
      name: ruleForm.value.name,
      condition: {
        operator: 'AND',
        conditions: ruleForm.value.conditions.map(c => ({
          ...c,
          // صمام الأمان: إرسال القيمة كـ Integer إذا تم اختيارها، وإلا تمريرها كـ null لترث مدة القاعدة العامة تلقائياً
          duration_seconds: ruleForm.value.duration_mode === 'custom'
            ? (c.duration_seconds !== null && c.duration_seconds !== '' ? Number(c.duration_seconds) : null)
            : null
        })),
        channels: ruleForm.value.channels,
        recipient: ruleForm.value.recipient,
        // إذا كنا في وضع الحساسات المخصصة، نجبر المدة العامة للبروتوكول على 0 لتجنب أي تداخل
        duration_seconds: ruleForm.value.duration_mode === 'global' ? Number(ruleForm.value.duration_seconds || 0) : 0
      },
      action_template: ruleForm.value.action_template,
      severity: ruleForm.value.severity,
      is_active: ruleForm.value.is_active
    }

    if (isEditing.value && currentRuleId.value) {
      await api.patch(`/api/rules/${currentRuleId.value}/`, payload)
    } else {
      await api.post('/api/rules/', payload)
    }

    router.push('/protocols')
  } catch (e) {
    console.error('فشل حفظ البروتوكول السريري:', e)
    alert('فشل حفظ البروتوكول، يرجى التحقق من المدخلات')
  }
}

onMounted(async () => {
  if (route.params.id) {
    isEditing.value = true
    currentRuleId.value = route.params.id
    await loadRuleForEdit(route.params.id)
  }
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

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%2364748b'><path d='M0 3l5 5 5-5z'/></svg>");
  background-repeat: no-repeat;
  background-position: left 12px center;
  padding-left: 28px !important;
}

[dir="ltr"] select {
  background-position: right 12px center;
  padding-right: 28px !important;
  padding-left: 10px !important;
}
</style>