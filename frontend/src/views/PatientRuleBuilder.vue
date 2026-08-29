<!-- PatientRuleBuilder.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl">
    
    <!-- الترويسة العلوية باللون التركوازي الغامق الموحد لهوية نظام MediWatch -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white select-none shrink-0">
      <div class="flex items-center gap-3">
        <!-- أيقونة باني القواعد الموحدة من إيكونيفاي داخل غلاف زجاجي ناعم -->
        <div class="w-10 h-10 shrink-0 rounded-xl bg-white/10 border border-white/5 flex items-center justify-center text-teal-300">
          <Icon icon="solar:tuning-2-bold" class="w-5 h-5" />
        </div>
        <div>
          <h1 class="text-xl md:text-2xl font-extrabold text-white tracking-tight">باني القواعد والبروتوكولات الخاصة للمريض</h1>
          <p class="text-xs text-teal-200/70 mt-1 font-medium">إنشاء بروتوكولات فسيولوجية مخصصة وموجهة سريرياً لحالة هذا المريض حصراً</p>
        </div>
      </div>

      <!-- أزرار الإلغاء والحفظ بالهوية الزجاجية المتناسقة مع لوحة التحكم -->
      <div class="flex items-center gap-2.5 w-full sm:w-auto justify-end select-none">
        <button 
          @click="discardChanges" 
          class="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-bold text-xs backdrop-blur-sm transition-all cursor-pointer"
        >
          Discard
        </button>
        <button 
          @click="submitRuleForm" 
          class="bg-teal-500/20 hover:bg-teal-500/30 text-teal-200 border border-teal-400/20 font-bold text-xs px-6 py-2.5 rounded-xl backdrop-blur-sm transition-all shadow-lg shadow-teal-900/10 cursor-pointer"
        >
          Save Protocol
        </button>
      </div>
    </header>

    <!-- الهيكل اللوجستي الثنائي المتناظر -->
    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch w-full">
      
      <!-- القسم الأول: هوية القاعدة الخاصة والمستلم -->
      <div class="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between overflow-hidden">
        
        <!-- 🟢 ترويسة هوية القاعدة باللون التركوازي الغامق والأيقونة البيضاء على اليسار المقابل تماماً -->
        <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none shrink-0">
          <div class="flex items-center gap-2">
            <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">1</span>
            <span class="font-extrabold text-white text-xs">هوية القاعدة الخاصة</span>
          </div>
          <Icon icon="solar:user-bold" class="w-5 h-5 text-white shrink-0" />
        </div>

        <div class="p-6 space-y-4 flex-1 flex flex-col justify-between gap-5 text-xs">
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

          <!-- أداة الخيار الثنائي الحصري لطريقة احتساب مهل الإنذار -->
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
          </div>

          <!-- حقل التجاوز الصريح للبروتوكولات العامة لمنع تداخل الإنذارات الكاذبة -->
          <div class="space-y-1.5" v-if="globalRules.length > 0">
            <label class="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
              إلغاء واستبدال بروتوكولات عامة نشطة
            </label>
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 max-h-[120px] overflow-y-auto custom-scrollbar space-y-2">
              <label 
                v-for="gRule in globalRules" 
                :key="gRule.id" 
                class="flex items-center gap-2 cursor-pointer font-bold select-none text-[11px] text-slate-600"
              >
                <input 
                  type="checkbox" 
                  :value="gRule.id" 
                  v-model="ruleForm.overridden_rules" 
                  class="rounded text-[#0d9488] focus:ring-[#0d9488]/50 w-3.5 h-3.5 cursor-pointer" 
                />
                <span>{{ gRule.name }} ({{ gRule.severity_display || gRule.severity }})</span>
              </label>
            </div>
            <p class="text-[9px] text-slate-400 mt-1 leading-relaxed">
              عند حفظ هذا البروتوكول, سيقوم النظام تلقائياً بتعطيل الإنذارات العامة المحددة أعلاه لنوح فقط تفادياً للتكرار [1, 2].
            </p>
          </div>

        </div>

        <!-- حالة التنشيط المنزلقة مع التعريب -->
        <div class="p-6 flex items-center justify-between border-t border-slate-100 text-xs select-none shrink-0">
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

      <!-- القسم الثاني: شروط التفعيل (ترويسة تركوازية ومفتاح الإضافة والأيقونة على اليسار المقابل للعنوان) -->
      <div class="lg:col-span-8 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col overflow-hidden gap-0">
        <!-- 🟢 ترويسة شروط التفعيل باللون التركوازي الغامق ومفتاح الإضافة على اليسار المقابل تماماً -->
        <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none shrink-0">
          <div class="flex items-center gap-2">
            <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">2</span>
            <span class="font-extrabold text-white text-xs">شروط التفعيل المنطقية لحالة المريض</span>
          </div>
          <!-- زر الإضافة مدمج بجانب الأيقونة البيضاء على اليسار المقابل للعنوان -->
          <div class="flex items-center gap-3 select-none">
            <button 
              type="button" 
              @click="addCondition" 
              class="text-[9px] font-bold text-teal-200 bg-white/10 hover:bg-white/20 border border-white/10 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              + Add Condition
            </button>
            <Icon icon="solar:tuning-2-bold" class="w-5 h-5 text-white shrink-0" />
          </div>
        </div>

        <div class="p-6 flex-1 space-y-4">
          <!-- صفوف الشروط الديناميكية الموزعة بـ 12 عمود متجانس -->
          <div class="space-y-3 overflow-y-auto max-h-[220px] custom-scrollbar pr-1">
            <div 
              v-for="(cond, index) in ruleForm.conditions" 
              :key="index" 
              class="grid grid-cols-12 gap-2 items-center bg-slate-50/50 p-2.5 border border-slate-100 rounded-xl animate-[fadeIn_0.2s_ease-out]"
            >
              <!-- 1. أداة الربط المنطقي -->
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

              <!-- 2. الحساس / الحقل -->
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

              <!-- 3. المعامل المنطقي -->
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

              <!-- 4. القيمة المطلوب قياسها -->
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

              <!-- 5. حقل مهلة استدامة اختيارية مخصصة لهذا الحساس -->
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

              <!-- 6. زر الحذف -->
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

      <!-- القسم الثالث: الإجراء والتوصية السريرية والمستلم (ترويسة تركوازية وأيقونة بيضاء مقابلة لليسار) -->
      <div class="lg:col-span-12 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-0 overflow-hidden flex flex-col">
        <!-- 🟢 ترويسة الإجراء باللون التركوازي الغامق والأيقونة البيضاء على اليسار المقابل تماماً للعنوان وبدون أي حدود -->
        <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none shrink-0">
          <div class="flex items-center gap-2">
            <span class="w-5 h-5 bg-white/10 text-teal-300 border border-white/5 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">3</span>
            <span class="font-extrabold text-white text-xs">الإجراء وقنوات التواصل (Action & Notification)</span>
          </div>
          <Icon icon="solar:shield-check-bold" class="w-5 h-5 text-white shrink-0" />
        </div>

        <div class="p-6 space-y-4">
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
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue' // 🟢 دمج الـ computed في سطر الاستدعاء الرئيسي الفردي والوحيد
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue' // 🟢 استيراد أيقونات إيكونيفاي الفردي والوحيد لمنع كراش المجمع
import api from '../api'

const router = useRouter()
const route = useRoute()
const patientId = ref(route.params.id) 

const loading = ref(false)
const isEditing = ref(false)
const currentRuleId = ref(null)

const globalRules = ref([]) 

const ruleForm = ref({
  name: '',
  conditions: [
    { field: 'heart_rate', op: '>', value: 110, connector: 'AND', duration_seconds: null },
    { field: 'activity_level', op: '==', value: 0, connector: 'AND', duration_seconds: null }
  ],
  severity: 'high',
  duration_mode: 'global', 
  duration_seconds: 0, 
  overridden_rules: [], 
  action_template: '',
  channels: ['UI Alert'],
  recipient: 'treating_doctor_only',
  is_active: true
})

const fetchGlobalRules = async () => {
  try {
    const res = await api.get('/api/rules/') 
    globalRules.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('فشل تحميل البروتوكولات السريرية العامة:', e)
  }
}

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
    
    const hasCustomDurations = Array.isArray(condObj.conditions) && condObj.conditions.some(c => c.duration_seconds !== null)
    const mode = hasCustomDurations ? 'custom' : 'global'

    ruleForm.value = {
      name: rule.name || '',
      conditions: Array.isArray(condObj.conditions) && condObj.conditions.length > 0 
        ? JSON.parse(JSON.stringify(condObj.conditions)) 
        : [{ field: 'heart_rate', op: '>', value: 110, connector: 'AND', duration_seconds: null }],
      severity: rule.severity || 'medium',
      duration_mode: mode, 
      duration_seconds: condObj.duration_seconds || rule.duration_seconds || 0,
      overridden_rules: rule.overridden_rules || [], 
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
          duration_seconds: ruleForm.value.duration_mode === 'custom'
            ? (c.duration_seconds !== null && c.duration_seconds !== '' ? Number(c.duration_seconds) : null)
            : null
        })),
        channels: ruleForm.value.channels,
        recipient: ruleForm.value.recipient,
        duration_seconds: ruleForm.value.duration_mode === 'global' ? Number(ruleForm.value.duration_seconds || 0) : 0
      },
      overridden_rules: ruleForm.value.overridden_rules, 
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
  await fetchGlobalRules() 
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