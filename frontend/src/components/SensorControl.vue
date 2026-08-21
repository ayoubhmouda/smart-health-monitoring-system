<!-- SensorControl.vue -->
<template>
  <div class="relative rounded-3xl border border-white/10 shadow-xl flex flex-col gap-5 select-none bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] p-5 sm:p-6 text-cyan-100/80" dir="rtl">
    
    <!-- هيدر لوحة التحكم المركزية -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-2 border-b border-white/10 gap-3">
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-xl bg-white/10 flex items-center justify-center text-teal-300 backdrop-blur-sm">
          <Sliders :size="16" stroke-width="2" />
        </div>
        <h3 class="text-xs font-black text-white tracking-wider uppercase">
          لوحة محاكاة السيناريوهات السريرية
        </h3>
      </div>
      
      <!-- أزرار الإجراءات العامة الموحدة -->
      <div class="flex flex-wrap items-center gap-1.5 self-start sm:self-auto">
        <button 
          @click="openAddSensorModal" 
          class="group relative bg-teal-500/20 hover:bg-teal-500/30 text-teal-200 border border-teal-400/20 font-bold text-[10px] px-2.5 py-2 rounded-lg backdrop-blur-sm transition-all flex items-center gap-1.5 shadow-lg shadow-teal-900/10"
          title="ربط مستشعر مخصص جديد"
        >
          <Plus :size="13" stroke-width="2.5" />
          <span class="hidden sm:inline">ربط مستشعر</span>
        </button>

        <button 
          @click="fetchSensors" 
          class="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-200/70 hover:text-cyan-100 transition-all backdrop-blur-sm"
          title="تحديث قائمة الحساسات"
        >
          <RefreshCw :size="14" stroke-width="2" :class="loading ? 'animate-spin' : ''" />
        </button>

        <div v-if="loading" class="text-[10px] font-mono font-bold text-teal-300 bg-teal-500/10 px-2 py-1 rounded-full backdrop-blur-sm animate-pulse flex items-center gap-1">
          <Loader :size="10" class="animate-spin" />
          مزامنة...
        </div>
      </div>
    </div>

    <!-- واجهة التنبيه في غياب الأجهزة -->
    <div v-if="sensors.length === 0 && !loading" class="text-cyan-300/50 text-[10px] text-center py-8 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-sm">
      <MonitorOff :size="28" class="mx-auto mb-2 opacity-50" />
      لا توجد حساسات مرتبطة بهذا المريض حالياً.
    </div>

    <div v-else class="space-y-4">
      <!-- أولاً: التحكم المركزي الموحد -->
      <div class="bg-white/5 backdrop-blur-md p-4 rounded-2xl border border-white/10 grid grid-cols-1 lg:grid-cols-12 gap-3 items-center">
        
        <div class="lg:col-span-4 space-y-0.5">
          <span class="text-[11px] font-bold text-white block">سيناريو التدهور الموحد</span>
          <span class="text-[9px] text-cyan-300/50 block">يتحكم بكافة أجهزة المريض في آنٍ واحد</span>
        </div>

        <div class="lg:col-span-3">
          <button 
            @click="toggleMasterSource"
            :class="masterSourceBtnClass"
            class="w-full text-[11px] font-bold py-2 px-3 rounded-xl transition-all duration-300 text-center border shadow-sm flex items-center justify-center gap-1.5 backdrop-blur-sm"
          >
            <ToggleLeft v-if="!isMasterSimulated" :size="14" />
            <ToggleRight v-else :size="14" />
            <span>تبديل المصدر للكل</span>
          </button>
        </div>

        <div class="lg:col-span-5">
          <select
            v-if="isMasterSimulated"
            v-model="bulkProfile"
            @change="updateBulkProfile"
            class="w-full text-[11px] bg-slate-800/80 text-slate-100 border border-slate-600/50 rounded-xl py-2 px-3 focus:outline-none focus:border-teal-400 font-bold transition-all shadow-sm cursor-pointer text-right backdrop-blur-sm"
          >
            <option value="">اختر سيناريو موحد...</option>
            <option value="normal">الوضع الطبيعي المستقر</option>
            <option value="gradual_deterioration">تدهور فسيولوجي تدريجي</option>
            <option value="emergency_spike">نوبة طوارئ حادة</option>
            <option value="abnormal">مؤشرات شاذة منخفضة</option>
            <option value="recovery">مرحلة الاستشفاء</option>
            <option value="random">محاكاة عشوائية</option>
          </select>
          <div v-else class="w-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[11px] font-bold py-2 px-3 rounded-xl text-center flex items-center justify-center gap-1.5 backdrop-blur-sm">
            <Wifi :size="12" class="text-emerald-400" />
            <span>البث المباشر (PHYSICAL)</span>
          </div>
        </div>
      </div>

      <!-- ثانياً: التحكم اليدوي والمنفرد المطوي -->
      <details class="group border border-white/10 rounded-2xl overflow-hidden bg-white/5 backdrop-blur-sm" open>
        <summary class="flex justify-between items-center p-3 bg-white/5 hover:bg-white/10 cursor-pointer select-none text-[11px] font-bold text-cyan-200/80 transition-colors">
          <div class="flex items-center gap-1.5">
            <Cpu :size="14" stroke-width="2" />
            <span>خيارات التحكم المتقدم والمنفرد بالأجهزة</span>
          </div>
          <ChevronDown :size="14" class="text-cyan-300/50 group-open:rotate-180 transition-transform duration-200" />
        </summary>

        <!-- شبكة 4x2 مكثفة ومتقاربة -->
        <div class="p-3 bg-black/10 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
          <div 
            v-for="sensor in pairedSensors" 
            :key="sensor.id" 
            class="p-3 rounded-2xl border flex flex-col justify-between gap-2 transition-all duration-300 relative overflow-hidden group/card"
            :class="sensor.is_active ? 'border-white/20 bg-white/5 hover:bg-white/10 hover:border-teal-400/30' : 'border-white/5 bg-black/20 opacity-50'"
          >
            <!-- رأس الكرت والتبديل -->
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <h4 class="font-extrabold text-white text-[11px] truncate flex items-center gap-1">
                  <Activity :size="12" class="text-teal-300/70 flex-shrink-0" />
                  {{ translateSensorName(sensor.sensor_type?.name) }}
                </h4>
                <span class="text-[9px] font-mono font-bold text-cyan-300/40 block">ID: {{ sensor.device_identifier }}</span>
              </div>

              <button 
                @click="toggleSensorActive(sensor)" 
                class="relative inline-flex h-4 w-7 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out outline-none"
                :class="sensor.is_active ? 'bg-emerald-500' : 'bg-slate-600'"
                :title="sensor.is_active ? 'إيقاف' : 'تشغيل'"
              >
                <span 
                  class="pointer-events-none inline-block h-3 w-3 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
                  :class="sensor.is_active ? 'translate-x-0' : '-translate-x-3'" 
                ></span>
              </button>
            </div>

            <!-- ملف المحاكاة -->
            <div class="space-y-1 text-[10px]">
              <label class="block font-bold text-cyan-200/50">الملف:</label>
              
              <template v-if="sensor.is_active">
                <select
                  v-if="getConfig(sensor)?.source === 'SIMULATED'"
                  :value="getConfig(sensor)?.simulation_profile || 'normal'"
                  @change="changeProfile(sensor, $event.target.value)"
                  class="w-full bg-slate-800/80 border border-slate-600/50 rounded-lg px-2 py-1 font-bold text-slate-200 outline-none text-right focus:border-teal-400/50 text-[10px]"
                >
                  <option value="normal">طبيعي</option>
                  <option value="abnormal">شاذ</option>
                  <option value="gradual_deterioration">تدهور</option>
                  <option value="emergency_spike">حاد</option>
                  <option value="random">عشوائي</option>
                  <option value="custom">مخصص</option>
                </select>
                
                <span v-else class="text-[10px] text-emerald-300 font-bold py-1 flex items-center gap-1 select-none font-mono bg-emerald-500/10 px-2 rounded-lg">
                  <Wifi :size="10" />
                  بث فوري
                </span>
              </template>
              
              <div v-else class="text-[10px] text-slate-400 font-semibold py-1 bg-slate-800/30 rounded-lg text-center">
                موقوف
              </div>
            </div>

            <!-- أزرار الإجراءات -->
            <div class="flex items-center justify-end gap-1 pt-2 border-t border-white/5">
              <button 
                @click="openRenameModal(sensor)" 
                class="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-200/70 hover:text-cyan-100 transition-all"
                title="تعديل المعرف"
              >
                <Pencil :size="12" stroke-width="2" />
              </button>

              <button 
                @click="deleteSensor(sensor.id)" 
                class="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-400/20 text-rose-400 hover:text-rose-300 transition-all"
                title="حذف الحساس"
              >
                <Trash2 :size="12" stroke-width="2" />
              </button>
            </div>

            <!-- مؤشر المصدر -->
            <div class="absolute top-1.5 left-1.5 opacity-60">
              <span v-if="getConfig(sensor)?.source === 'SIMULATED'" class="text-amber-400/70" title="محاكاة"><Cpu :size="8" /></span>
              <span v-else class="text-emerald-400/70" title="جهاز فعلي"><Wifi :size="8" /></span>
            </div>
          </div>
        </div>
      </details>
    </div>

    <!-- 1. منبثقة تعديل اسم الحساس (Rename Modal) -->
    <Teleport to="body">
      <div v-if="showRenameModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl w-full max-w-md p-6 space-y-4 text-cyan-100">
          <div class="flex items-center justify-between border-b border-slate-700 pb-3">
            <h3 class="text-sm font-extrabold text-white">تعديل معرف الحساس</h3>
            <button @click="showRenameModal = false" class="text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/5">
              <X :size="18" />
            </button>
          </div>

          <form @submit.prevent="submitRenameForm" class="space-y-4 text-xs">
            <div>
              <label class="block font-bold text-cyan-200/80 mb-1">المعرّف (Device Identifier)</label>
              <input 
                v-model="renameForm.device_identifier" 
                type="text" 
                required 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-mono font-bold text-slate-200" 
              />
            </div>

            <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-700">
              <button type="button" @click="showRenameModal = false" class="px-4 py-2 rounded-xl text-slate-400 font-bold hover:bg-slate-800 transition-colors">إلغاء</button>
              <button type="submit" class="bg-teal-600 hover:bg-teal-500 text-white font-bold px-5 py-2 rounded-xl transition-colors flex items-center gap-2">
                <Check :size="15" />
                حفظ
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- 2. منبثقة ربط حساس مخصص جديد (Add Sensor Modal) -->
    <Teleport to="body">
      <div v-if="showAddModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl w-full max-w-md p-6 space-y-4 text-cyan-100">
          <div class="flex items-center justify-between border-b border-slate-700 pb-3">
            <h3 class="text-sm font-extrabold text-white">ربط مستشعر جديد</h3>
            <button @click="showAddModal = false" class="text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/5">
              <X :size="18" />
            </button>
          </div>

          <form @submit.prevent="submitAddSensorForm" class="space-y-4 text-xs">
            <div>
              <label class="block font-bold text-cyan-200/80 mb-1">نوع المستشعر</label>
              <select v-model="addForm.sensor_type_id" class="w-full bg-slate-800 border border-slate-600 rounded-xl px-3 py-2.5 outline-none font-bold text-slate-200">
                <option v-for="type in sensorTypes" :key="type.id" :value="type.id">
                  {{ type.name }} ({{ type.unit }})
                </option>
              </select>
            </div>

            <div>
              <label class="block font-bold text-cyan-200/80 mb-1">المعرّف</label>
              <input 
                v-model="addForm.device_identifier" 
                type="text" 
                required 
                class="w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-2.5 focus:border-teal-400 outline-none font-mono font-bold text-slate-200" 
              />
            </div>

            <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-700">
              <button type="button" @click="showAddModal = false" class="px-4 py-2 rounded-xl text-slate-400 font-bold hover:bg-slate-800 transition-colors">إلغاء</button>
              <button type="submit" class="bg-teal-600 hover:bg-teal-500 text-white font-bold px-5 py-2 rounded-xl transition-colors flex items-center gap-2">
                <Plus :size="15" />
                ربط
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import { 
  Sliders, Plus, RefreshCw, Loader, MonitorOff, 
  ToggleLeft, ToggleRight, Wifi, Cpu, Activity, 
  ChevronDown, Pencil, Trash2, X, Check 
} from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  patientId: { type: Number, required: true }
})

const sensors = ref([])
const sensorTypes = ref([])
const loading = ref(true)
const bulkProfile = ref('')

const showRenameModal = ref(false)
const showAddModal = ref(false)

const renameForm = ref({ id: null, device_identifier: '' })
const addForm = ref({ sensor_type_id: null, device_identifier: '' })

function translateSensorName(name) {
  if (!name) return t('custom')
  const key = name.toLowerCase().replace(/ /g, '_') 
  return t(key)
}

async function fetchSensors() {
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

    const cachedBulk = localStorage.getItem(`bulk_profile_patient_${props.patientId}`)
    bulkProfile.value = cachedBulk || ''

  } catch (e) {
    console.error('فشل جلب الحساسات:', e)
  } finally {
    loading.value = false
  }
}

async function fetchSensorTypes() {
  try {
    const res = await api.get('/api/sensor-types/')
    sensorTypes.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    if (sensorTypes.value.length > 0) {
      addForm.value.sensor_type_id = sensorTypes.value[0].id
    }
  } catch (e) {
    console.error('فشل جلب أنواع الحساسات:', e)
  }
}

async function toggleSensorActive(sensor) {
  try {
    await api.patch(`/api/sensors/${sensor.id}/`, { is_active: !sensor.is_active })
    await fetchSensors()
  } catch (e) {
    console.error('فشل تغيير حالة الحساس:', e)
  }
}

async function submitRenameForm() {
  try {
    await api.patch(`/api/sensors/${renameForm.value.id}/`, {
      device_identifier: renameForm.value.device_identifier
    })
    showRenameModal.value = false
    await fetchSensors()
  } catch (e) {
    console.error('فشل حفظ المعرف:', e)
    alert('فشل تغيير المسمى، تأكد من عدم تكراره.')
  }
}

async function submitAddSensorForm() {
  try {
    const sensorRes = await api.post('/api/sensors/', {
      sensor_type: addForm.value.sensor_type_id,
      monitored_element: props.patientId,
      device_identifier: addForm.value.device_identifier,
      is_active: true
    })

    await api.post('/api/data-source-configs/', {
      sensor: sensorRes.data.id,
      source: 'SIMULATED',
      simulation_profile: 'normal'
    })

    showAddModal.value = false
    await fetchSensors()
  } catch (e) {
    console.error('فشل ربط الحساس:', e)
    alert('تعذر ربط الحساس، يرجى مراجعة المعرف.')
  }
}

async function deleteSensor(id) {
  if (!confirm('هل أنت متأكد من رغبتك في حذف هذا الجهاز كلياً؟')) return
  try {
    await api.delete(`/api/sensors/${id}/`)
    await fetchSensors()
  } catch (e) {
    console.error('فشل حذف الحساس:', e)
  }
}

async function changeProfile(s, p) {
  const cfg = getConfig(s)
  if (!cfg?.id) return
  try {
    await api.patch(`/api/data-source-configs/${cfg.id}/`, { simulation_profile: p })
    cfg.simulation_profile = p
  } catch (e) { console.error(e) }
}

async function toggleMasterSource() {
  if (!sensors.value.length) return
  loading.value = true
  const activeSensors = sensors.value.filter(s => s.is_active && getConfig(s))
  if (!activeSensors.length) {
    loading.value = false
    return
  }
  const firstConfig = getConfig(activeSensors[0])
  if (!firstConfig) {
    loading.value = false
    return
  }
  const nextSource = firstConfig.source === 'SIMULATED' ? 'PHYSICAL' : 'SIMULATED'
  
  try {
    const promises = activeSensors.map(s => 
      api.patch(`/api/data-source-configs/${getConfig(s).id}/`, { source: nextSource })
    )
    await Promise.all(promises)
    await fetchSensors()
  } catch (e) {
    console.error('فشل تبديل المصدر الموحد:', e)
  } finally {
    loading.value = false
  }
}

async function updateBulkProfile() {
  if (!bulkProfile.value) return
  loading.value = true
  try {
    const activeSensors = sensors.value.filter(s => s.is_active && getConfig(s) && getConfig(s).source === 'SIMULATED')
    const promises = activeSensors.map(s => 
      api.patch(`/api/data-source-configs/${getConfig(s).id}/`, { simulation_profile: bulkProfile.value })
    )
    await Promise.all(promises)
    localStorage.setItem(`bulk_profile_patient_${props.patientId}`, bulkProfile.value)
    await fetchSensors()
  } catch (e) {
    console.error('فشل تغيير السيناريو الموحد:', e)
  } finally {
    loading.value = false
  }
}

const pairedSensors = computed(() => {
  return [...sensors.value].sort((a, b) => (a.sensor_type?.id || 0) - (b.sensor_type?.id || 0))
})

const getConfig = (s) => s._config

const isMasterSimulated = computed(() => {
  if (!sensors.value.length) return false
  return sensors.value.some(s => s.is_active && getConfig(s)?.source === 'SIMULATED')
})

const masterSourceBtnClass = computed(() => {
  return isMasterSimulated.value
    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-400/20 hover:bg-emerald-500/20'
    : 'bg-amber-500/10 text-amber-300 border-amber-400/20 hover:bg-amber-500/20'
})

const openRenameModal = (sensor) => {
  renameForm.value = { id: sensor.id, device_identifier: sensor.device_identifier }
  showRenameModal.value = true
}

const openAddSensorModal = () => {
  addForm.value.device_identifier = `SN-${props.patientId}-custom-${Date.now().toString().slice(-4)}`
  showAddModal.value = true
}

watch(() => props.patientId, () => fetchSensors(), { immediate: true })

onMounted(() => fetchSensorTypes())
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.02);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.25);
}

select option {
  background: #0f172a;
  color: #e2e8f0;
}
</style>