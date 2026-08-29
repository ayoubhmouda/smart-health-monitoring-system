<!-- frontend/src/components/MetricCard.vue -->
<template>
  <div :class="[
    'p-3.5 sm:p-4 rounded-2xl flex flex-col justify-between h-[155px] sm:h-[160px] transition-all duration-300 shadow-sm hover:shadow-md w-full bg-white',
    cardBorderClass
  ]">
    <!-- الهيدر العلوي: الأيقونة وشارة الحالة -->
    <div class="flex items-center justify-between gap-2">
      <div :class="[
        'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300',
        iconBgClass
      ]">
        <!-- Heart Icon -->
        <svg v-if="props.icon === 'heart'" class="w-4 h-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>

        <!-- Oxygen SPO2 Icon -->
        <svg v-else-if="props.icon === 'o2'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>

        <!-- Blood Pressure Icon -->
        <svg v-else-if="props.icon === 'bp'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>

        <!-- Respiratory / Wind / Cloud Icon -->
        <svg v-else-if="isRespIcon" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.59 4.59A2 2 0 1111 8H2m10.59 11.41A2 2 0 1014 16H2m15.73-8.27A2.5 2.5 0 1119.5 12H2" />
        </svg>

        <!-- Bolt Icon -->
        <svg v-else-if="props.icon === 'bolt' || props.icon === 'activity'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>

        <!-- Temp Icon -->
        <svg v-else-if="props.icon === 'fire' || props.icon === 'temp'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
        </svg>

        <!-- Home Icon -->
        <svg v-else-if="props.icon === 'home'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      </div>

      <!-- Badge للحالة -->
      <div v-if="!isSpecialCard">
        <span :class="['px-2 py-0.5 rounded-full text-[10px] font-bold border flex items-center gap-1 transition-colors duration-300', statusBadgeClass]">
          <span class="w-1.5 h-1.5 rounded-full" :class="statusDotClass"></span>
          {{ statusLabel }}
        </span>
      </div>
      <div v-else-if="props.icon === 'bolt' || props.icon === 'activity'" class="inline-flex px-2 py-0.5 bg-cyan-50 border border-cyan-100 rounded-full text-[10px] text-cyan-700 font-bold">
        متابع حركي
      </div>
      <div v-else-if="props.icon === 'home'" class="inline-flex px-2 py-0.5 bg-amber-50 border border-amber-100 rounded-full text-[10px] text-amber-700 font-bold">
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
          <div class="w-7 h-7 rounded-lg bg-cyan-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
            <svg v-if="activityLevel === 0" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 18h20M4 18v-7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v7M4 13h16"/>
              <circle cx="8" cy="7" r="1.5"/>
            </svg>
            <svg v-else-if="activityLevel === 1" class="w-4 h-4 animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 18h20M4 18v-7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v7M4 13h16"/>
              <circle cx="7" cy="8" r="1.5"/>
              <path d="M17 5l2-2M20 7h2"/>
            </svg>
            <svg v-else-if="activityLevel === 2" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="13" cy="4" r="2"/><path d="M7 21l3-4 2 2 3 3M12 11l-2 4-4 2M10 8l4 1 3 4"/>
            </svg>
            <svg v-else-if="activityLevel === 3" class="w-4 h-4 animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="15" cy="4" r="2"/><path d="M18 19l-4-4 2-5-4 1-2 4M7 11l4-2 3 3M9 20l3-5"/>
            </svg>
            <span v-else class="text-xs font-bold">{{ props.value }}</span>
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

      <!-- 🟢 شريط القيم المرجعية والحدود القصوى والدنيا الموقعة أسفل شريط التحميل مباشرة (مطابق للقطة 100%) -->
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

const props = defineProps({
  title: String,
  value: [String, Number],
  status: String,
  icon: String,
  unit: String,
  minVal: { type: [String, Number], default: null }, 
  maxVal: { type: [String, Number], default: null }  
})

// 🟢 حساب القيمة الدنيا الفسيولوجية المطلقة للحساس لتثبيتها يميناً (تطابق اللقطة)
const absoluteMin = computed(() => {
  if (props.icon === 'heart') return '30'
  if (props.icon === 'o2') return '70'
  if (props.icon === 'bp') return '60/40'
  if (isRespIcon.value) return '5'
  if (props.icon === 'fire' || props.icon === 'temp') return '32'
  return null
})

// 🟢 حساب القيمة القصوى الفسيولوجية المطلقة للحساس لتثبيتها يساراً (تطابق اللقطة)
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
  if (isRespIcon.value) return 'br/min'
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

const iconBgClass = computed(() => {
  if (isRespIcon.value) return 'bg-sky-50 text-sky-500'
  switch (props.icon) {
    case 'heart': return 'bg-rose-50 text-rose-500'
    case 'o2': return 'bg-emerald-50 text-emerald-500'
    case 'bp': return 'bg-purple-50 text-purple-500'
    case 'bolt': case 'activity': return 'bg-cyan-50 text-cyan-500'
    case 'fire': case 'temp': return 'bg-orange-50 text-orange-500'
    case 'home': return 'bg-amber-50 text-amber-500'
    default: return 'bg-slate-50 text-slate-500'
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