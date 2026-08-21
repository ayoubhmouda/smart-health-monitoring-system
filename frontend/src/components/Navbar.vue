<!-- Navbar.vue -->
<template>
  <nav
    class="sticky top-0 z-50 h-16 bg-white border-b border-slate-200/80 shadow-sm flex items-center justify-between px-4 sm:px-6"
  >
    <!-- الشعار والعنوان -->
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center text-white font-extrabold text-sm shadow-md">
        <Activity :size="18" />
      </div>
      <h1 class="text-lg font-extrabold text-slate-800 tracking-tight hidden sm:block">
        Medi<span class="text-teal-600">Watch</span>
      </h1>
    </div>

    <!-- زر الهامبرغر يظهر فقط على الموبايل -->
    <button
      @click="store.isSidebarOpen = !store.isSidebarOpen"
      class="lg:hidden p-2 rounded-xl text-teal-800 hover:bg-teal-50 transition-colors"
      :title="store.isSidebarOpen ? 'إغلاق القائمة' : 'فتح القائمة'"
    >
      <Menu v-if="!store.isSidebarOpen" :size="22" stroke-width="2.5" />
      <X v-else :size="22" stroke-width="2.5" />
    </button>
  </nav>
</template>

<script setup>
import { Menu, X, Activity } from 'lucide-vue-next'
import { usePatientStore } from '../stores/patient'

const store = usePatientStore()
</script>