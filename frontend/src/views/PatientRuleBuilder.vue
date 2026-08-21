<!-- PatientRuleBuilder.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- الهيدر العلوي: العنوان والتأكيد -->
    <header class="w-full flex items-center justify-between pb-2 select-none">
      <div>
        <h1 class="text-xl font-extrabold text-slate-800 tracking-tight">باني القواعد والبروتوكولات الخاصة للمريض</h1>
        <p class="text-[11px] text-slate-400 mt-1">إنشاء بروتوكولات فسيولوجية مخصصة وموجهة سريرياً لحالة هذا المريض حصراً</p>
      </div>

      <div class="flex items-center gap-3">
        <button 
          @click="discardChanges" 
          class="px-5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-500 font-bold text-xs transition-all shadow-xs cursor-pointer"
        >
          Discard
        </button>
        <button 
          @click="submitRuleForm" 
          class="bg-[#0d9488] hover:bg-teal-700 text-white font-bold text-xs px-5 py-2 rounded-xl shadow-sm hover:shadow transition-all cursor-pointer"
        >
          Save Protocol
        </button>
      </div>
    </header>

    <!-- الهيكل اللوجستي الثنائي المتناظر -->
    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch w-full">
      
      <!-- القسم الأول: هوية القاعدة الخاصة والمستلم -->
      <div class="lg:col-span-4 bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between gap-5">
        <div class="space-y-5">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 bg-teal-50 text-teal-700 font-black rounded-full flex items-center justify-center border border-teal-100 text-xs font-mono">1</span>
            <span class="font-extrabold text-slate-800 text-sm">هوية القاعدة الخاصة</span>
          </div>

          <div class="space-y-4 text-xs">
            <!-- اسم القاعدة المخصصة -->
            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">اسم القاعدة المخصصة للمريض</label>
              <input 
                v-model="ruleForm.name" 
                type="text" 
                required 
                placeholder="بروتوكول ضبط أكسجين نوح آدم الخاص" 
                class="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 focus:border-teal-500 outline-none font-semibold text-slate-700" 
              />
            </div>

            <!-- درجة الخطورة السريرية -->
            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">درجة الخطورة السريرية</label>
              <div class="grid grid-cols-3 gap-2 bg-slate-50 p-1 border border-slate-100 rounded-xl">
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
                  حالة حرجة
                </button>
              </div>
            </div>

            <!-- 🟢 أداة الخيار الثنائي الحصري لطريقة احتساب مهل الإنذار -->
            <div class="space-y-1.5">
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">
                طريقة احتساب مهلة الإنذار السريري
              </label>
              <div class="grid grid-cols-2 gap-1 bg-slate-50 p-1 border border-slate-100 rounded-xl select-none">
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

            <!-- حقل استدامة الخطر العام للبروتوكول بأكمله (يُفتح فقط في الوضع الموحد) -->
            <div class="space-y-1.5 transition-all duration-300" :class="{ 'opacity-40 pointer-events-none': ruleForm.duration_mode === 'custom' }">
              <label class="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                مهلة الاستدامة العامة للبروتوكول
              </label>
              <select 
                v-model.number="ruleForm.duration_seconds" 
                :disabled="ruleForm.duration_mode === 'custom'"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 outline-none font-bold text-slate-700 font-mono text-center cursor-pointer focus:bg-white focus:border-teal-500 disabled:opacity-40"
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
                المهلة الزمنية المطبقة على شروط القاعدة ككل، تم حصر الخيارات بمضاعفات الـ 30 ثانية لتتوافق مع بث الحساسات.
              </p>
            </div>

          </div>
        </div>

        <!-- حالة التنشيط المنزلقة مع التعريب -->
        <div class="flex items-center justify-between pt-4 border-t border-slate-100 text-xs select-none">
          <span class="font-extrabold text-[10px] text-slate-400 uppercase tracking-wider">نشط</span>
          <button 
            @click="ruleForm.is_active = !ruleForm.is_active" 
            class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out outline-none"
            :class="ruleForm.is_active ? 'bg-emerald-500' : 'bg-slate-300'"
          >
            <span 
              class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
              :class="ruleForm.is_active ? 'translate-x-0' : '-translate-x-4'" 
            ></span>
          </button>
        </div>
      </div>

      <!-- القسم الثاني: شروط التفعيل -->
      <div class="lg:col-span-8 bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between gap-4">
        <div class="space-y-4">
          <div class="flex items-center justify-between pb-1">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 bg-teal-50 text-teal-700 font-black rounded-full flex items-center justify-center border border-teal-100 text-xs font-mono">2</span>
              <span class="font-extrabold text-slate-800 text-sm">شروط التفعيل المنطقية لحالة المريض</span>
            </div>

            <button 
              type="button" 
              @click="addCondition" 
              class="text-teal-700 bg-white hover:bg-teal-50 border border-teal-200 hover:border-teal-300 font-bold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1 transition-colors cursor-pointer"
            >
              <span>+ Add Condition</span>
            </button>
          </div>

          <!-- صفوف الشروط الديناميكية الموزعة بـ 12 عمود متجانس مع إضافة حقل الاستدامة المخصص للحساس المطور -->
          <div class="space-y-3 overflow-y-auto max-h-[220px] custom-scrollbar pr-1">
            <div 
              v-for="(cond, index) in ruleForm.conditions" 
              :key="index" 
              class="grid grid-cols-12 gap-2 items-center bg-slate-50/50 p-2.5 border border-slate-100 rounded-xl animate-[fadeIn_0.2s_ease-out]"
            >
              <!-- 1. أداة الربط المنطقي (Col: 2) -->
              <div class="col-span-2">
                <span 
                  v-if="index === 0" 
                  class="w-full inline-flex justify-center bg-teal-50 border border-teal-200 text-teal-700 font-bold px-2 py-1.5 rounded-lg text-[10px] uppercase font-mono"
                >
                  IF
                </span>
                <select 
                  v-else 
                  v-model="cond.connector" 
                  class="w-full bg-white border border-slate-200 text-slate-700 font-bold font-mono text-[10px] px-2 py-1.5 rounded-lg outline-none cursor-pointer text-center"
                >
                  <option value="AND">AND</option>
                  <option value="OR">OR</option>
                </select>
              </div>

              <!-- 2. الحساس / الحقل (Col: 3) -->
              <div class="col-span-3">
                <select v-model="cond.field" class="w-full bg-white border border-slate-200 rounded-xl px-2.5 py-1.5 text-xs outline-none">
                  <option value="severity">خطورة الذكاء (AI)</option>
                  <option value="heart_rate">نبض القلب (HR)</option>
                  <option value="oxygen_saturation">أكسجين الدم (SpO2)</option>
                  <option value="body_temperature">درجة الحرارة (Temp)</option>
                  <option value="blood_pressure_systolic">الضغط الانقباضي</option>
                  <option value="blood_pressure_diastolic">الضغط الانبساطي</option>
                  <option value="respiratory_rate">معدل التنفس (RR)</option>
                  <option value="activity_level">النشاط (Activity)</option>
                  <option value="room_temperature">حرارة الغرفة</option>
                </select>
              </div>

              <!-- 3. المعامل المنطقي (Col: 1) -->
              <div class="col-span-1">
                <select v-model="cond.op" class="w-full bg-white border border-slate-200 rounded-xl px-1 py-1.5 text-xs font-mono font-bold outline-none text-center">
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<=">&lt;=</option>
                  <option value="==">==</option>
                  <option value="!=">!=</option>
                </select>
              </div>

              <!-- 4. القيمة المطلوب قياسها (Col: 2) -->
              <div class="col-span-2">
                <select 
                  v-if="cond.field === 'severity'" 
                  v-model="cond.value" 
                  class="w-full bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-xs font-bold outline-none"
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                </select>
                <input 
                  v-else
                  v-model="cond.value" 
                  type="number" 
                  step="0.1" 
                  required 
                  class="w-full bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-xs font-mono font-bold outline-none text-center" 
                />
              </div>

              <!-- 🟢 5. حقل مهلة استدامة اختيارية مخصصة للحساس نفسه (تُقفل تلقائياً إذا كنا في الوضع العام لتفادي التداخل) (Col: 3) -->
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

              <!-- 6. زر الحذف (Col: 1) -->
              <div class="col-span-1 text-center">
                <button 
                  type="button" 
                  @click="removeCondition(index)" 
                  class="text-slate-400 hover:text-rose-600 font-bold transition-colors cursor-pointer"
                  v-if="ruleForm.conditions.length > 1"
                >
                  <svg class="w-4 h-4 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- القسم الثالث: الإجراء والتوصية السريرية والمستلم -->
      <div class="lg:col-span-12 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
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
              placeholder="مثال: تفقد قناع الأكسجين فوراً، تحضير السوائل الوريدية، وإبلاغ كادر تمريض الدور المشرف..." 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 focus:bg-white focus:border-teal-500 outline-none transition-all font-medium text-slate-700"
            ></textarea>
          </div>

          <div class="md:col-span-4 flex flex-col justify-between gap-3 text-xs">
            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">توجيه التنبيه السريري للمستلم</label>
              <select v-model="ruleForm.recipient" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none font-bold text-slate-700">
                <option value="treating_doctor_only">الطبيب المعالج فقط</option>
                <option value="caregiver_only">مقدم الرعاية فقط</option>
                <option value="doctor_and_caregiver">الطبيب المعالج ومقدم الرعاية معاً</option>
              </select>
            </div>

            <div>
              <label class="block text-[10px] font-extrabold text-slate-400 mb-1.5 uppercase tracking-wider">قناة التنبيه والاتصال</label>
              <div class="flex items-center gap-4 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">
                <label class="flex items-center gap-2 cursor-pointer font-bold select-none text-slate-600">
                  <input type="checkbox" value="UI Alert" v-model="ruleForm.channels" class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4" />
                  <span>تنبيه بالواجهة (UI Alert)</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer font-bold select-none text-slate-600">
                  <input type="checkbox" value="SMS" v-model="ruleForm.channels" class="rounded text-teal-600 w-4 h-4" />
                  <span>رسالة نصية قصيرة (SMS)</span>
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

const router = useRouter()
const route = useRoute()
const patientId = ref(route.params.id) 

const loading = ref(false)
const isEditing = ref(false)
const currentRuleId = ref(null)

const ruleForm = ref({
  name: '',
  conditions: [
    { field: 'heart_rate', op: '>', value: 110, connector: 'AND', duration_seconds: null },
    { field: 'activity_level', op: '==', value: 0, connector: 'AND', duration_seconds: null }
  ],
  severity: 'high',
  duration_mode: 'global', // 🟢 حقل تحديد وضع الاحتساب: 'global' (موحد للقاعدة) أو 'custom' (مخصص لكل حساس)
  duration_seconds: 0, 
  action_template: '',
  channels: ['UI Alert'],
  recipient: 'treating_doctor_only',
  is_active: true
})

// 🟢 تبديل وضع الاحتساب وقفل الحقول المقابلة بذكاء سريري
const setDurationMode = (mode) => {
  ruleForm.value.duration_mode = mode
  if (mode === 'global') {
    // تصفير مدد الحساسات لإجبارها على وراثة القيمة العامة
    ruleForm.value.conditions.forEach(c => {
      c.duration_seconds = null
    })
  } else if (mode === 'custom') {
    // تصفير مهلة القاعدة العامة لتفادي التداخل البصري
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
  if (confirm('هل أنت متأكد من رغبتك في إلغاء التعديلات والرجوع للملف الطبي؟')) {
    router.push(`/patients/${patientId.value}/medical-history`)
  }
}

const loadRuleForEdit = async (id) => {
  loading.value = true
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
    console.error('فشل تحميل تفاصيل القاعدة المخصصة:', e)
  } finally {
    loading.value = false
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
      monitored_element: Number(patientId.value), 
      condition: {
        operator: 'AND',
        conditions: ruleForm.value.conditions.map(c => ({
          ...c,
          // إذا كنا في الوضع العام، نجبر جميع حساسات السطر على null لترث المدة العامة، وإلا نمرر القيمة المخصصة
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

    router.push(`/patients/${patientId.value}/medical-history`)
  } catch (e) {
    console.error('فشل حفظ البروتوكول السريري المخصص:', e)
    alert('فشل حفظ البروتوكول، يرجى التحقق من المدخلات')
  }
}

onMounted(async () => {
  if (route.params.ruleId) {
    isEditing.value = true
    currentRuleId.value = route.params.ruleId
    await loadRuleForEdit(route.params.ruleId)
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