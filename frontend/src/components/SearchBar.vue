<!-- src/components/SearchBar.vue -->
<template>
  <div class="w-full">
    <div class="relative">
      <input
        v-model="searchQuery"
        @input="onSearchInput"
        @keyup.enter="onSearch"
        type="text"
        placeholder="Search vendors..."
        class="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-900 placeholder-gray-500"
      />
      <button
        @click="onSearch"
        class="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 text-sm font-medium text-blue-600 transition-all duration-300 hover:text-blue-800 hover:bg-gray-50 rounded-md"
      >
        Search
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const searchQuery = ref('');

const emit = defineEmits<{
  search: [query: string];
}>();

const onSearchInput = () => {
  // Optional: implement live search if needed
};

const onSearch = () => {
  // Always emit search, even with empty string
  emit('search', searchQuery.value);
};
</script>