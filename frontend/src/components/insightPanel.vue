<!-- insightPanel.vue -->
<template>
  <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/50">
    <h3 class="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
      <!-- أيقونة الاستدلال الذكي التوضيحية -->
      <svg class="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      <span>أحدث تنبؤ</span>
    </h3>
    
    <!-- واجهة نظيفة وهادئة في حال غياب التنبؤات السريرية حالياً -->
    <div v-if="!insight" class="flex flex-col items-center justify-center py-10 bg-slate-50/50 rounded-xl border border-dashed border-slate-100">
      <svg class="w-8 h-8 text-slate-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-slate-400 text-xs font-semibold">لا توجد تنبؤات حالية</p>
    </div>

    <!-- كارت تفاصيل التنبؤ الذكي بألوان الباستيل الناعمة والراقية (Soft Pastel Card) -->
    <div v-else :class="panelBgClass" class="p-4 rounded-xl transition-all duration-300">
      <div class="flex items-center justify-between mb-3.5">
        <!-- طابع الوقت الأنيق والواضح للتحقق السريري -->
        <div class="flex items-center gap-1.5 text-[10px] text-slate-500 font-semibold font-mono uppercase tracking-wide">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>آخر تحديث: {{ formatTime(insight.detected_at) }}</span>
        </div>
        
        <!-- ملصق الخطورة الذكي عالي التباين والأناقة (Clinical Severity Badge) -->
        <span :class="severityBadgeClass" class="text-[10px] px-2.5 py-1 rounded-full font-bold border transition-colors duration-300">
          {{ severityLabel }}
        </span>
      </div>
      
      <!-- نوع التنبؤ الذكي الصادر برمجياً -->
      <div class="text-slate-800 font-black text-lg mb-1 tracking-tight">
        {{ insight.insight_type === 'predicted_risk' ? 'خطر متوقع' : 'شذوذ حالي' }}
      </div>
      
      <!-- نص الوصف الطبي والسريري بخط فاحم واضح ومقروء للمتابعة -->
      <div class="text-slate-600 text-xs font-medium leading-relaxed mb-3">
        {{ insightDescription }}
      </div>

      <!-- شريط الثقة العصري البسيط (Minimalist Progress Bar) -->
      <div class="space-y-2 mt-4 pt-3 border-t border-slate-100">
        <div class="flex justify-between items-center text-[11px] font-bold text-slate-500">
          <span>نسبة الثقة في التنبؤ</span>
          <span class="font-extrabold text-slate-800">{{ (insight.confidence * 100).toFixed(1) }}%</span>
        </div>
        <!-- مجرى شريط التحميل باللون الرمادي الجليدي النقي -->
        <div class="w-full bg-slate-100 rounded-full h-2">
          <div
            :class="confidenceBarColor"
            class="h-2 rounded-full transition-all duration-500 shadow-sm"
            :style="{ width: (insight.confidence * 100) + '%' }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  insight: { type: Object, default: null }
})

// تنسيق الوقت بطريقة طبية نظيفة ومبسطة بالدقة المطلوبة
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit' })
}

// الوصف الطبي والسريري الموجه للطبيب بناءً على شدة الخطر
const insightDescription = computed(() => {
  if (!props.insight) return ''
  const s = props.insight.severity
  if (s === 'high' || s === 'critical') return 'يوجد تدهور فسيولوجي حرج. يرجى التدخل الفوري لسلامة المريض.'
  if (s === 'medium') return 'يوجد خطر سريري متوقع. يرجى مراقبة العلامات الحيوية عن كثب.'
  return 'العلامات الحيوية للمريض تقع بالكامل ضمن الحدود الآمنة والمستقرة.'
})

// تنسيق خلفيات الكروت الداخلية بألوان الباستيل الناعمة والراقية (Soft Pastel Palette)
const panelBgClass = computed(() => {
  const s = props.insight?.severity
  if (s === 'high' || s === 'critical') return 'bg-rose-50/60 border border-rose-100'
  if (s === 'medium') return 'bg-amber-50/60 border border-amber-100'
  return 'bg-emerald-50/60 border border-emerald-100'
})

// ترجمة شارات الخطورة اللفظية
const severityLabel = computed(() => {
  const s = props.insight?.severity
  if (s === 'high') return 'خطر مرتفع'
  if (s === 'critical') return 'خطر حرج'
  if (s === 'medium') return 'خطر متوسط'
  return 'مستقر'
})

// ملصقات الخطورة الدائرية الأنيقة (High-Contrast Badges)
const severityBadgeClass = computed(() => {
  const s = props.insight?.severity
  if (s === 'high' || s === 'critical') return 'bg-rose-100/60 text-rose-700 border-rose-200'
  if (s === 'medium') return 'bg-amber-100/60 text-amber-700 border-amber-200'
  return 'bg-emerald-100/60 text-emerald-700 border-emerald-200'
})

// ألوان شريط الثقة المضيئة والزاهية تماشياً مع الهوية
const confidenceBarColor = computed(() => {
  const s = props.insight?.severity
  if (s === 'high' || s === 'critical') return 'bg-rose-500'
  if (s === 'medium') return 'bg-amber-500'
  return 'bg-emerald-500'
})
</script>