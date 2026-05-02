<!-- src/components/Navbar.vue -->
<template>
  <nav class="bg-white shadow-sm border-b border-gray-100 relative z-10">
    <div class="max-w-full mx-auto px-7">
      <div class="flex justify-between items-center h-17">
        <!-- Left side - Logo/Title -->
        <div class="flex items-center">
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Kadman</h1>
        </div>
        
        <!-- Right side - Menu items -->
        <div class="flex space-x-2">
          <router-link
            to="/layout"
            class="relative px-5 py-2 text-sm font-medium text-gray-700 transition-all duration-300 hover:text-gray-900 hover:bg-gray-50 rounded-md"
            :class="isActive('/layout').value ? 'text-blue-600 bg-blue-50' : ''"
          >
            Layout
          </router-link>
          <router-link
            to="/attendance" 
            class="relative px-5 py-2 text-sm font-medium text-gray-700 transition-all duration-300 hover:text-gray-900 hover:bg-gray-50 rounded-md"
            :class="isActive('/attendance').value ? 'text-blue-600 bg-blue-50' : ''"
          >
            Attendance
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();

const isActive = (path: string) => {
  return computed(() => route.path === path);
};
</script>