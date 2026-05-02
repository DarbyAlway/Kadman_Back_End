<!-- src/components/SearchResults.vue -->
<template>
  <div class="w-full">
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="text-gray-500">Loading...</div>
    </div>
    
    <div v-else-if="error" class="flex items-center justify-center py-8">
      <div class="text-red-500">{{ error }}</div>
    </div>
    
    <div v-else-if="results.length === 0" class="flex items-center justify-center py-8">
      <div class="text-gray-500">No results found</div>
    </div>
    
    <div v-else class="space-y-3">
      <div
        v-for="vendor in results"
        :key="vendor.vendorID"
        class="vendor-card border border-gray-100 rounded-lg p-4 transition-all duration-300 hover:bg-gray-50 hover:border-gray-200 cursor-grab active:cursor-grabbing relative"
        draggable="true"
        @dragstart="handleDragStart($event, vendor)"
        @dragend="handleDragEnd"
      >
        <!-- Edit icon - appears on hover -->
        <button
          @click.stop="openEditModal(vendor)"
          class="edit-icon absolute -top-2 -right-2 w-6 h-6 bg-gray-500 hover:bg-gray-600 text-white rounded-full flex items-center justify-center opacity-0 transition-all duration-200"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18.5 2.50023C18.8978 2.1024 19.4374 1.87891 20 1.87891C20.5626 1.87891 21.1022 2.1024 21.5 2.50023C21.8978 2.89805 22.1213 3.43762 22.1213 4.00023C22.1213 4.56284 21.8978 5.1024 21.5 5.50023L12 15.0002L8 16.0002L9 12.0002L18.5 2.50023Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <h3 class="font-semibold text-gray-900">{{ vendor.shop_name }}</h3>
        <p class="text-sm text-gray-500 mt-1">ID: {{ vendor.vendorID }}</p>
        
        <div v-if="vendor.badges.length > 0" class="mt-3">
          <div class="flex flex-wrap gap-2">
            <span
              v-for="badge in vendor.badges"
              :key="badge"
              class="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full border border-blue-200"
            >
              {{ badge }}
            </span>
          </div>
        </div>
      </div>
      <!-- Add space at bottom for last item -->
      <div class="h-4"></div>
    </div>

    <!-- Edit Modal -->
    <div
      v-if="showEditModal"
      class="modal-overlay fixed inset-0 flex items-center justify-center z-50"
      style="background-color: rgba(0, 0, 0, 0.25);"
    >
      <div
        class="modal-content bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
      >
        <div class="mb-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Edit Vendor</h3>
          <div v-if="selectedVendor">
            <!-- Shop Name Input Field -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Shop Name:</label>
              <input
                v-model="editedShopName"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter shop name"
              />
            </div>
            
            <p class="text-sm text-gray-600 mb-3">
              <span class="font-medium">ID:</span> {{ selectedVendor.vendorID }}
            </p>
            
            <div class="mb-3">
              <p class="text-sm font-medium text-gray-700 mb-2">Badges:</p>
              <div class="flex flex-wrap gap-2 items-center">
                <span
                  v-for="(badge, index) in editedBadges"
                  :key="`${badge}-${index}`"
                  class="badge-item bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full border border-blue-200 relative group"
                >
                  {{ badge }}
                  <!-- Delete button - appears on hover -->
                  <button
                    @click="removeBadge(index)"
                    class="delete-badge absolute -top-1 -right-1 w-4 h-4 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    title="Remove badge"
                  >
                    ×
                  </button>
                </span>
                
                <!-- New Badge Input - appears when adding -->
                <input
                  v-if="isAddingBadge"
                  ref="badgeInput"
                  v-model="newBadgeText"
                  @keyup.enter="confirmAddBadge"
                  @keyup.escape="cancelAddBadge"
                  @blur="cancelAddBadge"
                  @input="adjustInputWidth"
                  type="text"
                  maxlength="20"
                  class="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full border border-blue-200 outline-none focus:ring-2 focus:ring-blue-400"
                  :style="{ width: inputWidth + 'px' }"
                />
                
                <!-- Add Badge Button - hidden when adding -->
                <button
                  v-if="!isAddingBadge"
                  @click="startAddBadge"
                  class="w-6 h-6 bg-blue-50 text-blue-700 text-xs rounded-full border border-blue-200 hover:bg-blue-100 transition-colors duration-200 font-bold flex items-center justify-center"
                  title="Add badge"
                >
                  +
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <button
            @click="closeEditModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="confirmEdit"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import type { Vendor, VendorStore } from '../types/api';

const props = defineProps<{
  results: Vendor[];
  loading: boolean;
  error: string | null;
  vendorStore: VendorStore;
}>();

const emit = defineEmits<{
  vendorUpdated: [vendor: Vendor];
}>();

const showEditModal = ref(false);
const selectedVendor = ref<Vendor | null>(null);
const editedShopName = ref('');
const editedBadges = ref<string[]>([]);
const isAddingBadge = ref(false);
const newBadgeText = ref('');
const badgeInput = ref<HTMLInputElement | null>(null);
const inputWidth = ref(24); // Start as circle (same as h-6)

const handleDragStart = (event: DragEvent, vendor: Vendor) => {
  if (event.dataTransfer) {
    // Only send vendor ID instead of full vendor data
    event.dataTransfer.setData('application/json', JSON.stringify({ vendorID: vendor.vendorID }));
    event.dataTransfer.effectAllowed = 'copy';
  }
};

const handleDragEnd = (event: DragEvent) => {
  // Reset cursor and any drag state if needed
};

const openEditModal = (vendor: Vendor) => {
  selectedVendor.value = vendor;
  editedShopName.value = vendor.shop_name;
  editedBadges.value = [...vendor.badges]; // Create a copy of badges for editing
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  selectedVendor.value = null;
  editedShopName.value = '';
  editedBadges.value = [];
  isAddingBadge.value = false;
  newBadgeText.value = '';
  inputWidth.value = 24;
};

const confirmEdit = async () => {
  if (!selectedVendor.value) return;
  
  const requestData = {
    vendorID: selectedVendor.value.vendorID,
    shop_name: editedShopName.value,
    badges: editedBadges.value
  };
  
  console.log('Sending to backend:', requestData);
  console.log('Request URL:', 'http://127.0.0.1:8080/update_badges');
  
  try {
    const response = await fetch('http://127.0.0.1:8080/update_badges', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.log('Error response body:', errorText);
      
      // Try to parse the error response as JSON to get the specific error message
      let errorMessage = 'Failed to update vendor. Please try again.';
      try {
        const errorJson = JSON.parse(errorText);
        if (errorJson.error) {
          errorMessage = errorJson.error;
        }
      } catch (parseError) {
        // If it's not JSON, use the raw error text
        errorMessage = errorText || `HTTP error! status: ${response.status}`;
      }
      
      // Show error message in browser alert
      alert(`Backend Connection Error: ${errorMessage}`);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Update successful:', result);
    
    // Create updated vendor object
    const updatedVendor: Vendor = {
      ...selectedVendor.value,
      shop_name: editedShopName.value,
      badges: [...editedBadges.value]
    };
    
    // Emit the updated vendor to parent to update the store
    emit('vendorUpdated', updatedVendor);
    
    closeEditModal();
  } catch (error) {
    console.error('Error updating vendor:', error);
    
    // Show connection error in browser if fetch fails completely
    if (error instanceof TypeError && error.message.includes('fetch')) {
      alert('Backend Connection Error: Unable to connect to the server. Please check if the backend is running on http://127.0.0.1:5000');
    } else if (!error.message.includes('Backend Connection Error')) {
      // Only show generic error if we haven't already shown a specific backend error
      alert(`Error updating vendor: ${error.message}`);
    }
  }
};

const startAddBadge = async () => {
  isAddingBadge.value = true;
  newBadgeText.value = '';
  inputWidth.value = 24; // Reset to circle width
  
  // Focus the input field after it appears
  await nextTick();
  if (badgeInput.value) {
    badgeInput.value.focus();
  }
};

const confirmAddBadge = () => {
  const trimmedText = newBadgeText.value.trim();
  if (trimmedText && !editedBadges.value.includes(trimmedText)) {
    editedBadges.value.push(trimmedText);
  }
  
  // Reset add badge state
  isAddingBadge.value = false;
  newBadgeText.value = '';
  inputWidth.value = 24;
};

const cancelAddBadge = () => {
  isAddingBadge.value = false;
  newBadgeText.value = '';
  inputWidth.value = 24;
};

const adjustInputWidth = () => {
  if (badgeInput.value) {
    // Create a temporary span to measure text width
    const span = document.createElement('span');
    span.style.visibility = 'hidden';
    span.style.position = 'absolute';
    span.style.fontSize = '12px'; // text-xs
    span.style.fontFamily = getComputedStyle(badgeInput.value).fontFamily;
    span.textContent = newBadgeText.value || ' '; // Use single space if empty
    
    document.body.appendChild(span);
    const textWidth = span.offsetWidth;
    document.body.removeChild(span);
    
    // Add padding for px-3 (12px each side) plus some extra space
    const minWidth = 24; // Minimum width (circle size)
    const calculatedWidth = Math.max(minWidth, textWidth + 30);
    inputWidth.value = calculatedWidth;
  }
};

const removeBadge = (index: number) => {
  editedBadges.value.splice(index, 1);
};
</script>

<style scoped>
.vendor-card:hover .edit-icon {
  opacity: 1;
}

.edit-icon:hover {
  transform: scale(1.1);
}

.badge-item {
  position: relative;
}

.delete-badge {
  z-index: 10;
}

.modal-overlay {
  /* Remove backdrop filter for lighter effect */
}

.modal-content {
  animation: modalAppear 0.2s ease-out;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>