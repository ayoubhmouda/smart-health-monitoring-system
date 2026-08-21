// frontend/src/stores/alerts.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import { usePatientStore } from './patient'

export const useAlertsStore = defineStore('alerts', () => {
  const allLatestReadings = ref({})       
  const allChartReadings = ref({})        
  const allMLInsights = ref({})           
  const activeInsights = ref({})          // { [patientId]: activeInsightObject }
  const patientAlertStates = ref({})      // { [patientId]: 'CRITICAL' | 'HIGH' | null }
  const alertTimestamps = ref({})         
  const dismissedAlertIds = ref(new Set()) // لتتبع الإنذارات التي أخفاها الطبيب من الشاشة فقط

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

  // 🟢 جلب البيانات بالـ REST API مع حصر الإنذارات وتمييز هوية القوانين بدقة
// 🟢 جلب البيانات بالـ REST API مع حصر الإنذارات وتطهير فوري للحالة النشطة لمنع تداخل الأشباح
  const fetchData = async (patientId) => {
    if (!patientId) return
    
    // 🛡️ صمام الأمان الفوري (0ms): تصفير بيانات العرض الحالي فوراً لمنع ظهور شبح بيانات المريض السابق
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

      // حماية من سباق البيانات (Race Condition): نتأكد أن المريض المختار لم يتغير أثناء فترة الطلب
      if (Number(patientId) === Number(patientStore.currentPatient?.id)) {
        latestReadings.value = currentPatientReadings
      }

      const insightsList = Array.isArray(insightRes.data) ? insightRes.data : (insightRes.data.results || [])
      
      const processedInsights = insightsList.map(item => {
        const action = cachedActions.find(a => Number(a.insight) === Number(item.id))
        const ruleObj = action ? cachedRules.find(r => r.name === (action.rule_name || action.rule?.name) || Number(r.id) === Number(action.rule)) : null
        const isGlobalRule = ruleObj ? (!ruleObj.monitored_element) : false

        return {
          ...item,
          monitored_element: item.monitored_element || patientId,
          rule_name: action ? (action.rule_name || action.rule?.name) : null,
          action_template: action ? (action.description || action.rule?.action_template) : null,
          is_global_rule: isGlobalRule
        }
      })

      const mlInsight = processedInsights.find(i => i.source?.toLowerCase() === 'ml_model' || i.source?.toLowerCase() === 'ml')
      allMLInsights.value[patientId] = mlInsight || null

      // حماية من سباق البيانات: تعيين التنبؤ فقط للمريض النشط الحالي
      if (Number(patientId) === Number(patientStore.currentPatient?.id)) {
        latestInsight.value = mlInsight || null
      }
      
      const latestReading = data[0]
      const serverTime = latestReading ? new Date(latestReading.recorded_at).getTime() : Date.now()

      const activeThreshold = processedInsights.find(i => {
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
        activeInsights.value[patientId] = activeThreshold
        patientAlertStates.value[patientId] = severity
        alertTimestamps.value[patientId] = Date.now()
      } else {
        const lastReceived = alertTimestamps.value[patientId] || 0
        if (Date.now() - lastReceived > 35000) {
          activeInsights.value[patientId] = null
          patientAlertStates.value[patientId] = null
        }
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

  // 🟢 عدد الإنذارات في السايدبار: CRITICAL و HIGH فقط
  const activeAlertsCount = computed(() => {
    return Object.values(patientAlertStates.value).filter(v => v === 'CRITICAL' || v === 'HIGH').length
  })

  // 🟢 اختيار التنبيه العائم الأكثر خطورة (مع استبعاد ما أغلقه الطبيب مؤقتاً بـ X)
  const latestThresholdInsight = computed(() => {
    const patientStore = usePatientStore()
    const currentId = patientStore.currentPatient?.id

    // إذا كان المريض الحالي في حالة حرجة/عالية ولم يغلق الطبيب بطاقته، يُعرض أولاً
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

  // 🟢 دالة إخفاء بطاقة التنبيه المنبثقة فقط دون مسح الإنذار من السايدبار
  const dismissAlert = (alertId) => {
    if (alertId) {
      dismissedAlertIds.value.add(alertId)
    }
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
    alertPruneTimer = setInterval(() => {
      const now = Date.now()
      for (const pId in alertTimestamps.value) {
        const lastAlertTime = alertTimestamps.value[pId]
        if (lastAlertTime && (now - lastAlertTime > 45000)) {
          activeInsights.value[pId] = null
          patientAlertStates.value[pId] = null
          alertTimestamps.value[pId] = null
        }
      }
    }, 5000)
  }

  // 🟢 استماع فوري للـ WebSockets وتصفية صارمة لـ CRITICAL و HIGH
  // 🟢 استماع فوري للـ WebSockets وتنسيق مستقل ومطور لتنبؤات الـ ML والإنذارات السريرية
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
                is_global_rule: payload.insight?.is_global_rule // استقبال نوع ومصدر القاعدة من البث الفوري للسوكيت
              }
              
              const severity = String(insightData.severity).toUpperCase()
              const isML = insightData.source?.toLowerCase() === 'ml_model' || insightData.source?.toLowerCase() === 'ml'

              // 🟢 1. إذا كان التنبؤ مصدره الـ ML، نحدث الـ State الخاص به دوماً بشكل مستقل لملء كارت التنبؤات
              if (isML) {
                allMLInsights.value[p_id] = insightData
                if (Number(p_id) === Number(activeCurrentId)) {
                  latestInsight.value = insightData
                }
              }

              // 🟢 2. إذا كانت الخطورة حرجة أو عالية (وليس ML)، يُعامل كخطر لشبكة الأمان والبروتوكولات في السايدبار وبانر الطوارئ
              if (['CRITICAL', 'HIGH'].includes(severity) && !isML) {
                activeInsights.value[p_id] = insightData
                patientAlertStates.value[p_id] = severity
                alertTimestamps.value[p_id] = Date.now()
              }
            } else if (payload?.type === 'alert') {
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

  return {
    allLatestReadings,
    allChartReadings,
    allMLInsights,
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
    fetchData,
    fetchChartData,
    setupAllWebSockets,
    updatePatientAlertState,
    startCountdown,
    dismissAlert
  }
})