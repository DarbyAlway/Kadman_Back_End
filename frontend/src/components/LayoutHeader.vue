<!-- src/components/LayoutHeader.vue -->
<template>
  <div class="h-full bg-white border-b border-gray-100 px-5 flex items-center">
    <div class="flex justify-between items-center w-full">
      <h2 class="text-lg font-semibold text-gray-900">Market Visualization</h2>
      <div class="flex space-x-3">
        <!-- Begin Attendance Button -->
        <button
          v-if="selectedLayout && !hasUnsavedChanges"
          @click="showBeginAttendanceModal = true"
          class="px-4 py-2 text-sm font-medium text-green-700 bg-green-50 border border-green-200 hover:bg-green-100 rounded-md transition-colors duration-200"
          title="Begin Attendance Process"
        >
          Begin Attendance
        </button>

        <!-- Select Layout Dropdown -->
        <div class="relative">
          <button
            @click="toggleDropdown"
            class="flex items-center justify-between w-56 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors duration-200"
          >
            <span>{{ selectedLayoutName || 'Select Layout' }}</span>
            <svg 
              class="w-4 h-4 transition-transform duration-200"
              :class="{ 'rotate-180': isDropdownOpen }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Overlay Rename Input (appears on top of dropdown button) -->
          <div
            v-if="selectedLayout && isRenaming"
            class="absolute inset-0 z-50"
          >
            <input
              ref="renameInput"
              v-model="tempLayoutName"
              @keyup.enter="confirmRename"
              @keyup.escape="cancelRename"
              @blur="cancelRename"
              type="text"
              class="w-full h-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border-2 border-blue-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-lg"
              placeholder="Enter layout name"
            />
          </div>
          
          <!-- Dropdown Menu -->
          <div
            v-if="isDropdownOpen && !isRenaming"
            class="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-md shadow-lg z-40"
          >
            <!-- Always show Create New Layout option at the top -->
            <div class="py-1 border-b border-gray-100">
              <a
                href="#"
                @click.prevent="handleCreateNewLayout"
                class="flex items-center px-4 py-2 text-sm text-green-700 hover:bg-green-50 font-medium"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Create New Layout
              </a>
            </div>

            <!-- Existing layouts section -->
            <div v-if="loadingLayouts" class="py-2 px-4 text-sm text-gray-500">
              Loading layouts...
            </div>
            <div v-else-if="layoutError" class="py-2 px-4 text-sm text-red-500">
              Failed to load layouts
            </div>
            <div v-else-if="layouts.length === 0" class="py-2 px-4 text-sm text-gray-500">
              No existing layouts
            </div>
            <div v-else class="py-1">
              <a
                v-for="layout in layouts"
                :key="layout.id"
                href="#"
                @click.prevent="handleSelectLayout(layout)"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                :class="{ 'bg-blue-50 text-blue-700': selectedLayout?.id === layout.id }"
              >
                {{ layout.name }}
              </a>
            </div>
          </div>
        </div>

        <!-- Debug Info Button -->
        <button
          v-if="selectedLayout"
          @click="showDebugInfo"
          class="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
          title="Debug Layout Data"
        >
          Debug
        </button>

        <!-- Rename Button (stays visible even when renaming) -->
        <button
          v-if="selectedLayout"
          @click="startRename"
          class="px-3 py-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
          :class="{ 'bg-blue-100 border-blue-300': isRenaming }"
          title="Rename Layout"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </button>

        <!-- Save Button with visual indicator for unsaved changes -->
        <button
          @click="handleSave"
          class="px-4 py-2 text-sm font-medium text-white rounded-md transition-colors duration-200"
          :class="hasUnsavedChanges ? 'bg-orange-600 hover:bg-orange-700' : 'bg-blue-600 hover:bg-blue-700'"
          :title="hasUnsavedChanges ? 'You have unsaved changes' : 'Save layout'"
        >
          <span v-if="hasUnsavedChanges" class="mr-1">●</span>
          Save
        </button>

        <!-- Trash Button -->
        <button
          @click="handleDelete"
          class="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors duration-200"
          title="Delete"
        >
          <svg 
            class="w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" 
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Begin Attendance Confirmation Modal -->
    <div
      v-if="showBeginAttendanceModal"
      class="modal-overlay fixed inset-0 flex items-center justify-center z-50"
      style="background-color: rgba(0, 0, 0, 0.25);"
    >
      <div
        class="modal-content bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
      >
        <div class="mb-4">
          <div class="flex items-center mb-4">
            <svg class="w-6 h-6 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900">Begin Attendance Process</h3>
          </div>
          
          <p class="text-gray-600 mb-6">
            Are you sure you want to begin the attendance process for "<strong>{{ selectedLayout?.name }}</strong>"? This will:
            <br/>• Send attendance notifications to all vendors via LINE
            <br/>• Set all vendor statuses to "pending attendance"
            <br/>• Activate the layout status
          </p>
        </div>

        <div class="flex space-x-3 justify-end">
          <button
            @click="showBeginAttendanceModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="confirmBeginAttendance"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors duration-200"
          >
            Begin Attendance
          </button>
        </div>
      </div>
    </div>

    <!-- Unsaved Changes Confirmation Modal -->
    <div
      v-if="showUnsavedModal"
      class="modal-overlay fixed inset-0 flex items-center justify-center z-50"
      style="background-color: rgba(0, 0, 0, 0.25);"
    >
      <div
        class="modal-content bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
      >
        <div class="mb-4">
          <div class="flex items-center mb-4">
            <svg class="w-6 h-6 text-orange-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900">Unsaved Changes</h3>
          </div>
          
          <p class="text-gray-600 mb-6">
            You have unsaved changes. Do you want to save before continuing?
          </p>
        </div>

        <div class="flex space-x-3 justify-end">
          <button
            @click="discardChanges"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
          >
            Don't Save
          </button>
          <button
            @click="cancelAction"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="saveAndContinue"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
          >
            Save & Continue
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="modal-overlay fixed inset-0 flex items-center justify-center z-50"
      style="background-color: rgba(0, 0, 0, 0.25);"
    >
      <div
        class="modal-content bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
      >
        <div class="mb-4">
          <div class="flex items-center mb-4">
            <svg class="w-6 h-6 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clip-rule="evenodd" />
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 000 2v3a1 1 0 001 1h4a1 1 0 001-1v-3a1 1 0 100-2H7z" clip-rule="evenodd" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900">Delete Layout</h3>
          </div>
          
          <p class="text-gray-600 mb-6">
            Are you sure you want to delete "<strong>{{ selectedLayout?.name }}</strong>"? This action cannot be undone.
          </p>
        </div>

        <div class="flex space-x-3 justify-end">
          <button
            @click="cancelDelete"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors duration-200"
          >
            Delete Layout
          </button>
        </div>
      </div>
    </div>

    <!-- Debug Modal -->
    <div
      v-if="showDebugModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="hideDebugInfo"
    >
      <div
        class="bg-white rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-auto"
        @click.stop
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Debug Layout Data</h3>
          <button
            @click="hideDebugInfo"
            class="text-gray-500 hover:text-gray-700"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div v-if="selectedLayout" class="space-y-4">
          <div>
            <h4 class="font-medium text-gray-900">Layout Info:</h4>
            <pre class="bg-gray-100 p-3 rounded text-sm">{{ JSON.stringify({
              id: selectedLayout.id,
              name: selectedLayout.name,
              dataKeysCount: Object.keys(selectedLayout.data || {}).length
            }, null, 2) }}</pre>
          </div>
          
          <div>
            <h4 class="font-medium text-gray-900">First 10 Data Entries:</h4>
            <pre class="bg-gray-100 p-3 rounded text-sm max-h-96 overflow-auto">{{ JSON.stringify(
              Object.fromEntries(
                Object.entries(selectedLayout.data || {}).slice(0, 10)
              ), null, 2) }}</pre>
          </div>
          
          <div>
            <h4 class="font-medium text-gray-900">Non-null Assignments:</h4>
            <pre class="bg-gray-100 p-3 rounded text-sm max-h-96 overflow-auto">{{ JSON.stringify(
              Object.fromEntries(
                Object.entries(selectedLayout.data || {}).filter(([key, value]) => value.vendorID !== null)
              ), null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import { LayoutService } from '../services/layoutService';
import type { Layout } from '../types/api';

const emit = defineEmits<{
  layoutSelected: [layout: Layout];
  currentLayoutData: [data: any];
}>();

const isDropdownOpen = ref(false);
const layouts = ref<Layout[]>([]);
const selectedLayout = ref<Layout | null>(null);
const originalLayout = ref<Layout | null>(null); // Store original state for comparison
const loadingLayouts = ref(false);
const layoutError = ref(false);
const showDebugModal = ref(false);
const isRenaming = ref(false);
const tempLayoutName = ref('');
const renameInput = ref<HTMLInputElement | null>(null);

// Unsaved changes modal
const showUnsavedModal = ref(false);
const pendingAction = ref<(() => void) | null>(null);

// Delete confirmation modal
const showDeleteModal = ref(false);

// Begin Attendance modal
const showBeginAttendanceModal = ref(false);

// Current layout data from parent (for detecting changes)
const currentLayoutData = ref<any>({});

const BASE_URL = 'http://127.0.0.1:8080';

const selectedLayoutName = computed(() => {
  if (!selectedLayout.value) return null;
  
  // Show asterisk for new/unsaved layouts
  const isNewLayout = selectedLayout.value.id > 1000000000; // Temporary IDs are large timestamps
  return isNewLayout ? `${selectedLayout.value.name} *` : selectedLayout.value.name;
});

const hasUnsavedChanges = computed(() => {
  if (!selectedLayout.value || !originalLayout.value) return false;
  
  // Check if name changed (from rename)
  const nameChanged = selectedLayout.value.name !== originalLayout.value.name;
  
  // Check if layout data changed (vendor assignments)
  // Ensure both are properly formatted for comparison
  const originalData = originalLayout.value.data || {};
  const currentData = currentLayoutData.value || {};
  
  // Normalize the data for comparison - only compare non-null entries
  const normalizeData = (data: any) => {
    const normalized: any = {};
    Object.entries(data).forEach(([key, value]: [string, any]) => {
      if (value && value.vendorID !== null && value.vendorID !== undefined) {
        normalized[key] = {
          vendorID: value.vendorID,
          shop_name: value.shop_name
        };
      }
    });
    return normalized;
  };
  
  const normalizedOriginal = normalizeData(originalData);
  const normalizedCurrent = normalizeData(currentData);
  
  const dataChanged = JSON.stringify(normalizedCurrent) !== JSON.stringify(normalizedOriginal);
  
  console.log('Unsaved changes check:', {
    nameChanged,
    dataChanged,
    originalDataKeys: Object.keys(normalizedOriginal).length,
    currentDataKeys: Object.keys(normalizedCurrent).length,
    originalData: normalizedOriginal,
    currentData: normalizedCurrent
  });
  
  return nameChanged || dataChanged;
});

// Watch for current layout data changes from parent
const updateCurrentLayoutData = (data: any) => {
  console.log('LayoutHeader: updateCurrentLayoutData called with:', {
    dataKeys: Object.keys(data || {}).length,
    data: data
  });
  
  currentLayoutData.value = data;
  
  console.log('LayoutHeader: After update:', {
    hasUnsavedChanges: hasUnsavedChanges.value,
    currentDataKeys: Object.keys(currentLayoutData.value).length,
    originalDataKeys: Object.keys(originalLayout.value?.data || {}).length
  });
};

defineExpose({ updateCurrentLayoutData });

const toggleDropdown = async () => {
  // Don't open dropdown if currently renaming
  if (isRenaming.value) return;
  
  if (!isDropdownOpen.value && layouts.value.length === 0) {
    await fetchLayouts();
  }
  isDropdownOpen.value = !isDropdownOpen.value;
};

const fetchLayouts = async () => {
  loadingLayouts.value = true;
  layoutError.value = false;
  
  try {
    const fetchedLayouts = await LayoutService.getAllLayouts();
    layouts.value = fetchedLayouts;
    console.log('LayoutHeader: Fetched layouts:', fetchedLayouts);
  } catch (error) {
    console.error('LayoutHeader: Error fetching layouts:', error);
    layoutError.value = true;
  } finally {
    loadingLayouts.value = false;
  }
};

const checkUnsavedChanges = (nextAction: () => void) => {
  if (hasUnsavedChanges.value) {
    pendingAction.value = nextAction;
    showUnsavedModal.value = true;
  } else {
    nextAction();
  }
};

const handleCreateNewLayout = () => {
  checkUnsavedChanges(() => {
    createNewLayout();
  });
};

const handleSelectLayout = (layout: Layout) => {
  checkUnsavedChanges(() => {
    selectLayout(layout);
  });
};

const discardChanges = () => {
  showUnsavedModal.value = false;
  if (pendingAction.value) {
    pendingAction.value();
    pendingAction.value = null;
  }
};

const cancelAction = () => {
  showUnsavedModal.value = false;
  pendingAction.value = null;
};

const saveAndContinue = async () => {
  try {
    await handleSave();
    showUnsavedModal.value = false;
    if (pendingAction.value) {
      pendingAction.value();
      pendingAction.value = null;
    }
  } catch (error) {
    console.error('Error saving layout:', error);
    // Keep modal open if save failed
  }
};

const startRename = async () => {
  if (!selectedLayout.value) return;
  
  // Close dropdown if open
  isDropdownOpen.value = false;
  
  isRenaming.value = true;
  tempLayoutName.value = selectedLayout.value.name;
  
  // Focus the input field after it appears
  await nextTick();
  if (renameInput.value) {
    renameInput.value.focus();
    renameInput.value.select(); // Select all text for easy replacement
  }
};

const confirmRename = () => {
  if (!selectedLayout.value || !tempLayoutName.value.trim()) {
    cancelRename();
    return;
  }
  
  const newName = tempLayoutName.value.trim();
  const oldName = selectedLayout.value.name;
  
  // Update the layout name
  selectedLayout.value = {
    ...selectedLayout.value,
    name: newName
  };
  
  console.log('Layout renamed from:', oldName, 'to:', newName);
  
  // Reset rename state
  isRenaming.value = false;
  tempLayoutName.value = '';
};

const cancelRename = () => {
  isRenaming.value = false;
  tempLayoutName.value = '';
  console.log('Rename cancelled');
};

const createNewLayout = () => {
  isDropdownOpen.value = false;
  
  // Create a new empty layout
  const newLayout: Layout = {
    id: Date.now(), // Temporary ID until saved to backend
    name: `New Layout ${new Date().toLocaleDateString()}`,
    data: {}
  };
  
  selectedLayout.value = newLayout;
  originalLayout.value = JSON.parse(JSON.stringify(newLayout)); // Deep copy
  currentLayoutData.value = {};
  
  console.log('Created new layout:', newLayout);
  
  // Emit the new layout to parent component
  emit('layoutSelected', newLayout);
};

const selectLayout = (layout: Layout) => {
  console.log('LayoutHeader: selectLayout called with:', layout.name);
  
  selectedLayout.value = layout;
  originalLayout.value = JSON.parse(JSON.stringify(layout)); // Deep copy for comparison
  isDropdownOpen.value = false;
  
  // Initialize current layout data to exactly match the original layout data
  // This prevents false positive unsaved changes on initial load
  currentLayoutData.value = JSON.parse(JSON.stringify(layout.data || {}));
  
  console.log('LayoutHeader: Initialized data:', {
    layoutName: layout.name,
    originalDataKeys: Object.keys(layout.data || {}).length,
    currentDataKeys: Object.keys(currentLayoutData.value).length,
    hasUnsavedChanges: hasUnsavedChanges.value
  });
  
  // Emit the selected layout to parent component
  emit('layoutSelected', layout);
};

const showDebugInfo = () => {
  showDebugModal.value = true;
};

const hideDebugInfo = () => {
  showDebugModal.value = false;
};

const handleSave = async () => {
  if (!selectedLayout.value) {
    console.log('No layout selected to save');
    return;
  }

  const isNewLayout = selectedLayout.value.id > 1000000000; // Temporary IDs are large timestamps
  
  try {
    if (isNewLayout) {
      console.log('Saving new layout:', selectedLayout.value.name);
      const newId = await LayoutService.insertLayout(selectedLayout.value.name, currentLayoutData.value);
      
      // Update the layout with the real ID from database
      selectedLayout.value = {
        ...selectedLayout.value,
        id: newId,
        data: currentLayoutData.value
      };
      
      // Update original layout for comparison
      originalLayout.value = JSON.parse(JSON.stringify(selectedLayout.value));
      
      alert('New layout saved successfully!');
    } else {
      console.log('Updating existing layout:', selectedLayout.value.name);
      await LayoutService.updateLayout(selectedLayout.value.id, selectedLayout.value.name, currentLayoutData.value);
      
      // Update the selected layout's data with current data
      selectedLayout.value = {
        ...selectedLayout.value,
        data: currentLayoutData.value
      };
      
      // Update original layout for comparison
      originalLayout.value = JSON.parse(JSON.stringify(selectedLayout.value));
      
      alert('Layout updated successfully!');
    }
    
    // Refresh layouts list to get updated data from database
    await fetchLayouts();
    
    // Update the layouts array with the current layout's updated data
    const layoutIndex = layouts.value.findIndex(l => l.id === selectedLayout.value!.id);
    if (layoutIndex !== -1) {
      layouts.value[layoutIndex] = JSON.parse(JSON.stringify(selectedLayout.value));
    }
    
  } catch (error) {
    console.error('Error saving layout:', error);
    alert(`Error saving layout: ${error.message}`);
    throw error; // Re-throw for saveAndContinue to handle
  }
};

const handleDelete = () => {
  if (!selectedLayout.value) {
    console.log('No layout selected to delete');
    return;
  }

  // Check for unsaved changes before showing delete modal
  if (hasUnsavedChanges.value) {
    // Set pending action to show delete modal after handling unsaved changes
    checkUnsavedChanges(() => {
      showDeleteModal.value = true;
    });
  } else {
    // No unsaved changes, show delete modal directly
    showDeleteModal.value = true;
  }
};

const confirmDelete = async () => {
  if (!selectedLayout.value) return;

  const isNewLayout = selectedLayout.value.id > 1000000000; // Temporary IDs are large timestamps
  
  if (isNewLayout) {
    // For new layouts that haven't been saved, just clear the selection
    selectedLayout.value = null;
    originalLayout.value = null;
    currentLayoutData.value = {};
    showDeleteModal.value = false;
    
    // Emit event to clear the layout in parent
    emit('layoutSelected', { id: 0, name: '', data: {} } as Layout);
    
    alert('New layout cleared successfully!');
    return;
  }

  try {
    await LayoutService.deleteLayout(selectedLayout.value.id);
    
    // Remove from layouts list
    layouts.value = layouts.value.filter(l => l.id !== selectedLayout.value!.id);
    
    // Clear current selection
    selectedLayout.value = null;
    originalLayout.value = null;
    currentLayoutData.value = {};
    
    showDeleteModal.value = false;
    
    // Emit event to clear the layout in parent
    emit('layoutSelected', { id: 0, name: '', data: {} } as Layout);
    
    alert('Layout deleted successfully!');
  } catch (error) {
    console.error('Error deleting layout:', error);
    alert(`Error deleting layout: ${error.message}`);
  }
};

const cancelDelete = () => {
  showDeleteModal.value = false;
};

const confirmBeginAttendance = async () => {
  if (!selectedLayout.value) {
    console.log('No layout selected');
    return;
  }

  console.log('Beginning attendance process for layout:', selectedLayout.value.name);
  
  try {
    showBeginAttendanceModal.value = false;
    
    const response = await fetch(`${BASE_URL}/begin_attendance/${selectedLayout.value.id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const results = await response.json();
    console.log('Begin attendance results:', results);
    
    // Count successful notifications
    const successfulNotifications = results.filter((r: any) => 
      r.notification_status === 200 || r.notification_status === '200'
    ).length;
    
    const totalVendors = results.length;
    
    alert(`Attendance process started successfully!\n\nNotifications sent to ${successfulNotifications} out of ${totalVendors} vendors.\n\nLayout has been activated and vendor statuses set to "pending attendance".\n\nCheck console for detailed results.`);
    
  } catch (error) {
    console.error('Error beginning attendance process:', error);
    alert(`Error starting attendance process: ${error.message}`);
  }
};

// Close dropdown when clicking outside
const closeDropdown = () => {
  isDropdownOpen.value = false;
};

// Add event listener to close dropdown when clicking outside
if (typeof window !== 'undefined') {
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    if (!target.closest('.relative')) {
      closeDropdown();
    }
  });
}

onMounted(() => {
  // Optionally fetch layouts on mount
  // fetchLayouts();
});
</script>