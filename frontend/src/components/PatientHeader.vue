<!-- PatientHeader.vue -->
<template>
  <!-- بطاقة تعريف المريض والمزامنة، بنفس هوية السايدبار اللونية -->
  <div
    class="sticky top-3 z-20 w-full rounded-3xl border border-white/10 p-4 sm:p-5 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 select-none bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c]"
    dir="rtl"
  >
    <!-- القسم الأيمن: بيانات المريض -->
    <div class="flex items-start sm:items-center gap-3.5 min-w-0">
      <!-- الدائرة البيضاء مع أيقونة المستخدم -->
      <div
        class="w-13 h-13 sm:w-14 sm:h-14 rounded-full bg-white shadow-lg flex items-center justify-center overflow-hidden flex-shrink-0"
      >
        <User :size="32" class="sm:w-10 sm:h-10 text-[#0a3d48]" stroke-width="2" />
      </div>

      <div class="min-w-0 space-y-1.5">
        <div class="flex flex-wrap items-center gap-2">
          <h2 class="text-base sm:text-lg font-black text-white leading-tight tracking-tight truncate">
            {{ patient.full_name }}
          </h2>

          <span class="font-mono text-[11px] font-bold text-cyan-100/50">
            ID: {{ patient.id }}
          </span>

          <!-- زر الملف الطبي -->
          <router-link
            :to="`/patients/${patient.id}/medical-history`"
            class="medical-file-btn"
            title="عرض السجل الطبي للمريض"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>الملف الطبي</span>
            <ChevronLeft :size="13" class="opacity-70" />
          </router-link>
        </div>

        <!-- سطر البيانات الديموغرافية والسريرية، بلا بطاقات — نص وفواصل فقط -->
        <div class="flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-[13px] text-cyan-100/75 font-semibold">
          <span>{{ patient.age }} سنة</span>

          <span class="text-cyan-100/25">•</span>

          <!-- أيقونة الجنس من Lucide -->
          <span class="text-cyan-100/75 inline-flex items-center justify-center">
            <Mars v-if="genderLetter === 'M'" :size="16" stroke-width="2.5" />
            <Venus v-else-if="genderLetter === 'F'" :size="16" stroke-width="2.5" />
            <!-- إذا كانت القيمة غير معروفة لا نعرض شيئاً -->
          </span>

          <span class="text-cyan-100/25">•</span>

          <span>{{ getElementTypeText(patient.element_type) }}</span>
        </div>
      </div>
    </div>

    <!-- القسم الأيسر: لوحة المزامنة الحية، بلا بطاقات — عناصر مباشرة على خلفية البطاقة -->
    <div class="flex items-center justify-between md:justify-end gap-5 flex-shrink-0">
      <!-- حالة الاتصال + التايمر الدائري -->
      <div class="flex items-center gap-2.5">
        <div class="relative w-12 h-12 flex items-center justify-center flex-shrink-0">
          <!-- القرص الأبيض الداخلي -->
          <div class="absolute inset-[6px] rounded-full bg-white shadow-inner"></div>

          <svg class="relative w-12 h-12 -rotate-90" viewBox="0 0 44 44">
            <circle cx="22" cy="22" r="18" fill="none" stroke-width="3.5" class="text-white/15" stroke="currentColor" />
            <circle
              cx="22" cy="22" r="18" fill="none" stroke-width="3.5"
              stroke-linecap="round"
              :class="timerRingClass"
              stroke="currentColor"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
              class="transition-all duration-700 ease-linear"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <Check v-if="justUpdated" :size="15" stroke-width="3" class="text-emerald-800" />
            <span v-else class="text-[11px] font-mono font-black text-emerald-800">
              {{ countdown }}
            </span>
          </div>
        </div>

        <div class="flex flex-col leading-tight">
          <span
            class="w-2 h-2 rounded-full mb-1"
            :class="justUpdated ? 'bg-emerald-400' : isWsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400 animate-pulse'"
          ></span>
          <span class="text-[10px] font-bold" :class="justUpdated || isWsConnected ? 'text-emerald-300' : 'text-amber-300'">
            {{ justUpdated ? 'تحديث فوري' : isWsConnected ? 'مراقبة حية' : 'تحديث احتياطي' }}
          </span>
        </div>
      </div>

      <!-- توقيت آخر قراءة داخل بيضاوية بيضاء -->
      <div v-if="lastUpdatedTime" class="flex flex-col items-center justify-center bg-white rounded-full px-4 py-1.5 shadow-lg leading-tight">
        <span class="text-[8px] uppercase font-bold tracking-wider text-slate-400">آخر تحديث</span>
        <span class="font-mono font-black text-emerald-800 mt-0.5">{{ lastUpdatedTime }}</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronLeft, Check, Mars, Venus, User } from 'lucide-vue-next'

const props = defineProps({
  patient: { type: Object, required: true },
  isWsConnected: { type: Boolean, default: false },
  justUpdated: { type: Boolean, default: false },
  countdown: { type: Number, default: 30 },
  totalDuration: { type: Number, default: 30 },
  lastUpdatedTime: { type: String, default: '' }
})

// رمز الجنس M / F (يُستخدم للتحقق من الأيقونة)
const genderLetter = computed(() => {
  const g = props.patient.gender
  if (g === 'M' || g === 'Male') return 'M'
  if (g === 'F' || g === 'Female') return 'F'
  return '؟'
})

const getElementTypeText = (t) => {
  if (t === 'patient') return 'مريض'
  if (t === 'elderly') return 'مسن رعاية'
  if (t === 'disabled') return 'احتياجات خاصة'
  return 'حالة تحت المراقبة'
}

const formatDate = (rawDate) => {
  if (!rawDate) return 'غير متوفر'
  const date = new Date(rawDate)
  return isNaN(date.getTime()) ? 'غير متوفر' : date.toISOString().split('T')[0]
}

// حسابات التايمر الدائري
const RADIUS = 18
const circumference = 2 * Math.PI * RADIUS

const dashOffset = computed(() => {
  const total = props.totalDuration > 0 ? props.totalDuration : 30
  const ratio = props.justUpdated ? 1 : Math.min(Math.max(props.countdown / total, 0), 1)
  return circumference * (1 - ratio)
})

const timerRingClass = computed(() => {
  if (props.justUpdated) return 'text-emerald-400'
  return props.isWsConnected ? 'text-emerald-400' : 'text-amber-400'
})
</script>

<style scoped>
.medical-file-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 10px;
  font-weight: 700;
  color: #ecfeff;
  background: linear-gradient(135deg, #159aaa 0%, #087582 100%);
  border: 1px solid rgba(165, 243, 252, 0.2);
  padding: 0.35rem 0.7rem;
  border-radius: 0.75rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
  transition: all 180ms ease;
}

.medical-file-btn:hover {
  background: linear-gradient(135deg, #1aabba 0%, #0a8491 100%);
  border-color: rgba(165, 243, 252, 0.35);
  transform: translateY(-1px);
}
</style>