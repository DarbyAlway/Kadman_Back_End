<!-- src/App.vue -->
<template>
  <div id="app" class="h-screen flex flex-col overflow-hidden">
    <div class="flex-shrink-0">
      <Navbar />
    </div>
    <div class="flex-1 overflow-hidden">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import Navbar from './components/Navbar.vue';
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Ensure no body scrolling */
html, body {
  height: 100%;
  overflow: hidden;
}
</style>