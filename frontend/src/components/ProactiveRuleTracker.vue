<!-- frontend/src/components/ProactiveRuleTracker.vue -->
<template>
  <section class="bg-white rounded-[2rem] border border-slate-200 shadow-sm flex flex-col overflow-hidden transition-all duration-500 select-none">
    
    <!-- الترويسة الموحدة بهوية MediWatch التركوازية الغامقة والأيقونة الحرة -->
    <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-extrabold text-white leading-tight">
            المراقبة الاستباقية للبروتوكولات السريرية
          </h2>
          <span 
            v-if="activeProgressionsCount > 0" 
            class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-200 border border-amber-400/30 text-[9px] font-black animate-pulse"
          >
            {{ activeProgressionsCount }} قيد التحقق
          </span>
        </div>
        <p class="text-[10px] text-teal-200/60 mt-0.5 font-medium">
          رصد استدامة المؤشرات والتدخل الاستباقي قبل اكتمال مهلة الإنذار
        </p>
      </div>
      <Icon icon="solar:tuning-2-bold" class="w-6 h-6 text-white shrink-0" />
    </div>

    <div class="p-5 sm:p-6 space-y-4">
      
      <!-- الحالة الأولى: استقرار تام ولا توجد قواعد قيد الاكتمال -->
      <div 
        v-if="displayRules.length === 0" 
        class="py-8 px-4 text-center flex flex-col items-center justify-center gap-2.5 rounded-2xl bg-slate-50/50 border border-dashed border-slate-200 text-slate-400"
      >
        <Icon icon="solar:shield-check-bold" class="w-8 h-8 text-emerald-500/70" />
        <p class="text-xs font-extrabold text-slate-700">كافة المؤشرات مستقرة</p>
        <p class="text-[11px] font-medium text-slate-400">
          لا توجد بروتوكولات مخصصة أو عامة قيد التحقق أو تقترب من إطلاق الإنذار حالياً.
        </p>
      </div>

      <!-- الحالة الثانية: قائمة القواعد الجاري تتبع تقدمها الزمني -->
      <div v-else class="space-y-4">
        <div 
          v-for="rule in displayRules" 
          :key="rule.rule_id"
          class="p-4 rounded-2xl border transition-all duration-300 flex flex-col gap-3.5 bg-slate-50/60"
          :class="getCardBorderClass(rule.overall_progress)"
        >
          
          <!-- رأس كارت القاعدة: الاسم، الخطورة، ونسبة الاكتمال الإجمالية -->
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2 min-w-0">
              <span 
                class="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border font-mono shrink-0"
                :class="getSeverityBadgeClass(rule.severity)"
              >
                {{ rule.severity_display || rule.severity }}
              </span>
              <h3 class="font-extrabold text-slate-800 text-xs truncate">
                {{ rule.rule_name }}
              </h3>
              <span v-if="rule.is_patient_specific" class="text-[9px] bg-teal-50 text-teal-700 border border-teal-200 px-1.5 py-0.5 rounded-md font-bold shrink-0">
                خاص بالمريض
              </span>
            </div>

            <!-- النسبة الإجمالية للتقدم -->
            <div class="flex items-center gap-2 shrink-0">
              <span class="text-xs font-black font-mono" :class="getProgressTextClass(rule.overall_progress)">
                {{ rule.overall_progress }}%
              </span>
            </div>
          </div>

          <!-- شريط التقدم الإجمالي للقاعدة -->
          <div class="w-full bg-slate-200/80 h-2 rounded-full overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-500 ease-out"
              :class="getProgressBarColorClass(rule.overall_progress)"
              :style="{ width: `${rule.overall_progress}%` }"
            ></div>
          </div>

          <!-- تفاصيل الشروط الفرعية لكل حساس -->
          <div v-if="rule.conditions && rule.conditions.length > 0" class="pt-1 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div 
              v-for="(cond, cIdx) in rule.conditions" 
              :key="cIdx"
              class="p-2.5 rounded-xl bg-white border border-slate-200/80 flex flex-col gap-1.5 text-[10px]"
            >
              <div class="flex items-center justify-between font-bold">
                <span class="text-slate-700 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full" :class="cond.is_matching ? 'bg-amber-500 animate-ping' : 'bg-slate-300'"></span>
                  {{ cond.field_label }}: {{ cond.op }} {{ cond.target_value }}
                </span>
                <span class="font-mono text-slate-500">
                  {{ cond.sustained_seconds }}ث / {{ cond.target_duration }}ث
                </span>
              </div>

              <!-- شريط تقدم الحساس الفردي -->
              <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full transition-all duration-300"
                  :class="getProgressBarColorClass(cond.progress)"
                  :style="{ width: `${cond.progress}%` }"
                ></div>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useDoctorStore } from '../stores/doctor'

const props = defineProps({
  progressions: {
    type: Array,
    default: () => []
  }
})

const doctorStore = useDoctorStore()

// 🟢 فلترة القواعد الموجهة لدور المستخدم الحالي فقط
const displayRules = computed(() => {
  if (!Array.isArray(props.progressions)) return []
  
  const userRole = doctorStore.role?.toLowerCase() || localStorage.getItem('user_role')?.toLowerCase() || ''
  
  return [...props.progressions]
    .filter(rule => {
      const recipient = rule.recipient || 'doctor_and_caregiver'
      
      // إذا كانت القاعدة موجهة لكلا الدورين
      if (recipient === 'doctor_and_caregiver') return true
      
      // إذا كانت موجهة للطبيب فقط والمستخدم الحالي طبيب (أو مشرف)
      if (recipient === 'treating_doctor_only' && (userRole === 'doctor' || userRole === 'admin')) return true
      
      // إذا كانت موجهة لمقدم الرعاية والمستخدم الحالي مقدم رعاية
      if (recipient === 'caregiver_only' && (userRole === 'caregiver' || userRole === 'nurse')) return true
      
      return false
    })
    .sort((a, b) => (b.overall_progress || 0) - (a.overall_progress || 0))
})

const activeProgressionsCount = computed(() => {
  return displayRules.value.filter(r => r.overall_progress > 0).length
})

const getSeverityBadgeClass = (severity) => {
  const s = String(severity).toLowerCase()
  if (s === 'critical') return 'bg-rose-50 text-rose-700 border-rose-200'
  if (s === 'high') return 'bg-orange-50 text-orange-700 border-orange-200'
  return 'bg-yellow-50 text-yellow-700 border-yellow-200'
}

const getProgressBarColorClass = (progress) => {
  const p = Number(progress || 0)
  if (p >= 80) return 'bg-rose-500 animate-pulse'
  if (p >= 50) return 'bg-amber-500'
  return 'bg-teal-500'
}

const getProgressTextClass = (progress) => {
  const p = Number(progress || 0)
  if (p >= 80) return 'text-rose-600'
  if (p >= 50) return 'text-amber-600'
  return 'text-teal-600'
}

const getCardBorderClass = (progress) => {
  const p = Number(progress || 0)
  if (p >= 80) return 'border-rose-300 bg-rose-50/20'
  if (p >= 50) return 'border-amber-300 bg-amber-50/20'
  return 'border-slate-200'
}
</script>