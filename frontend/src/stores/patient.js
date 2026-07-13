import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePatientStore = defineStore('patient', () => {
  const currentPatient = ref(null)
  const patients = ref([])

  const selectPatient = (patient) => {
    currentPatient.value = patient
  }

  return { currentPatient, patients, selectPatient }
})