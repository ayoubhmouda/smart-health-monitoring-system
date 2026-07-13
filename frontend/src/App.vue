<template>
  <div v-if="isAuthPage" class="min-h-screen bg-gray-100">
    <router-view />
  </div>
  <div v-else class="flex min-h-screen bg-[#0b1a24]"> 
    <Sidebar />
    <div class="flex-1 overflow-y-auto">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')

import { useI18n } from 'vue-i18n'
import { watchEffect } from 'vue'
const { locale } = useI18n()
// هذا الكود يراقب المتغير locale، وبمجرد تغيره يقلب اتجاه الصفحة بالكامل
watchEffect(() => {
  document.documentElement.lang = locale.value
  document.documentElement.dir = locale.value === 'ar' ? 'rtl' : 'ltr'
})
</script>