<template>
  <div class="bg-[#111c24] p-3 rounded-xl border border-[#16222f] shadow-lg overflow-hidden">
    <h3 class="text-[11px] font-bold text-slate-500 tracking-wider uppercase mb-3">
      {{ $t('sensor_control') }}
    </h3>
    
    <div v-if="loading" class="text-slate-500 text-xs text-center py-4 font-mono">
      {{ $t('syncing') }}
    </div>
    <div v-else-if="sensors.length === 0" class="text-slate-500 text-xs text-center py-4">
      {{ $t('no_sensors') }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-2">
      <template v-for="sensor in pairedSensors" :key="sensor.id">
        <div 
          class="bg-[#0b1319] p-2.5 rounded-lg border border-[#16222f] grid grid-cols-12 gap-1.5 items-center w-full overflow-hidden"
          :class="{ 'md:col-span-2': sensor.sensor_type?.name === 'Activity Level' }"
        >
          
          <div class="col-span-4 flex flex-col min-w-0">
            <span class="text-xs font-bold text-slate-200 truncate block select-none">
              {{ translateSensorName(sensor.sensor_type?.name) }}
            </span>
            <span class="text-[9px] font-mono text-slate-600 truncate block mt-0.5">
              ID: {{ sensor.device_identifier }}
            </span>
          </div>

          <div class="col-span-3 w-full">
            <button 
              @click="toggleSource(sensor)" 
              :class="sourceBtnClass(sensor)" 
              class="w-full text-[10px] font-bold py-1.5 px-0.5 rounded-md transition-all duration-200 text-center truncate block"
            >
              {{ sourceLabel(sensor) }}
            </button>
          </div>
          
          <div class="col-span-5 w-full flex justify-end min-w-0">
            <select
              v-if="getConfig(sensor)?.source === 'SIMULATED'"
              :value="getConfig(sensor)?.simulation_profile || 'normal'"
              @change="changeProfile(sensor, $event.target.value)"
              class="w-full text-[10px] bg-[#111c24] text-slate-300 border border-[#16222f] rounded-md py-1.5 pr-2 pl-1 focus:outline-none focus:border-cyan-500/50 font-medium transition-colors cursor-pointer text-right"
            >
              <option value="normal">{{ $t('normal') }}</option>
              <option value="abnormal">{{ $t('abnormal') }}</option>
              <option value="gradual_deterioration">{{ $t('gradual_deterioration') }}</option>
              <option value="emergency_spike">{{ $t('emergency_spike') }}</option>
              <option value="random">{{ $t('random') }}</option>
              <option value="custom">{{ $t('custom') }}</option>
            </select>
            
            <span v-else class="text-[9px] text-emerald-500/60 font-mono font-bold pl-2 tracking-wide select-none">
              {{ $t('live') }}
            </span>
          </div>

        </div>
      </template>
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

// تم إصلاح الدالة هنا بوضع التعبير المنتظم / /g لاستبدال كافة الفراغات بشرطات سفلية
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
    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20' 
    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20'
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