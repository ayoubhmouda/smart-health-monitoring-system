<!-- MetricCard.vue -->
<template>
  <div :class="[
    'bg-white p-5 rounded-2xl border border-slate-100 flex flex-col justify-between h-full transition-all duration-300 hover:border-slate-200 shadow-sm shadow-slate-100/50 hover:shadow-md'
  ]">
    <div class="flex items-start gap-2.5 sm:gap-3 text-xs font-semibold text-slate-500 mb-2">
      <!-- حاوية الأيقونة الطبية ذات الخلفية الملونة الناعمة والشفافة (Soft Pastel Circle) -->
      <div :class="[
        'w-8 h-8 rounded-full flex items-center justify-center transition-transform duration-300 flex-shrink-0',
        iconBgClass
      ]">
        <!-- 1. أيقونة نبض القلب المضيئة والنابضة (heart) -->
        <svg v-if="props.icon === 'heart'" class="w-4 h-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>

        <!-- 2. أيقونة تشبع الأكسجين السريرية النظيفة (o2) -->
        <svg v-else-if="props.icon === 'o2'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>

        <!-- 3. أيقونة ضغط الدم البنفسجية المعتمدة (bp) -->
        <svg v-else-if="props.icon === 'bp'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>

        <!-- 🟢 4. أيقونة البرق المتوهج (bolt) المخصصة لحساس النشاط الحركي كما طلبت -->
        <svg v-else-if="props.icon === 'bolt'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>

        <!-- 5. أيقونة لهب الحرارة لدرجة حرارة الجسم (fire) -->
        <svg v-else-if="props.icon === 'fire'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
        </svg>

        <!-- 🟢 6. أيقونة الرياح والتنفس الانسيابية (Wind) المربوطة بمسمى cloud لمعدل التنفس كما طلبت -->
        <svg v-else-if="props.icon === 'cloud'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.59 4.59A2 2 0 1111 8H2m10.59 11.41A2 2 0 1014 16H2m15.73-8.27A2.5 2.5 0 1119.5 12H2" />
        </svg>

        <!-- 7. أيقونة منزل السياق البيئي لـ درجة حرارة الغرفة (home) -->
        <svg v-else-if="props.icon === 'home'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      </div>
      <!-- جعلنا حجم خط العنوان ديناميكياً ليلتفت لسطرين بنعومة بالغة دون اقتطاع -->
      <span class="text-slate-600 font-bold text-[10px] sm:text-xs whitespace-normal leading-tight flex-1 select-none">{{ props.title }}</span>
    </div>
    
    <!-- القيمة الحيوية الصريحة بالخط الفاحم الفاخر -->
    <div class="text-2xl font-extrabold text-slate-800 mt-1 mb-2 font-mono tracking-tight">{{ props.value }}</div>
    
    <!-- ملصقات الحالة الطبية دقيقة التلوين والدائرية (Micro-Badges) -->
    <div v-if="props.icon !== 'bolt' && props.icon !== 'home'" class="flex items-center">
      <span :class="[
        'px-2.5 py-1 rounded-full text-[10px] font-bold border transition-colors duration-300', 
        statusBadgeClass
      ]">
        {{ statusLabel }}
      </span>
    </div>
    <!-- ملصق النشاط التفاعلي النشط -->
    <div v-else-if="props.icon === 'bolt'" class="inline-flex px-2.5 py-1 bg-cyan-50 border border-cyan-100 rounded-full text-[10px] text-cyan-700 font-bold uppercase tracking-wide">
      متابع حركي
    </div>
    <!-- ملصق السياق البيئي المنزلي الهادئ -->
    <div v-else-if="props.icon === 'home'" class="inline-flex px-2.5 py-1 bg-amber-50 border border-amber-100 rounded-full text-[10px] text-amber-700 font-bold uppercase tracking-wide">
      سياق بيئي
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({ title: String, value: String, status: String, icon: String })
const { t } = useI18n()

const statusLabel = computed(() => {
  switch (props.status) { 
    case 'Critical': return t('status_critical'); 
    case 'Caution': return t('status_caution'); 
    case 'Good': return t('status_good'); 
    default: return t('status_normal'); 
  }
})

const iconBgClass = computed(() => {
  switch (props.icon) {
    case 'heart': return 'bg-rose-50 text-rose-500';
    case 'o2': return 'bg-emerald-50 text-emerald-500';
    case 'bp': return 'bg-purple-50 text-purple-500';
    case 'bolt': return 'bg-cyan-50 text-cyan-500';     // 🟢 خلفية البرق النحاسية للنشاط الحركي
    case 'fire': return 'bg-orange-50 text-orange-500';   
    case 'cloud': return 'bg-sky-50 text-sky-500';       // 🟢 خلفية الرياح التنفسية
    case 'home': return 'bg-amber-50 text-amber-500';     
    default: return 'bg-slate-50 text-slate-500';
  }
})

const statusBadgeClass = computed(() => {
  switch (props.status) { 
    case 'Critical': 
      return 'bg-rose-50 text-rose-600 border-rose-100'; 
    case 'Caution': 
      return 'bg-amber-50 text-amber-600 border-amber-100'; 
    case 'Good': 
      return 'bg-emerald-50 text-emerald-600 border-emerald-100'; 
    default: 
      return 'bg-slate-50 text-slate-600 border-slate-100'; 
  }
})
</script>