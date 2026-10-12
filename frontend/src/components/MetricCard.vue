<!-- frontend/src/components/MetricCard.vue -->
<template>
  <div :class="[
    'p-3.5 sm:p-4 rounded-2xl flex flex-col justify-between h-[155px] sm:h-[160px] transition-all duration-300 shadow-sm hover:shadow-md w-full bg-white',
    cardBorderClass
  ]">
    <!-- الهيدر العلوي: الأيقونة الحرة وشارة الحالة -->
    <div class="flex items-center justify-between gap-2">
      
      <!-- 🟢 أيقونة حرة بدون بطاقة أو دائرة أو حدود بلون #0a3d48 المعتمد -->
      <div class="flex items-center justify-center flex-shrink-0">
        <Icon 
          :icon="iconName" 
          :class="['w-6 h-6 text-[#0a3d48]', props.icon === 'heart' ? 'animate-pulse' : '']" 
        />
      </div>

      <!-- Badge للحالة -->
      <div v-if="!isSpecialCard">
        <span :class="['px-2 py-0.5 rounded-full text-[10px] font-bold border flex items-center gap-1 transition-colors duration-300', statusBadgeClass]">
          <span class="w-1.5 h-1.5 rounded-full" :class="statusDotClass"></span>
          {{ statusLabel }}
        </span>
      </div>
      <div v-else-if="props.icon === 'bolt' || props.icon === 'activity'" class="inline-flex px-2 py-0.5 bg-[#0a3d48]/10 border border-[#0a3d48]/20 rounded-full text-[10px] text-[#0a3d48] font-bold">
        متابع حركي
      </div>
      <div v-else-if="props.icon === 'home'" class="inline-flex px-2 py-0.5 bg-[#0a3d48]/10 border border-[#0a3d48]/20 rounded-full text-[10px] text-[#0a3d48] font-bold">
        سياق بيئي
      </div>
    </div>

    <!-- عنوان الحساس -->
    <div class="text-slate-500 font-bold text-[11px] sm:text-xs uppercase tracking-tight leading-snug break-words">
      {{ props.title }}
    </div>

    <!-- القيمة وتنسيق الوحدة -->
    <div class="my-0.5">
      <!-- حالة النشاط الحركي -->
      <template v-if="props.icon === 'bolt' || props.icon === 'activity'">
        <div class="flex items-center gap-2 bg-slate-50/80 p-1.5 rounded-xl border border-slate-100">
          <div class="w-7 h-7 rounded-lg bg-[#0a3d48] text-white flex items-center justify-center flex-shrink-0 shadow-sm">
            <Icon :icon="activityIcon" class="w-4 h-4" />
          </div>
          <span class="text-xs sm:text-sm font-extrabold text-slate-800">{{ activityText }}</span>
        </div>
      </template>

      <!-- القيم الرقمية لجميع الحساسات مع إظهار الوحدة بشكل متناسق -->
      <template v-else>
        <div dir="ltr" class="flex items-baseline justify-end gap-1">
          <span class="text-lg sm:text-xl font-black text-slate-800 font-mono tracking-tight leading-none">
            {{ props.value }}
          </span>
          <span v-if="displayUnit" class="text-[11px] font-bold text-slate-500 font-sans">
            {{ displayUnit }}
          </span>
        </div>
      </template>
    </div>

    <div class="space-y-1">
      <!-- شريط مدى الحساس السفلي -->
      <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
        <div :class="['h-full rounded-full transition-all duration-500', barColorClass]" :style="{ width: barWidth }"></div>
      </div>

      <!-- شريط القيم المرجعية والحدود القصوى والدنيا الموقعة أسفل شريط التحميل -->
      <div v-if="props.minVal !== null || props.maxVal !== null" class="text-[10px] text-slate-400 font-bold select-none flex justify-between items-center px-1 font-mono leading-none">
        <span>{{ absoluteMin ?? '--' }}</span>
        <span class="text-slate-500 font-extrabold">{{ props.minVal }}-{{ props.maxVal }}</span>
        <span>{{ absoluteMax ?? '--' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  status: String,
  icon: String,
  unit: String,
  minVal: { type: [String, Number], default: null }, 
  maxVal: { type: [String, Number], default: null }  
})

// 🟢 تعيين الأيقونات الخمس المحددة من قبلك بالضبط
const iconName = computed(() => {
  if (isRespIcon.value) return 'bi:lungs-fill'
  switch (props.icon) {
    case 'heart': return 'streamline-flex:heart-rate-solid'
    case 'bp': return 'fontisto:blood-drop'
    case 'o2': return 'simple-icons:o2'
    case 'fire':
    case 'temp': return 'famicons:thermometer-outline'
    case 'bolt':
    case 'activity': return 'solar:running-2-bold'
    case 'home': return 'solar:home-2-bold'
    default: return 'streamline-flex:heart-rate-solid'
  }
})

// أيقونات الوضعية الحركية من Iconify
const activityIcon = computed(() => {
  switch (activityLevel.value) {
    case 0: return 'solar:sleeping-bold'
    case 1: return 'solar:armchair-bold'
    case 2: return 'mingcute:walk-fill'
    case 3: return 'solar:running-2-bold'
    default: return 'solar:user-bold'
  }
})

const absoluteMin = computed(() => {
  if (props.icon === 'heart') return '30'
  if (props.icon === 'o2') return '70'
  if (props.icon === 'bp') return '60/40'
  if (isRespIcon.value) return '5'
  if (props.icon === 'fire' || props.icon === 'temp') return '32'
  return null
})

const absoluteMax = computed(() => {
  if (props.icon === 'heart') return '200'
  if (props.icon === 'o2') return '100'
  if (props.icon === 'bp') return '190/110'
  if (isRespIcon.value) return '50'
  if (props.icon === 'fire' || props.icon === 'temp') return '42'
  return null
})

const isRespIcon = computed(() => {
  return ['cloud', 'resp', 'respiratory', 'wind', 'lungs'].includes(props.icon)
})

const isSpecialCard = computed(() => {
  return ['bolt', 'activity', 'home'].includes(props.icon)
})

const displayUnit = computed(() => {
  if (props.unit) return props.unit
  const valStr = String(props.value)
  if (valStr.includes('mmHg') || valStr.includes('bpm') || valStr.includes('°C') || valStr.includes('%')) {
    return '' 
  }
  if (props.icon === 'bp') return 'mmHg'
  if (props.icon === 'heart') return 'bpm'
  if (props.icon === 'o2') return '%'
  if (props.icon === 'fire' || props.icon === 'temp') return '°C'
  if (isRespIcon.value) return 'rpm'
  return ''
})

const activityLevel = computed(() => {
  const parsed = parseInt(props.value, 10)
  return isNaN(parsed) ? null : parsed
})

const activityText = computed(() => {
  switch (activityLevel.value) {
    case 0: return 'استلقاء'
    case 1: return 'حركة بسيطة'
    case 2: return 'مشي'
    case 3: return 'جري'
    default: return props.value
  }
})

const cardBorderClass = computed(() => {
  switch (props.status) {
    case 'Critical': return 'border-2 border-rose-500 shadow-rose-100/60 animate-pulse'
    case 'Caution': return 'border-2 border-amber-400 shadow-amber-100/60'
    default: return 'border border-slate-200/90 hover:border-slate-300'
  }
})

const statusLabel = computed(() => {
  switch (props.status) {
    case 'Critical': return 'خطر'
    case 'Caution': return 'انتباه'
    default: return 'مستقر'
  }
})

const statusBadgeClass = computed(() => {
  switch (props.status) {
    case 'Critical': return 'bg-rose-100/80 text-rose-800 border-rose-300 font-bold'
    case 'Caution': return 'bg-amber-100/80 text-amber-800 border-amber-300 font-bold'
    default: return 'bg-emerald-50 text-emerald-700 border-emerald-200/80 font-bold'
  }
})

const statusDotClass = computed(() => {
  switch (props.status) {
    case 'Critical': return 'bg-rose-500'
    case 'Caution': return 'bg-amber-500'
    default: return 'bg-emerald-500'
  }
})

const barColorClass = computed(() => {
  switch (props.status) {
    case 'Critical': return 'bg-rose-500'
    case 'Caution': return 'bg-amber-400'
    default: return 'bg-emerald-500'
  }
})

const barWidth = computed(() => {
  if (props.status === 'Critical') return '100%'
  if (props.status === 'Caution') return '75%'
  return '60%'
})
</script>