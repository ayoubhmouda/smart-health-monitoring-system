<!-- frontend/src/components/PatientHeader.vue -->
<template>
  <!-- البطاقة التركوازية الغامقة الموحدة لهوية نظام MediWatch مع حدود ناعمة وبانحناءات دائرية فاخرة -->
  <header 
    class="w-full rounded-[2rem] bg-gradient-to-r from-[#0d4553] to-[#072a33] p-5 shadow-xl flex flex-col md:flex-row items-center justify-between gap-4 border border-white/10 select-none text-white overflow-hidden relative"
  >
    <!-- لمسة إضاءة محيطية تراكوازية بالخلفية لزيادة الجمال البصري -->
    <div class="absolute -top-16 -right-16 w-36 h-36 bg-teal-400/10 rounded-full blur-3xl"></div>

    <!-- الجزء الأيمن: زر تفاعلي عريض جداً ومميز برمز الانتقال والسهم الجانبي الصريح على طرفه -->
    <router-link 
      :to="`/patients/${patient.id}/medical-history`"
      class="flex items-center justify-between gap-4 w-full md:w-auto md:min-w-[460px] z-10 cursor-pointer bg-white/5 border border-white/5 hover:border-white/12 hover:bg-white/10 rounded-3xl px-5 py-4 select-none transition-all duration-300 group/patient active:scale-[0.98]"
    >
      <div class="flex items-center gap-6 min-w-0">
        <!-- الأفتار الدائري الأبيض مع أيقونة مستخدم واضحة ومعيارية تتوسط الدائرة تماماً -->
        <div class="w-14 h-14 rounded-full bg-white flex items-center justify-center text-[#0a3d48] shrink-0 shadow-md border border-white/10 overflow-hidden">
          <Icon icon="basil:user-solid" class="w-13 h-13 shrink-0 transition-transform duration-300 group-hover/patient:scale-105" />
        </div>

        <div class="min-w-0">
          <!-- الاسم ومعرّف الهوية -->
          <div class="flex items-center gap-3">
            <span class="text-base md:text-lg font-black text-white leading-tight group-hover/patient:text-teal-300 transition-colors">
              {{ patient.full_name }}
            </span>

            <span class="text-[10px] font-black text-teal-300 font-mono tracking-tight bg-teal-500/15 border border-teal-900/20 px-3.5 py-0.5 rounded-full shrink-0"> 
              ID: {{ patient.id }} 
            </span> 
          </div>

          <!-- السطر الفرعي (تم توسيع المسافات بين العناصر) -->
          <div class="flex items-center gap-5 text-teal-100/70 text-xs font-bold mt-2 select-none">
            <!-- النوع معرّب -->
            <span>{{ getPatientTypeLabel(patient.element_type) }}</span>
            
            <!-- أيقونة الجنس -->
            <Icon 
              :icon="patient.gender === 'M' || patient.gender === 'ذكر' ? 'ph:gender-male-bold' : 'ph:gender-female-bold'" 
              :class="patient.gender === 'M' || patient.gender === 'ذكر' ? 'text-sky-400' : 'text-rose-400'"
              class="w-5 h-5 shrink-0 inline-block align-middle" 
            />
            
            <!-- العمر -->
            <span>{{ patient.age || 'غير محدد' }} سنة</span>
          </div>
        </div>
      </div>

      <!-- سهم الانتقال -->
      <div class="w-8 h-8 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center text-teal-300 shrink-0 group-hover/patient:bg-teal-500/20 group-hover/patient:border-teal-400/20 transition-all duration-300">
        <Icon 
          icon="solar:alt-arrow-left-bold" 
          class="w-4 h-4 text-teal-300 group-hover/patient:-translate-x-1 transition-transform duration-300" 
        />
      </div>
    </router-link>

    <!-- الجزء الأيسر: كبسولة المراقبة المحاطة بحد ليزري يمتلئ بالكامل باللون التراكوازي عند الثانية 30 وينقص تدريجياً وبسلاسة تامة ومستمرة دون تقطع -->
    <div 
      class="relative p-[1.5px] rounded-3xl overflow-hidden shrink-0 w-full md:w-auto md:min-w-[340px] z-10 flex items-center justify-center"
    >
      <!-- الحدود المضيئة التفاعلية (تم ربطها بـ CSS Property لضمان الحركة الدائرية الناعمة والمستمرة كالزبدة) -->
      <div 
        class="absolute inset-0 border-beam" 
        :style="{
          '--countdown-percent': countdownPercent,
          background: `conic-gradient(from 180deg, #2dd4bf 0%, #2dd4bf var(--countdown-percent), transparent var(--countdown-percent), transparent 100%)`
        }"
      ></div>

      <!-- 🟢 الكبسولة الداخلية (تقوم بقناع التدرج ومزودة بـ نبض خفيف ولطيف باللون الأخضر الداكن على الإطار والظل عند التحديث) -->
      <div 
        :class="justUpdated ? 'border-emerald-600/35 shadow-[0_0_12px_rgba(5,150,105,0.15)] bg-[#0a313b]/95' : 'border-white/5 shadow-inner bg-[#0a313b]/95'"
        class="w-full h-full rounded-[23px] p-3 px-6 flex items-center justify-between gap-6 select-none transition-all duration-300 backdrop-blur-md"
      >
        <!-- 1. آخر تحديث من السيرفر بالملي ثانية -->
        <div class="text-right flex flex-col gap-0.5">
          <span class="text-[9px] font-black text-teal-300 uppercase tracking-wider block font-sans">آخر تحديث فسيولوجي</span>
          <span class="text-xs font-bold font-mono text-white block">
            {{ lastUpdatedTime || 'الآن' }}
          </span>
        </div>
        
        <span class="w-px h-6 bg-white/10"></span>

        <!-- 2. نبض المراقبة الحية الأخضر التفاعلي -->
        <div class="flex items-center gap-1.5 select-none">
          <span class="flex h-2 w-2 relative shrink-0">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span class="text-[10px] font-black text-teal-100 uppercase tracking-wider"> دورة التحديث</span>
        </div>

        <span class="w-px h-6 bg-white/10"></span>

        <!-- 3. العداد الدائري: مكبر بالكامل لـ w-14 h-14، معبأ باللون الأبيض الناصع، وذو دوران انسيابي متصل ومستقر -->
        <div class="relative flex items-center justify-center shrink-0 select-none">
          <svg class="w-14 h-14 transform -rotate-90">
            <circle cx="28" cy="28" r="22" stroke="rgba(255,255,255,0.06)" stroke-width="3" fill="transparent" />
            <circle cx="28" cy="28" r="20" fill="white" />
            <circle 
              cx="28" cy="28" r="22" 
              stroke="rgb(45, 212, 191)" 
              stroke-width="3" 
              fill="transparent" 
              stroke-dasharray="138.23"
              :stroke-dashoffset="138.23 * (1 - countdown / 30)"
              class="transition-all duration-1000 ease-linear"
            />
          </svg>
          <span class="absolute text-[12px] font-black font-mono text-[#0a3d48] mt-0.5">
            {{ countdown }}
          </span>
        </div>
      </div>
    </div>

  </header>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue' // استيراد الأيقونات الموحدة إجبارياً لمنع تداخل الـ SVGs

const props = defineProps({
  patient: {
    type: Object,
    required: true
  },
  isWsConnected: {
    type: Boolean,
    default: false
  },
  justUpdated: {
    type: Boolean,
    default: false
  },
  countdown: {
    type: Number,
    default: 30
  },
  lastUpdatedTime: {
    type: String,
    default: ''
  }
})

// حساب النسبة المئوية للعداد التنازلي لإغلاق وفتح شريط ليزر الحدود المضيء ديناميكياً
const countdownPercent = computed(() => {
  return `${(props.countdown / 30) * 100}%`
})

// دالة حركية تقوم بترجمة مسمى حالة المريض تلقائياً للعربية لمنع ظهور أي كلمة إنجليزية بالواجهة
const getPatientTypeLabel = (type) => {
  if (!type) return 'مريض'
  const t = String(type).toLowerCase()
  if (t === 'patient') return 'مريض'
  if (t === 'elderly') return 'كبار السن'
  if (t === 'disabled') return 'ذوي الهمم'
  return type
}
</script>

<style scoped>
/* تسجيل حقل النسبة المئوية المخصصة لتمكين المتصفحات من معالجة الحركة الانتقالية التنازلية بنعومة كاملة كالزبدة وبدون أي تقطع */
@property --countdown-percent {
  syntax: '<percentage>';
  inherits: false;
  initial-value: 100%;
}

/* ربط الحركة بـ 1s linear لضمان تدفق الليزر بشكل مستمر متناسق مع دوران العداد الدائري */
.border-beam {
  transition: --countdown-percent 1s linear;
}

/* التحديث الحركي لـ ease-linear يضمن حركة التايمر الدائري بشكل انسيابي متصل وليس متقطع */
circle {
  transition: stroke-dashoffset 1s linear, stroke 0.3s ease;
}
</style>