// frontend/src/stores/alerts.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import { usePatientStore } from './patient'
import { useDoctorStore } from './doctor'

export const useAlertsStore = defineStore('alerts', () => {
  const allLatestReadings = ref({})       
  const allChartReadings = ref({})        
  const allMLInsights = ref({})           
  const allRuleProgressions = ref({})     // تخزين تقدم القواعد لكل مريض { [patientId]: [...] }
  const activeInsights = ref({})          
  const patientAlertStates = ref({})      // مخصص لحالة السايدبار اللحظية الحية فقط
  const unresolvedPatientIds = ref([])    
  const unhandledAlertsCount = ref(0)     // 🟢 عداد إجمالي التنبيهات الحقيقي للنافبار
  const alertTimestamps = ref({})         
  const dismissedAlertIds = ref(new Set()) 

  const latestReadings = ref({})
  const latestInsight = ref(null)
  const isWsConnected = ref(false)
  const lastUpdatedTime = ref('')
  const justUpdated = ref(false)
  const showEmergencyBanner = ref(true)
  const countdown = ref(30)
  
  const wsSockets = ref({})
  let chartFetchSeq = 0
  let countdownTimer = null
  let alertPruneTimer = null

  let cachedRules = []
  let cachedActions = []
  let lastRulesFetchTime = 0

  const SENSOR_KEY_MAP = {
    'Heart Rate': 'heart_rate',
    'Oxygen Saturation': 'oxygen',
    'Activity Level': 'activity_level',
    'Body Temperature': 'temperature',
    'Blood Pressure Systolic': 'bp_sys',
    'Blood Pressure Diastolic': 'bp_dia',
    'Respiratory Rate': 'respiratory_rate',
    'Room Temperature': 'room_temperature',
  }

  const getReadingKey = (r) => {
    if (r?.id != null) return `id:${r.id}`
    const sensorName = r?.sensor_name || r?.sensor?.sensor_type?.name || 'unknown'
    return `k:${sensorName}:${r?.recorded_at}`
  }

  const mergeReadingsForPatient = (patientId, incoming) => {
    if (!Array.isArray(incoming) || incoming.length === 0) return
    const currentList = allChartReadings.value[patientId] || []
    const byKey = new Map(currentList.map(r => [getReadingKey(r), r]))
    
    incoming.forEach(r => {
      if (!r) return
      byKey.set(getReadingKey(r), r)
    })
    
    const merged = Array.from(byKey.values()).sort(
      (a, b) => new Date(a.recorded_at) - new Date(b.recorded_at)
    )
    
    allChartReadings.value = {
      ...allChartReadings.value,
      [patientId]: merged.length > 100 ? merged.slice(-100) : merged
    }
  }

  const applyToLatestReadings = (p_id, item) => {
    const key = SENSOR_KEY_MAP[item?.sensor_name]
    if (!key || !item) return
    
    if (!allLatestReadings.value[p_id]) {
      allLatestReadings.value[p_id] = {}
    }
    
    const existing = allLatestReadings.value[p_id][key]
    const incomingTime = item.recorded_at ? new Date(item.recorded_at).getTime() : null
    const existingTime = existing?.recorded_at ? new Date(existing.recorded_at).getTime() : -Infinity
    
    if (incomingTime == null || incomingTime >= existingTime) {
      allLatestReadings.value[p_id] = {
        ...allLatestReadings.value[p_id],
        [key]: { ...existing, ...item }
      }
    }
  }

  // 🟢 جلب العدد الإجمالي الحقيقي للتنبيهات غير المحلولة من جدول الإشعارات
const fetchUnhandledAlertsCount = async () => {
    try {
      const res = await api.get('/api/notifications/unread-count/')
      if (res.data?.count !== undefined) {
        unhandledAlertsCount.value = res.data.count
      }
    } catch (e) {
      console.error('Failed to fetch unhandled alerts count:', e)
    }
  }

  // 🟢 إنقاص العداد بمقدار 1 فقط عند ضغط الطبيب
  const decrementAlertsCount = () => {
    unhandledAlertsCount.value = Math.max(0, unhandledAlertsCount.value - 1)
  }

  const fetchData = async (patientId) => {
    if (!patientId) return
    
    const patientStore = usePatientStore()
    if (Number(patientId) === Number(patientStore.currentPatient?.id)) {
      latestReadings.value = {}
      latestInsight.value = null
    }

    try {
      const now = Date.now()
      if (now - lastRulesFetchTime > 30000 || cachedRules.length === 0) {
        const [actRes, rulesRes] = await Promise.all([
          api.get('/api/corrective-actions/'),
          api.get('/api/rules/')
        ])
        cachedActions = Array.isArray(actRes.data) ? actRes.data : (actRes.data.results || [])
        cachedRules = Array.isArray(rulesRes.data) ? rulesRes.data : (rulesRes.data.results || [])
        lastRulesFetchTime = now
      }

      const [readingsRes, insightRes] = await Promise.all([
        api.get('/api/sensor-readings/', {
          params: { sensor__monitored_element: patientId, monitored_element: patientId, ordering: '-recorded_at', limit: 30 }
        }),
        api.get('/api/insights/', {
          params: { monitored_element: patientId, ordering: '-detected_at', limit: 10 }
        })
      ])
      
      const data = Array.isArray(readingsRes.data) ? readingsRes.data : (readingsRes.data.results || [])
      
      const currentPatientReadings = {
        heart_rate: data.find(r => r.sensor_name === 'Heart Rate'),
        oxygen: data.find(r => r.sensor_name === 'Oxygen Saturation'),
        activity_level: data.find(r => r.sensor_name === 'Activity Level'),
        temperature: data.find(r => r.sensor_name === 'Body Temperature'),
        bp_sys: data.find(r => r.sensor_name === 'Blood Pressure Systolic'),
        bp_dia: data.find(r => r.sensor_name === 'Blood Pressure Diastolic'),
        respiratory_rate: data.find(r => r.sensor_name === 'Respiratory Rate'),
        room_temperature: data.find(r => r.sensor_name === 'Room Temperature'),
      }

      allLatestReadings.value[patientId] = currentPatientReadings

      if (Number(patientId) === Number(patientStore.currentPatient?.id)) {
        latestReadings.value = currentPatientReadings
      }

      const insightsList = Array.isArray(insightRes.data) ? insightRes.data : (insightRes.data.results || [])
      
      const processedInsights = insightsList.map(item => {
        const action = cachedActions
          .filter(a => Number(a.insight) === Number(item.id))
          .sort((a, b) => b.id - a.id)
          .find(a => {
            const ruleObj = cachedRules.find(r => r.name === (a.rule_name || a.rule?.name) || Number(r.id) === Number(a.rule))
            return ruleObj ? ruleObj.is_active : false
          })
        
        const ruleObj = action ? cachedRules.find(r => r.name === (action.rule_name || action.rule?.name) || Number(r.id) === Number(action.rule)) : null
        const isGlobalRule = ruleObj ? (!ruleObj.monitored_element) : false
        const ruleCondition = ruleObj ? (ruleObj.condition || {}) : {}

        return {
          ...item,
          monitored_element: item.monitored_element || patientId,
          rule_name: action ? (action.rule_name || action.rule?.name) : null,
          action_template: action ? (action.description || action.rule?.action_template) : null,
          is_global_rule: isGlobalRule,
          recipient: ruleCondition.recipient || 'doctor_and_caregiver' 
        }
      })

      const mlInsight = processedInsights.find(i => i.source?.toLowerCase() === 'ml_model' || i.source?.toLowerCase() === 'ml')
      allMLInsights.value[patientId] = mlInsight || null

      if (Number(patientId) === Number(patientStore.currentPatient?.id)) {
        latestInsight.value = mlInsight || null
      }
      
      const latestReading = data[0]
      const serverTime = latestReading ? new Date(latestReading.recorded_at).getTime() : Date.now()

      const activeThreshold = processedInsights.find(i => {
        if (i.status === 'resolved' || i.status === 'acknowledged') return false

        const sev = String(i.severity).toUpperCase()
        const isSevere = ['CRITICAL', 'HIGH'].includes(sev)
        if (!isSevere) return false
        
        const src = i.source?.toLowerCase()
        if (src === 'rules') {
          const ruleExists = cachedRules.some(r => r.name === i.rule_name || Number(r.id) === Number(i.rule_id))
          if (!ruleExists && cachedRules.length > 0) return false
        }

        const detectedTime = new Date(i.detected_at).getTime()
        const diff = serverTime - detectedTime
        return diff >= 0 && diff < (2 * 60 * 1000)
      })

      if (activeThreshold) {
        const severity = String(activeThreshold.severity).toUpperCase()
        
        const doctorStore = useDoctorStore()
        const userRole = doctorStore.role?.toLowerCase() || localStorage.getItem('user_role')?.toLowerCase() || ''
        const recipient = activeThreshold.recipient || 'doctor_and_caregiver'
        
        const isAllowed = 
          recipient === 'doctor_and_caregiver' ||
          (recipient === 'treating_doctor_only' && (userRole === 'doctor' || userRole === 'admin')) ||
          (recipient === 'caregiver_only' && (userRole === 'caregiver' || userRole === 'nurse'))

        if (isAllowed) {
          activeInsights.value[patientId] = activeThreshold
          patientAlertStates.value[patientId] = severity
          alertTimestamps.value[patientId] = Date.now()
          
          if (!unresolvedPatientIds.value.includes(Number(patientId))) {
            unresolvedPatientIds.value.push(Number(patientId))
          }
        }
      } else {
        // لا تصفير زمني تلقائي ليبقى العداد ثابتاً
      }

      lastUpdatedTime.value = new Date().toLocaleTimeString('ar-LY', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } catch (e) {
      console.error('Error fetching data in store:', e)
    }
  }

  const fetchChartData = async (patientId) => {
    if (!patientId) return
    const now = new Date()
    const startDate = new Date(now.getTime() - 60 * 60 * 1000).toISOString()
    const requestId = ++chartFetchSeq
    try {
      const params = { sensor__monitored_element: patientId, ordering: '-recorded_at', start_date: startDate }
      const res = await api.get('/api/sensor-readings/', { params })
      const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
      if (requestId !== chartFetchSeq) return
      mergeReadingsForPatient(patientId, data)
    } catch (e) {
      console.error('Chart fetch error:', e)
    }
  }

  const updatePatientAlertState = (patientId) => {
    if (!patientId) return
    fetchData(patientId)
  }

  // 🟢 العداد المعروض في النافبار: يقرأ مباشرة من إجمالي التنبيهات المعلقة الحقيقية
  const activeAlertsCount = computed(() => {
    return unhandledAlertsCount.value
  })

  const latestThresholdInsight = computed(() => {
    const patientStore = usePatientStore()
    const currentId = patientStore.currentPatient?.id

    if (currentId && activeInsights.value[currentId] && patientAlertStates.value[currentId]) {
      const currentAlert = activeInsights.value[currentId]
      if (!dismissedAlertIds.value.has(currentAlert.id)) {
        return currentAlert
      }
    }

    let bestInsight = null
    let bestWeight = 0

    for (const pId in activeInsights.value) {
      const insight = activeInsights.value[pId]
      if (!insight || dismissedAlertIds.value.has(insight.id)) continue
      if (!patientAlertStates.value[pId]) continue

      const severity = String(insight.severity).toUpperCase()
      const weight = severity === 'CRITICAL' ? 2 : (severity === 'HIGH' ? 1 : 0)

      if (weight > bestWeight) {
        bestWeight = weight
        bestInsight = insight
      }
    }
    return bestInsight
  })

  const dismissAlert = (alertId) => {
    if (alertId) {
      dismissedAlertIds.value.add(alertId)
    }
  }

  // 🟢 تصفير حالة السايدبار وإنقاص عداد النافبار بنقرة الطبيب حصراً
  const clearPatientAlert = (patientId) => {
    if (patientId) {
      activeInsights.value[patientId] = null
      patientAlertStates.value[patientId] = null
      alertTimestamps.value[patientId] = null
      unresolvedPatientIds.value = unresolvedPatientIds.value.filter(id => Number(id) !== Number(patientId))
    }
    decrementAlertsCount()
  }

  const startCountdown = (patientId) => {
    countdown.value = 30
    clearInterval(countdownTimer)
    countdownTimer = setInterval(() => {
      if (countdown.value > 0) {
        countdown.value--
      } else {
        fetchData(patientId)
        fetchChartData(patientId)
        countdown.value = 30
      }
    }, 1000)
  }

  const startAlertPruneService = () => {
    clearInterval(alertPruneTimer)
  }

  const setupAllWebSockets = (patientList) => {
    Object.values(wsSockets.value).forEach(socket => {
      if (socket) {
        socket.onclose = null
        socket.onerror = null
        socket.close()
      }
    })
    wsSockets.value = {}
    clearInterval(countdownTimer)
    startAlertPruneService()

    // 🟢 جلب إجمالي التنبيهات المعلقة الحقيقية من قاعدة البيانات فور بدء الاتصال
    fetchUnhandledAlertsCount()

    if (!Array.isArray(patientList) || patientList.length === 0) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname || 'localhost'
    const patientStore = usePatientStore()

    patientList.forEach(patient => {
      const p_id = patient.id
      const wsUrl = `${protocol}//${host}:8000/ws/notifications/${p_id}/`
      
      try {
        const currentSocket = new WebSocket(wsUrl)
        wsSockets.value[p_id] = currentSocket

        currentSocket.onopen = () => {
          isWsConnected.value = true
        }

        currentSocket.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data)
            const activeCurrentId = patientStore.currentPatient?.id

            if (payload?.type === 'sensor_update') {
              const newItems = Array.isArray(payload.readings) ? payload.readings : []
              
              if (!allLatestReadings.value[p_id]) {
                allLatestReadings.value[p_id] = {}
              }
              newItems.forEach(item => {
                applyToLatestReadings(p_id, item)
              })

              mergeReadingsForPatient(p_id, newItems)

              if (Number(p_id) === Number(activeCurrentId)) {
                latestReadings.value = { ...allLatestReadings.value[p_id] }
                justUpdated.value = true
                setTimeout(() => { justUpdated.value = false }, 1500)
                countdown.value = 30
              }

            } else if (payload?.type === 'insight_update') {
              const insightData = {
                ...payload.insight,
                monitored_element: payload.insight?.monitored_element || p_id,
                is_global_rule: payload.insight?.is_global_rule,
                recipient: payload.insight?.recipient || 'doctor_and_caregiver'
              }

              // 1. التعافي اللحظي للسايدبار: مسح اللون وإغلاق النافذة فوراً عند زوال الخطر
              if (insightData.status === 'resolved') {
                activeInsights.value[p_id] = null
                patientAlertStates.value[p_id] = null
                alertTimestamps.value[p_id] = null
                if (Number(p_id) === Number(activeCurrentId)) {
                  showEmergencyBanner.value = false
                }
                return
              }
              
              const severity = String(insightData.severity).toUpperCase()
              const isML = insightData.source?.toLowerCase() === 'ml_model' || insightData.source?.toLowerCase() === 'ml'

              if (isML) {
                allMLInsights.value[p_id] = insightData
                if (Number(p_id) === Number(activeCurrentId)) {
                  latestInsight.value = insightData
                }
              }

              const doctorStore = useDoctorStore()
              const userRole = doctorStore.role?.toLowerCase() || localStorage.getItem('user_role')?.toLowerCase() || ''
              const recipient = insightData.recipient || 'doctor_and_caregiver'
              
              const isAllowed = 
                recipient === 'doctor_and_caregiver' ||
                (recipient === 'treating_doctor_only' && (userRole === 'doctor' || userRole === 'admin')) ||
                (recipient === 'caregiver_only' && (userRole === 'caregiver' || userRole === 'nurse'))

              if (['CRITICAL', 'HIGH'].includes(severity) && !isML && isAllowed) {
                activeInsights.value[p_id] = insightData
                patientAlertStates.value[p_id] = severity
                alertTimestamps.value[p_id] = Date.now()

                if (!unresolvedPatientIds.value.includes(Number(p_id))) {
                  unresolvedPatientIds.value.push(Number(p_id))
                }
                // 🟢 تم حذف الزيادة العشوائية من هنا لمنع تضخم العداد مع كل دورة
              }
            } else if (payload?.type === 'rule_progression_update') {
              allRuleProgressions.value[p_id] = Array.isArray(payload.progressions) ? payload.progressions : []
            } else if (payload?.type === 'alert') {
              // 🟢 عند ولادة تنبيه جديد حقيقي، نستعلم عن العدد المحدث مباشرة من السيرفر
              fetchUnhandledAlertsCount()
              fetchData(p_id)
            }
          } catch (err) {
            console.error('Socket message parse error:', err)
          }
        }

        currentSocket.onerror = () => {}
        currentSocket.onclose = () => {}
      } catch (err) {
        console.error('Socket connect error:', err)
      }
    })

    const initialPatientId = patientStore.currentPatient?.id
    if (initialPatientId) {
      startCountdown(initialPatientId)
    }
  }

  const readings = computed(() => {
    const pId = usePatientStore().currentPatient?.id
    return pId ? (allChartReadings.value[pId] || []) : []
  })

  const currentPatientProgressions = computed(() => {
    const pId = usePatientStore().currentPatient?.id
    return pId ? (allRuleProgressions.value[pId] || []) : []
  })

  return {
    allLatestReadings,
    allChartReadings,
    allMLInsights,
    allRuleProgressions,
    currentPatientProgressions,
    activeInsights,
    latestReadings,
    latestInsight,
    latestThresholdInsight,
    readings,
    isWsConnected,
    lastUpdatedTime,
    justUpdated,
    showEmergencyBanner,
    countdown,
    patientAlertStates,
    activeAlertsCount,
    unresolvedPatientIds,
    unhandledAlertsCount,
    fetchUnhandledAlertsCount,
    decrementAlertsCount,
    fetchData,
    fetchChartData,
    setupAllWebSockets,
    updatePatientAlertState,
    startCountdown,
    dismissAlert,
    clearPatientAlert
  }
})