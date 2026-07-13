<template>
  <div class="bg-[#13222c] p-4 rounded-xl border border-slate-700/50">
    <h3 class="text-sm font-semibold text-slate-300 mb-4">أحدث تنبؤ</h3>
    
    <!-- إذا لم توجد تنبؤات بعد -->
    <div v-if="!insight" class="flex items-center justify-center py-6">
      <p class="text-slate-500 text-sm">لا توجد تنبؤات حالية</p>
    </div>

    <!-- تفاصيل التنبؤ -->
    <div v-else :class="panelBgClass" class="p-4 rounded-lg transition-colors duration-300">
      <div class="flex items-center justify-between mb-3">
        <span class="text-xs text-slate-400">{{ formatTime(insight.detected_at) }}</span>
        <span :class="severityBadgeClass" class="text-xs px-2 py-1 rounded-full font-bold">
          {{ severityLabel }}
        </span>
      </div>
      
      <div class="text-white font-bold text-lg mb-1">
        {{ insight.insight_type === 'predicted_risk' ? 'خطر متوقع' : 'شذوذ حالي' }}
      </div>
      
      <div class="text-slate-300 text-sm mb-2">
        {{ insightDescription }}
      </div>

      <!-- شريط الثقة -->
      <div class="w-full bg-slate-700 rounded-full h-2 mt-3">
        <div
          :class="confidenceBarColor"
          class="h-2 rounded-full transition-all duration-500"
          :style="{ width: (insight.confidence * 100) + '%' }"
        ></div>
      </div>
      <p class="text-xs text-slate-400 mt-2">
        نسبة الثقة: {{ (insight.confidence * 100).toFixed(1) }}%
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  insight: { type: Object, default: null }
})

// تنسيق الوقت
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('ar')
}

// وصف مبسط للتنبؤ
const insightDescription = computed(() => {
  if (!props.insight) return ''
  const s = props.insight.severity
  if (s === 'high' || s === 'critical') return 'يوجد خطر مرتفع يستدعي التدخل الفوري.'
  if (s === 'medium') return 'يوجد خطر متوسط. يرجى مراقبة المريض عن كثب.'
  return 'المؤشرات الحيوية ضمن الحدود الطبيعية.'
})

// لون الخلفية حسب الشدة
const panelBgClass = computed(() => {
  const s = props.insight?.severity
  if (s === 'high' || s === 'critical') return 'bg-rose-900/30 border border-rose-500/50'
  if (s === 'medium') return 'bg-amber-900/30 border border-amber-500/50'
  return 'bg-emerald-900/30 border border-emerald-500/50'
})

// شارة الخطورة
const severityLabel = computed(() => {
  const s = props.insight?.severity
  if (s === 'high') return 'مرتفع'
  if (s === 'critical') return 'حرج'
  if (s === 'medium') return 'متوسط'
  return 'منخفض'
})

const severityBadgeClass = computed(() => {
  const s = props.insight?.severity
  if (s === 'high' || s === 'critical') return 'bg-rose-500/20 text-rose-300'
  if (s === 'medium') return 'bg-amber-500/20 text-amber-300'
  return 'bg-emerald-500/20 text-emerald-300'
})

// لون شريط الثقة
const confidenceBarColor = computed(() => {
  const s = props.insight?.severity
  if (s === 'high' || s === 'critical') return 'bg-rose-500'
  if (s === 'medium') return 'bg-amber-500'
  return 'bg-emerald-500'
})
</script>