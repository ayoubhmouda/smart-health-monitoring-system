<!-- SensorControl.vue -->
<template>
  <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/50 overflow-hidden">
    
    <!-- هيدر لوحة التحكم المركزية -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-5 border-b border-slate-100 gap-4">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-full bg-teal-50 flex items-center justify-center text-teal-600">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
        </div>
        <h3 class="text-xs font-bold text-slate-700 tracking-wider uppercase">
          لوحة محاكاة السيناريوهات السريرية المركزية
        </h3>
      </div>
      
      <!-- مؤشر التحميل والمزامنة الجليدي -->
      <div v-if="loading" class="text-xs font-mono font-bold text-teal-600 bg-teal-50 px-3 py-1 rounded-full animate-pulse">
        {{ $t('syncing') }}...
      </div>
    </div>

    <!-- واجهة التنبيه في حال غياب الأجهزة -->
    <div v-if="sensors.length === 0 && !loading" class="text-slate-400 text-xs text-center py-6">
      {{ $t('no_sensors') }}
    </div>

    <div v-else class="space-y-6">
      <!-- 🟢 أولاً: التحكم المركزي الموحد (الـ Master Controller العريض) -->
      <div class="bg-slate-50/50 p-5 rounded-2xl border border-slate-100 grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
        
        <div class="lg:col-span-4 space-y-1">
          <span class="text-xs font-bold text-slate-700 block">سيناريو تدهور الحالة الموحد</span>
          <span class="text-[10px] text-slate-400 block">يتحكم بملفات جميع أجهزة المريض الـ 8 في نفس اللحظة</span>
        </div>

        <!-- أزرار التبديل المركزية بين Simulated و Physical لكافة الأجهزة -->
        <div class="lg:col-span-3">
          <button 
            @click="toggleMasterSource"
            :class="masterSourceBtnClass"
            class="w-full text-xs font-bold py-2.5 px-4 rounded-xl transition-all duration-200 text-center border shadow-sm flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            <span>تبديل مصدر كافة الأجهزة</span>
          </button>
        </div>

        <!-- القائمة المنسدلة الموحدة لجميع الحساسات المحاكية -->
        <div class="lg:col-span-5 flex justify-end">
          <select
            v-if="isMasterSimulated"
            @change="changeMasterProfile($event.target.value)"
            class="w-full text-xs bg-white text-slate-700 border border-slate-200 rounded-xl py-2.5 pr-3 pl-2 focus:outline-none focus:border-teal-500 font-bold transition-all shadow-sm cursor-pointer text-right"
          >
            <option value="normal"> الوضع الطبيعي المستقر (Normal Base)</option>
            <option value="gradual_deterioration"> تدهور فسيولوجي تدريجي (Gradual 10 Min)</option>
            <option value="emergency_spike"> نوبة طوارئ حادة مفاجئة (Emergency Spike)</option>
            <option value="abnormal"> مؤشرات شاذة منخفضة (Concerning Low)</option>
            <option value="recovery"> مرحلة الاستشفاء والنقاهة (Recovery)</option>
            <option value="random"> محاكاة عشوائية (Random)</option>
          </select>
          <div v-else class="w-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-bold py-2.5 px-4 rounded-xl text-center flex items-center justify-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span>كافة الأجهزة متصلة بالبث المباشر (PHYSICAL)</span>
          </div>
        </div>

      </div>

      <!-- 🛠️ ثانياً: التحكم اليدوي والمنفرد المطوي (Advanced Manual Control) -->
      <details class="group border border-slate-100 rounded-2xl overflow-hidden">
        <summary class="flex justify-between items-center p-4 bg-slate-50/30 hover:bg-slate-50 cursor-pointer select-none text-xs font-bold text-slate-500 transition-colors">
          <span>خيارات التحكم المتقدم والمنفرد بالأجهزة (اختياري)</span>
          <svg class="w-4 h-4 text-slate-400 group-open:rotate-180 transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </summary>

        <div class="p-4 bg-white grid grid-cols-1 md:grid-cols-2 gap-3 border-t border-slate-100">
          <template v-for="sensor in pairedSensors" :key="sensor.id">
            <div 
              class="bg-slate-50/30 p-3 rounded-xl border border-slate-100 grid grid-cols-12 gap-2 items-center w-full overflow-hidden"
              :class="{ 'md:col-span-2': sensor.sensor_type?.name === 'Activity Level' }"
            >
              
              <div class="col-span-4 flex flex-col min-w-0">
                <span class="text-xs font-bold text-slate-700 truncate block">
                  {{ translateSensorName(sensor.sensor_type?.name) }}
                </span>
                <span class="text-[9px] font-mono text-slate-400 truncate block mt-0.5">
                  ID: {{ sensor.device_identifier }}
                </span>
              </div>

              <div class="col-span-3 w-full">
                <button 
                  @click="toggleSource(sensor)" 
                  :class="sourceBtnClass(sensor)" 
                  class="w-full text-[10px] font-bold py-1.5 px-0.5 rounded-lg transition-all duration-200 text-center border truncate block"
                >
                  {{ sourceLabel(sensor) }}
                </button>
              </div>
              
              <div class="col-span-5 w-full flex justify-end min-w-0">
                <select
                  v-if="getConfig(sensor)?.source === 'SIMULATED'"
                  :value="getConfig(sensor)?.simulation_profile || 'normal'"
                  @change="changeProfile(sensor, $event.target.value)"
                  class="w-full text-[10px] bg-white text-slate-600 border border-slate-200 rounded-lg py-1.5 pr-2 pl-1 focus:outline-none focus:border-teal-500 font-bold transition-colors cursor-pointer text-right"
                >
                  <option value="normal">{{ $t('normal') }}</option>
                  <option value="abnormal">{{ $t('abnormal') }}</option>
                  <option value="gradual_deterioration">{{ $t('gradual_deterioration') }}</option>
                  <option value="emergency_spike">{{ $t('emergency_spike') }}</option>
                  <option value="random">{{ $t('random') }}</option>
                  <option value="custom">{{ $t('custom') }}</option>
                </select>
                
                <span v-else class="text-[10px] text-emerald-600 font-bold pl-2 tracking-wide flex items-center gap-1 select-none">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  <span>بث مباشر</span>
                </span>
              </div>

            </div>
          </template>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'

const { t } = useI18n()

const props = defineProps({ patientId: Number })
const sensors = ref([])
const loading = ref(false)

const translateSensorName = (name) => {
  if (!name) return t('custom')
  const key = name.toLowerCase().replace(/ /g, '_') 
  return t(key)
}

const pairedSensors = computed(() => {
  const list = [...sensors.value]
  const activity = list.find(s => s.sensor_type?.name === 'Activity Level')
  const others = list.filter(s => s.sensor_type?.name !== 'Activity Level')
  return [...others, ...(activity ? [activity] : [])]
})

const fetchSensors = async () => {
  if (!props.patientId) return
  loading.value = true
  try {
    const res = await api.get('/api/sensors/', { params: { monitored_element: props.patientId } })
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    const sensorIds = list.map(s => s.id)
    let configs = []
    
    if (sensorIds.length) {
      const cfgRes = await api.get('/api/data-source-configs/', { params: { sensor: sensorIds.join(',') } })
      configs = Array.isArray(cfgRes.data) ? cfgRes.data : (cfgRes.data.results || [])
    }
    
    list.forEach(s => { s._config = configs.find(c => c.sensor === s.id) || null })
    sensors.value = list
  } catch (e) { console.error(e) } finally { loading.value = false }
}

watch(() => props.patientId, fetchSensors, { immediate: true })

const getConfig = (s) => s._config

const sourceLabel = (s) => getConfig(s)?.source === 'PHYSICAL' ? t('physical') : t('simulated')

const sourceBtnClass = (s) => {
  return getConfig(s)?.source === 'PHYSICAL' 
    ? 'bg-emerald-50 text-emerald-600 border-emerald-100 hover:bg-emerald-100/50' 
    : 'bg-amber-50 text-amber-600 border-amber-100 hover:bg-amber-100/50'
}

// التحقق الفوري ما إذا كانت جميع الأجهزة حالياً في وضع المحاكاة لفتح الـ Master Selector
const isMasterSimulated = computed(() => {
  if (!sensors.value.length) return false
  return sensors.value.some(s => getConfig(s)?.source === 'SIMULATED')
})

const masterSourceBtnClass = computed(() => {
  return isMasterSimulated.value
    ? 'bg-emerald-50 text-emerald-700 border-emerald-100 hover:bg-emerald-100'
    : 'bg-amber-50 text-amber-700 border-amber-100 hover:bg-amber-100'
})

// 🟢 التحكم المركزي الموحد: تبديل مصدر جميع الأجهزة دفعة واحدة
const toggleMasterSource = async () => {
  if (!sensors.value.length) return
  loading.value = true
  const firstConfig = getConfig(sensors.value[0])
  if (!firstConfig) {
    loading.value = false
    return
  }
  const nextSource = firstConfig.source === 'SIMULATED' ? 'PHYSICAL' : 'SIMULATED'
  
  try {
    const promises = sensors.value
      .filter(s => getConfig(s))
      .map(s => api.patch(`/api/data-source-configs/${getConfig(s).id}/`, { source: nextSource }))
    
    await Promise.all(promises)
    sensors.value.forEach(s => {
      const cfg = getConfig(s)
      if (cfg) cfg.source = nextSource
    })
  } catch (e) {
    console.error('فشل تبديل المصدر الموحد:', e)
  } finally {
    loading.value = false
  }
}

// 🟢 التحكم المركزي الموحد: تغيير ملف محاكاة جميع الأجهزة الـ 8 في نفس اللحظة
const changeMasterProfile = async (profile) => {
  if (!sensors.value.length) return
  loading.value = true
  try {
    const promises = sensors.value
      .filter(s => getConfig(s) && getConfig(s).source === 'SIMULATED')
      .map(s => api.patch(`/api/data-source-configs/${getConfig(s).id}/`, { simulation_profile: profile }))
    
    await Promise.all(promises)
    sensors.value.forEach(s => {
      const cfg = getConfig(s)
      if (cfg && cfg.source === 'SIMULATED') cfg.simulation_profile = profile
    })
  } catch (e) {
    console.error('فشل تغيير سيناريو المحاكاة الموحد:', e)
  } finally {
    loading.value = false
  }
}

const toggleSource = async (s) => {
  const cfg = getConfig(s)
  if (!cfg?.id) return
  const ns = cfg.source === 'SIMULATED' ? 'PHYSICAL' : 'SIMULATED'
  try {
    await api.patch(`/api/data-source-configs/${cfg.id}/`, { source: ns })
    cfg.source = ns
  } catch (e) { console.error(e) }
}

const changeProfile = async (s, p) => {
  const cfg = getConfig(s)
  if (!cfg?.id) return
  try {
    await api.patch(`/api/data-source-configs/${cfg.id}/`, { simulation_profile: p })
    cfg.simulation_profile = p
  } catch (e) { console.error(e) }
}
</script>