<!-- frontend/src/components/insightPanel.vue -->
<template>
  <!-- الكارت الأب المطور بإنحناءات دائرية فاخرة ومحكمة ومقاومة للتمدد العشوائي -->
  <div class="bg-white rounded-[2rem] border border-slate-200 shadow-sm flex flex-col overflow-hidden">
    
    <!-- 🟢 ترويسة كارت الذكاء الاصطناعي باللون التركوازي الغامق والأيقونة البيضاء الصريحة على اليسار المقابل للعنوان -->
    <div class="bg-[#0a3d48] text-white p-5 rounded-t-[2rem] flex items-center justify-between gap-3 select-none">
      <div class="min-w-0">
        <h3 class="text-sm font-extrabold text-white leading-tight">
          أحدث تنبؤ للعلامات
        </h3>
        <p class="text-[10px] text-teal-200/60 mt-0.5 font-medium">
          استبصارات الذكاء الاصطناعي 
        </p>
      </div>
      <!-- الأيقونة بيضاء ناصعة وبدون حدود في الجهة المقابلة للعنوان -->
      <Icon icon="solar:bolt-bold" class="w-6 h-6 text-white shrink-0 animate-pulse" />
    </div>

    <!-- جسد الكارت المصفى بمسافاته المحددة مسبقاً وتفاصيله الحية -->
    <div class="p-5 flex flex-col gap-4">
      
      <!-- واجهة نظيفة وهادئة في حال غياب التنبؤات السريرية حالياً مع استخدام إيكونيفاي فقط -->
      <div v-if="!insight" class="flex flex-col items-center justify-center py-12 bg-slate-50 border border-slate-100 rounded-2xl select-none">
        <Icon icon="solar:shield-check-bold" class="w-10 h-10 text-slate-300 mb-2 shrink-0" />
        <p class="text-slate-400 text-xs font-black">لا توجد تنبؤات حالية</p>
      </div>

      <!-- كارت تفاصيل التنبؤ الذكي بألوان الباستيل الناعمة والراقية -->
      <div v-else :class="panelBgClass" class="p-4 rounded-2xl transition-all duration-300">
        <div class="flex items-center justify-between mb-3.5 select-none">
          <!-- طابع الوقت الأنيق الموحد بأيقونة إيكونيفاي فقط -->
          <div class="flex items-center gap-1.5 text-[10px] text-slate-500 font-bold font-mono uppercase tracking-wide">
            <Icon icon="solar:clock-circle-bold" class="w-3.5 h-3.5 text-slate-400" />
            <span>آخر تحديث فسيولوجي: {{ formatTime(insight.detected_at) }}</span>
          </div>
          
          <!-- ملصق الخطورة السريري الموحد لدرجة خطورة التنبؤ -->
          <span :class="severityBadgeClass" class="text-[9px] px-2.5 py-0.5 rounded-full font-black border uppercase tracking-wider transition-colors duration-300">
            {{ severityLabel }}
          </span>
        </div>
        
        <!-- نوع التنبؤ الذكي الصادر برمجياً -->
        <div class="text-slate-800 font-black text-lg mb-1 tracking-tight select-none">
          {{ insight.insight_type === 'predicted_risk' ? 'خطر متوقع' : 'شذوذ حالي المظهر' }}
        </div>
        
        <!-- نص الوصف الطبي والسريري بخط واضح ومقروء للمتابعة -->
        <div class="text-slate-600 text-xs font-bold leading-relaxed mb-3">
          {{ insightDescription }}
        </div>

        <!-- شريط الثقة العصري البسيط (Minimalist Progress Bar) -->
        <div class="space-y-2 mt-4 pt-3 border-t border-slate-100/85">
          <div class="flex justify-between items-center text-[10px] font-black text-slate-500 select-none">
            <span>نسبة الثقة في التنبؤ المالي</span>
            <span class="font-black text-slate-800 font-mono">{{ (insight.confidence * 100).toFixed(1) }}%</span>
          </div>
          <!-- مجرى شريط التحميل باللون الرمادي الجليدي النقي -->
          <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              :class="confidenceBarColor"
              class="h-2 rounded-full transition-all duration-500 shadow-sm"
              :style="{ width: (insight.confidence * 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue' // استيراد الأيقونات الموحدة إجبارياً لمنع تداخل الـ SVGs

const props = defineProps({
  insight: { type: Object, default: null }
})

// تنسيق الوقت بطريقة طبية نظيفة ومبسطة
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

// تنسيق خلفيات الكروت الداخلية بألوان الباستيل الناعمة والراقية
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

// ملصقات الخطورة الدائرية الأنيقة
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