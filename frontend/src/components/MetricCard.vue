<template>
  <div :class="[
    'bg-[#13222c] p-4 rounded-xl border flex-shrink-0 w-[155px] sm:w-auto snap-start', 
    props.color, 
    'transition-all duration-300 hover:border-opacity-60 shadow-lg shadow-black/20'
  ]">
    <div class="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-1">
      <svg v-if="props.icon === 'heart'" class="w-4 h-4 text-rose-400 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
      <svg v-else-if="props.icon === 'o2'" class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
      <svg v-else-if="props.icon === 'temp'" class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <svg v-else-if="props.icon === 'bp'" class="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
      <svg v-else-if="props.icon === 'activity'" class="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
      <span>{{ props.title }}</span>
    </div>
    
    <div class="text-xl sm:text-2xl font-black text-white mt-1.5 mb-2 font-mono tracking-tight">{{ props.value }}</div>
    
    <div v-if="props.icon !== 'activity'" class="flex items-center justify-between text-[11px] font-bold">
      <span :class="statusColorClass">// {{ statusLabel }}</span>
    </div>
    <div v-else class="text-[10px] text-slate-500 font-mono tracking-wide uppercase">
      {{ $t('kinetic_tracker') }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n' // استدعاء نظام الترجمة لحساب الحالات برمجياً

const props = defineProps({ title: String, value: String, status: String, color: String, icon: String })
const { t } = useI18n()

// جلب نصوص الحالات الطبية بناءً على اللغة الحالية المفعلة في المشروع
const statusLabel = computed(() => {
  switch (props.status) { 
    case 'Critical': return t('status_critical'); 
    case 'Caution': return t('status_caution'); 
    case 'Good': return t('status_good'); 
    default: return t('status_normal'); 
  }
})

const statusColorClass = computed(() => {
  switch (props.status) { case 'Critical': return 'text-rose-400 drop-shadow-[0_0_4px_rgba(244,63,94,0.2)]'; case 'Caution': return 'text-amber-400'; default: return 'text-emerald-400'; }
})
</script>