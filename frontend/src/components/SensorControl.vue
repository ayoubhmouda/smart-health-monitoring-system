<!-- frontend/src/components/SensorControl.vue -->
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
          class="group relative bg-[#0d9488]/30 hover:bg-[#0d9488]/50 text-teal-200 border border-teal-400/20 font-bold text-[10px] px-2.5 py-2 rounded-lg backdrop-blur-sm transition-all flex items-center gap-1.5 shadow-lg shadow-teal-900/10 cursor-pointer"
          title="ربط مستشعر مخصص جديد"
        >
          <Plus :size="13" stroke-width="2.5" />
          <span class="hidden sm:inline">ربط مستشعر</span>
        </button>

        <button 
          @click="fetchSensors" 
          class="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-200/70 hover:text-cyan-100 transition-all backdrop-blur-sm cursor-pointer"
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
      <!-- أولاً: التحكم المركزي الموحد للسيناريوهات -->
      <div class="bg-white/5 backdrop-blur-md p-4 rounded-2xl border border-white/10 grid grid-cols-1 lg:grid-cols-12 gap-3 items-center">
        
        <div class="lg:col-span-4 space-y-0.5">
          <span class="text-[11px] font-bold text-white block">سيناريو التدهور الموحد</span>
          <span class="text-[9px] text-cyan-300/50 block">يتحكم بكافة أجهزة المريض في آنٍ واحد</span>
        </div>

        <div class="lg:col-span-3">
          <button 
            @click="toggleMasterSource"
            :class="masterSourceBtnClass"
            class="w-full text-[11px] font-bold py-2 px-3 rounded-xl transition-all duration-300 text-center border shadow-sm flex items-center justify-center gap-1.5 backdrop-blur-sm cursor-pointer"
          >
            <ToggleLeft v-if="!isMasterSimulated" :size="14" />
            <ToggleRight v-else :size="14" />
            <span>تبديل المصدر للكل</span>
          </button>
        </div>

        <div class="lg:col-span-5">
          <!-- خيارات السيناريو الموحد للباكيند الـ 5 السريرية المعتمدة -->
          <select
            v-if="isMasterSimulated"
            v-model="bulkProfile"
            @change="updateBulkProfile"
            class="w-full text-[11px] bg-slate-800/80 text-slate-100 border border-slate-600/50 rounded-xl py-2 px-3 focus:outline-none focus:border-teal-400 font-bold transition-all shadow-sm cursor-pointer text-right backdrop-blur-sm"
          >
            <option value="">اختر سيناريو موحد...</option>
            <option value="normal">الوضع الطبيعي المستقر</option>
            <option value="gradual_deterioration">تدهور فسيولوجي تدريجي</option>
            <option value="gradual_recovery">تحسن فسيولوجي تدريجي</option>
            <option value="sudden_high">ارتفاع حاد مفاجئ</option>
            <option value="sudden_low">انخفاض حاد مفاجئ</option>
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

        <!-- شبكة الكروت البيضاء المنسجمة مع الهوية السريرية -->
        <div class="p-3 bg-teal-950/20 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 select-none">
          <div 
            v-for="sensor in pairedSensors" 
            :key="sensor.id" 
            class="p-3 rounded-2xl border flex flex-col justify-between gap-3 transition-all duration-300 relative overflow-visible"
            :class="[
              sensor.is_active 
                ? 'bg-white text-slate-700 border-slate-200/80 shadow-xs' 
                : 'bg-slate-100 text-slate-400 border-slate-200/50 opacity-60'
            ]"
          >
            <!-- رأس الكرت وبداخله السويتش النشط مع زر الثلاث نقاط التفاعلي -->
            <div class="flex items-start justify-between gap-2 relative">
              <div class="min-w-0">
                <h4 class="font-black text-slate-800 text-[11px] truncate flex items-center gap-1">
                  <icon  :size="12" :class="sensor.is_active ? 'text-[#0d9488]' : 'text-slate-400'" class="flex-shrink-0" />
                  {{ translateSensorName(sensor.sensor_type?.name) }}
                </h4>
                <span class="text-[9px] font-mono font-bold text-slate-400 block mt-0.5">ID: {{ sensor.device_identifier }}</span>
              </div>

              <!-- حلقة الإجراءات المجمعة بداخل زر ثلاث نقاط أنيق ومنزلق -->
              <div class="flex items-center gap-1">
                <button 
                  v-if="sensor.is_active"
                  @click.stop="toggleCardMenu(sensor.id)"
                  class="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer shrink-0"
                  title="الإجراءات"
                >
                  <MoreVertical :size="14" stroke-width="2.5" />
                </button>

                <!-- منبثقة الخيارات المنفردة للحساس -->
                <div 
                  v-if="activeMenuSensorId === sensor.id"
                  class="absolute left-0 top-7 w-36 bg-white border border-slate-200 rounded-xl shadow-lg z-30 py-1.5 text-[10px] font-bold text-slate-700 animate-[fadeIn_0.15s_ease-out]"
                >
                  <button 
                    @click="toggleSingleSensorSource(sensor)"
                    class="w-full text-right px-3.5 py-2 hover:bg-slate-50 transition-colors flex items-center gap-1.5 text-slate-700 cursor-pointer"
                  >
                    <RefreshCw :size="11" />
                    <span>{{ getConfig(sensor)?.source === 'SIMULATED' ? 'تحويل لبث حقيقي' : 'تحويل لمحاكاة' }}</span>
                  </button>
                  <button 
                    @click="openRenameModal(sensor)"
                    class="w-full text-right px-3.5 py-2 hover:bg-slate-50 transition-colors flex items-center gap-1.5 text-slate-700 cursor-pointer"
                  >
                    <Pencil :size="11" />
                    <span>تعديل المعرّف</span>
                  </button>
                  <button 
                    @click="deleteSensor(sensor.id)"
                    class="w-full text-right px-3.5 py-2 hover:bg-slate-50 hover:text-rose-600 transition-colors flex items-center gap-1.5 text-rose-500 border-t border-slate-100 cursor-pointer"
                  >
                    <Trash2 :size="11" />
                    <span>حذف الجهاز</span>
                  </button>
                </div>

                <!-- سويتش الإيقاف والتشغيل السريع -->
                <button 
                  @click="toggleSensorActive(sensor)" 
                  class="relative inline-flex h-4 w-7 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out outline-none shrink-0"
                  :class="sensor.is_active ? 'bg-emerald-500' : 'bg-slate-400'"
                  :title="sensor.is_active ? 'إيقاف' : 'تشغيل'"
                >
                  <span 
                    class="pointer-events-none inline-block h-3 w-3 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
                    :class="sensor.is_active ? 'translate-x-0' : '-translate-x-3'" 
                  ></span>
                </button>
              </div>
            </div>

            <!-- ملف المحاكاة أو البث الفوري المباشر للحساس المنفرد -->
            <div class="space-y-1 text-[10px]">
              <template v-if="sensor.is_active">
                <select
                  v-if="getConfig(sensor)?.source === 'SIMULATED'"
                  :value="getConfig(sensor)?.simulation_profile || 'normal'"
                  @change="changeProfile(sensor, $event.target.value)"
                  class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 outline-none text-right focus:border-teal-500/50 text-[10px] cursor-pointer"
                >
                  <!-- 🟢 1. تخصيص كروت وضعيات النشاط الحركي الحصرية والمستقلة -->
                  <template v-if="sensor.sensor_type?.name === 'Activity Level'">
                    <option value="activity_resting">سكون / نوم</option>
                    <option value="activity_sitting">جلوس</option>
                    <option value="activity_walking">مشي</option>
                    <option value="activity_running">جري / ركض</option>
                  </template>

                  <!-- 🟢 2. الحساسات الأخرى تعرض السيناريوهات السريرية الـ 5 المعتمدة -->
                  <template v-else>
                    <option value="normal">الوضع الطبيعي المستقر</option>
                    <option value="gradual_deterioration">تدهور فسيولوجي تدريجي</option>
                    <option value="gradual_recovery">تحسن فسيولوجي تدريجي</option>
                    <option value="sudden_high">ارتفاع حاد مفاجئ</option>
                    <option value="sudden_low">انخفاض حاد مفاجئ</option>
                  </template>
                </select>
                
                <span v-else class="text-[9px] text-emerald-700 font-extrabold py-1.5 flex items-center justify-center gap-1 select-none font-mono bg-emerald-50 border border-emerald-100 rounded-lg">
                  <Wifi :size="10" />
                  بث فيزيائي حقيقي (REAL)
                </span>
              </template>
              
              <div v-else class="text-[10px] text-slate-400 font-bold py-1 bg-slate-200/50 border border-slate-200/20 rounded-lg text-center select-none">
                الجهاز موقوف
              </div>
            </div>

            <!-- مؤشر صغير يوضح مصدر الحساس في زاوية الكارت -->
            <div class="absolute bottom-2 left-2.5 opacity-60">
              <span v-if="getConfig(sensor)?.source === 'SIMULATED'" class="text-amber-500" title="بث محاكي بالـ CPU"><icon  :size="10" /></span>
              <span v-else class="text-emerald-500" title="جهاز بث فسيولوجي فعلي"><Wifi :size="10" /></span>
            </div>
          </div>
        </div>
      </details>
    </div>

    <!-- 1. منبثقة تعديل اسم الحساس -->
    <Teleport to="body">
      <div v-if="showRenameModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-55 flex items-center justify-center p-4">
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

    <!-- 2. منبثقة ربط حساس مخصص جديد -->
    <Teleport to="body">
      <div v-if="showAddModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-55 flex items-center justify-center p-4">
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
  ChevronDown, Pencil, Trash2, X, Check, MoreVertical 
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

// معرف كرت القائمة المنسدلة المفتوح حالياً لزر الثلاث نقاط
const activeMenuSensorId = ref(null)

const toggleCardMenu = (sensorId) => {
  if (activeMenuSensorId.value === sensorId) {
    activeMenuSensorId.value = null
  } else {
    activeMenuSensorId.value = sensorId
  }
}

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

// تبديل مصدر البث بشكل فردي ومنعزل لكل حساس من خلال زر الثلاث نقاط
async function toggleSingleSensorSource(sensor) {
  const cfg = getConfig(sensor)
  if (!cfg?.id) return
  const nextSource = cfg.source === 'SIMULATED' ? 'PHYSICAL' : 'SIMULATED'
  loading.value = true
  try {
    await api.patch(`/api/data-source-configs/${cfg.id}/`, { source: nextSource })
    activeMenuSensorId.value = null // إغلاق القائمة
    await fetchSensors()
  } catch (e) {
    console.error('فشل تبديل مصدر الحساس المنفرد:', e)
  } finally {
    loading.value = false
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
  activeMenuSensorId.value = null // إغلاق القائمة
}

const openAddSensorModal = () => {
  addForm.value.device_identifier = `SN-${props.patientId}-custom-${Date.now().toString().slice(-4)}`
  showAddModal.value = true
}

// إغلاق قائمة الثلاث نقاط تلقائياً عند النقر في أي مكان خارج الكارت
onMounted(() => {
  window.addEventListener('click', () => {
    activeMenuSensorId.value = null
  })
})

watch(() => props.patientId, () => fetchSensors(), { immediate: true })

onMounted(() => fetchSensorTypes())
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
}
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