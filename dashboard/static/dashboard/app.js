const { createApp } = Vue;

createApp({
  delimiters: ['[[', ']]'],
  data() {
    return {
      patients: [],
      selectedPatient: null,
      patientSensors: [],
      latestHR: '-',
      latestO2: '-',
      latestTemp: '-',
      latestInsight: null,
      lastUpdate: '',
      API: '/api'
    };
  },
  computed: {
    severityClass() {
      if (!this.latestInsight) return '';
      const s = this.latestInsight.severity;
      if (s === 'high' || s === 'critical') return 'bg-red-100 text-red-800';
      if (s === 'medium') return 'bg-yellow-100 text-yellow-800';
      return 'bg-green-100 text-green-800';
    }
  },
  async mounted() {
    await this.loadPatients();
    setInterval(() => this.refreshAll(), 30000);
  },
  methods: {
    async loadPatients() {
      try {
        const res = await axios.get(`${this.API}/monitored-elements/`);
        this.patients = res.data;
      } catch (e) { console.error(e); }
    },
    async selectPatient(patient) {
      this.selectedPatient = patient;
      await Promise.all([this.loadReadings(), this.loadInsight(), this.loadSensors()]);
    },


async loadReadings() {
  if (!this.selectedPatient) return;
  try {
    const res = await axios.get(`${this.API}/sensor-readings/`, {
      params: {
        sensor__monitored_element: this.selectedPatient.id,
        ordering: '-recorded_at',
        limit: 20
      }
    });
    const readings = res.data || [];
    this.latestHR = this.findReading(readings, 'Heart Rate');
    this.latestO2 = this.findReading(readings, 'Oxygen Saturation');
    this.latestTemp = this.findReading(readings, 'Body Temperature');
  } catch (e) { console.error(e); }
},

async loadSensors() {
  if (!this.selectedPatient) return;
  try {
    const res = await axios.get(`${this.API}/sensors/`, {
      params: { monitored_element: this.selectedPatient.id }
    });
    this.patientSensors = res.data || [];
  } catch (e) { console.error(e); }
},

    findReading(readings, sensorName) {
      const r = readings.find(r => r.sensor?.sensor_type?.name === sensorName);
      return r ? r.value : '-';
    },
    async loadInsight() {
      try {
        const res = await axios.get(`${this.API}/insights/`, {
          params: { monitored_element: this.selectedPatient.id, ordering: '-detected_at', limit: 1 }
        });
        this.latestInsight = res.data?.[0] || null;
      } catch (e) { console.error(e); }
    },
    
    async toggleSource(sensor) {
      const config = sensor.data_source_config;
      if (!config?.id) { alert('لا يوجد إعداد مصدر.'); return; }
      const newSource = config.source === 'SIMULATED' ? 'PHYSICAL' : 'SIMULATED';
      try {
        await axios.patch(`${this.API}/data-source-configs/${config.id}/`, { source: newSource });
        config.source = newSource;
      } catch (e) { alert('فشل التبديل.'); }
    },
    async refreshAll() {
      if (this.selectedPatient) {
        await this.loadReadings();
        await this.loadInsight();
      }
      this.lastUpdate = new Date().toLocaleTimeString('ar-LY');
    }
  }
}).mount('#app');