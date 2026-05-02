<!-- src/views/Attendance.vue -->
<template>
  <div class="h-full bg-gray-50 overflow-auto">
    <!-- Header -->
    <div class="bg-white border-b border-gray-100 px-6 py-4 sticky top-0 z-10">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Attendance Management</h1>
          <p class="text-gray-600 text-sm mt-1">Monitor vendor attendance for active layouts</p>
        </div>
        <div class="flex space-x-3">
          <button 
            @click="showResetAttendanceModal = true"
            class="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 hover:bg-red-100 rounded-md transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            End Attendance
          </button>
          <button 
            @click="showResetQuotaModal = true"
            class="px-4 py-2 text-sm font-medium text-orange-700 bg-orange-50 border border-orange-200 hover:bg-orange-100 rounded-md transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset Quota
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Vendors</dt>
                <dd class="text-lg font-medium text-gray-900">{{ totalVendors }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Complete</dt>
                <dd class="text-lg font-medium text-gray-900">{{ completeCount }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Pending Attendance</dt>
                <dd class="text-lg font-medium text-gray-900">{{ pendingAttendanceCount }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Pending Payment</dt>
                <dd class="text-lg font-medium text-gray-900">{{ pendingPaymentCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-500">Loading active layouts...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error Loading Data</h3>
            <p class="text-sm text-red-600 mt-1">{{ error }}</p>
          </div>
        </div>
        <button 
          @click="fetchActiveLayouts"
          class="mt-3 px-3 py-1.5 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-md transition-colors duration-200"
        >
          Try Again
        </button>
      </div>

      <!-- Layout Tables -->
      <div v-if="!loading && !error && mockData.length > 0" class="space-y-6">
        <div
          v-for="layout in mockData"
          :key="layout.id"
          class="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden"
        >
          <!-- Layout Header -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-100">
            <div class="flex justify-between items-center">
              <div class="flex items-center space-x-4">
                <h3 class="text-lg font-semibold text-gray-900">{{ layout.name }}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <svg class="w-2 h-2 mr-1" fill="currentColor" viewBox="0 0 8 8">
                    <circle cx="4" cy="4" r="3" />
                  </svg>
                  {{ layout.status }}
                </span>
                <span class="text-sm text-gray-600">
                  Layout ID: <span class="font-medium">{{ layout.id }}</span>
                </span>
              </div>
              <div class="flex space-x-2">
              </div>
            </div>
          </div>

          <!-- Vendors Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vendor Information
                  </th>
                  <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="(vendor, position) in layout.data"
                  :key="`${layout.id}-${position}`"
                  class="hover:bg-gray-50 transition-colors duration-150"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span class="text-xs font-medium text-blue-800">{{ position }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex flex-col">
                      <div class="text-sm font-medium text-gray-900">{{ vendor.shop_name }}</div>
                      <div class="text-sm text-gray-500">ID: {{ vendor.vendorID }}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="flex flex-col items-center">
                      <span 
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getStatusClasses(vendor.status)"
                      >
                        <svg 
                          class="w-2 h-2 mr-1" 
                          :class="getStatusIconClasses(vendor.status)"
                          fill="currentColor" 
                          viewBox="0 0 8 8"
                        >
                          <circle cx="4" cy="4" r="3" />
                        </svg>
                        {{ formatStatus(vendor.status) }}
                      </span>
                      <!-- Show expected payment under status for pending payment -->
                      <div 
                        v-if="vendor.status === 'pending payment' && vendorPayments[vendor.vendorID]"
                        class="text-xs text-orange-600 font-medium mt-1"
                      >
                        Expected: ฿{{ vendorPayments[vendor.vendorID]?.toLocaleString() || '0' }}
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Empty State (when no active layouts) -->
      <div v-else-if="!loading && !error && mockData.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No active layouts</h3>
        <p class="mt-1 text-sm text-gray-500">There are currently no active layouts to display.</p>
      </div>

      <!-- Reset Attendance Confirmation Modal -->
      <div
        v-if="showResetAttendanceModal"
        class="modal-overlay fixed inset-0 flex items-center justify-center z-50"
        style="background-color: rgba(0, 0, 0, 0.25);"
      >
        <div
          class="modal-content bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
        >
          <div class="mb-4">
            <div class="flex items-center mb-4">
              <svg class="w-6 h-6 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900">End All Attendance</h3>
            </div>
            
            <p class="text-gray-600 mb-6">
              Are you sure you want to end all attendance data? This will:
              <br/>• Clear all vendor statuses (set to empty)
              <br/>• Set all layouts to "inactive" status
              <br/>This action cannot be undone.
            </p>
          </div>

          <div class="flex space-x-3 justify-end">
            <button
              @click="showResetAttendanceModal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              @click="confirmResetAllAttendance"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors duration-200"
            >
              End All Attendance
            </button>
          </div>
        </div>
      </div>

      <!-- Reset Quota Confirmation Modal -->
      <div
        v-if="showResetQuotaModal"
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
              <h3 class="text-lg font-semibold text-gray-900">Reset Quota</h3>
            </div>
            
            <p class="text-gray-600 mb-6">
              Are you sure you want to reset the quota data? This will reset all quota-related information for all vendors. This action cannot be undone.
            </p>
          </div>

          <div class="flex space-x-3 justify-end">
            <button
              @click="showResetQuotaModal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              @click="confirmResetAttendance"
              class="px-4 py-2 text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 rounded-md transition-colors duration-200"
            >
              Reset Quota
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

// Data state
const mockData = ref([]);
const loading = ref(false);
const error = ref<string | null>(null);
const showResetAttendanceModal = ref(false);
const showResetQuotaModal = ref(false);
const vendorPayments = ref<Record<number, number>>({}); // Store payment amounts by vendorID

const BASE_URL = 'http://127.0.0.1:8080';

// API Functions
const fetchActiveLayouts = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`${BASE_URL}/get_all_active_layout`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    mockData.value = data;
    console.log('Fetched active layouts:', data);
    
    // Fetch payment data for vendors with pending payment status
    await fetchPaymentData(data);
    
  } catch (err) {
    console.error('Error fetching active layouts:', err);
    error.value = 'Failed to load active layouts';
    
    // Fallback to mock data for demo purposes
    mockData.value = [
      {
        "data": {
          "B1": {
            "shop_name": "Pattaranon",
            "status": "pending attendance",
            "vendorID": 112
          },
          "B2": {
            "shop_name": "Ananta",
            "status": "pending attendance",
            "vendorID": 113
          },
          "B3": {
            "shop_name": "Somchai Store",
            "status": "complete",
            "vendorID": 114
          },
          "B4": {
            "shop_name": "Niran Shop",
            "status": "pending payment",
            "vendorID": 115
          },
          "A1": {
            "shop_name": "Kamon Market",
            "status": "complete",
            "vendorID": 116
          },
          "A2": {
            "shop_name": "Siriporn Goods",
            "status": "pending attendance",
            "vendorID": 117
          }
        },
        "id": 3,
        "name": "Layout_test1",
        "status": "active"
      }
    ];
  } finally {
    loading.value = false;
  }
};

// Fetch payment data for vendors with pending payment status
const fetchPaymentData = async (layouts: any[]) => {
  const pendingPaymentVendors: number[] = [];
  
  // Collect all vendor IDs with pending payment status
  layouts.forEach(layout => {
    Object.values(layout.data).forEach((vendor: any) => {
      if (vendor.status === 'pending payment' && vendor.vendorID) {
        pendingPaymentVendors.push(vendor.vendorID);
      }
    });
  });
  
  // Fetch payment data for each vendor
  const paymentPromises = pendingPaymentVendors.map(async (vendorID) => {
    try {
      const response = await fetch(`${BASE_URL}/get_payment/${vendorID}`);
      if (response.ok) {
        const data = await response.json();
        return { vendorID, payment: data.payment };
      }
    } catch (err) {
      console.error(`Error fetching payment for vendor ${vendorID}:`, err);
    }
    return { vendorID, payment: 0 }; // Default to 0 if fetch fails
  });
  
  const paymentResults = await Promise.all(paymentPromises);
  
  // Store payment data in vendorPayments ref
  paymentResults.forEach(({ vendorID, payment }) => {
    vendorPayments.value[vendorID] = payment || 0;
  });
  
  console.log('Fetched payment data:', vendorPayments.value);
};

const resetAllAttendance = async () => {
  try {
    const response = await fetch(`${BASE_URL}/reset_all_attendance`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Reset all attendance successful:', result);
    alert('All layouts reset: vendor statuses cleared and layouts set to inactive.');
    
    // Refresh data after reset
    await fetchActiveLayouts();
  } catch (err) {
    console.error('Error resetting all attendance:', err);
    alert(`Error resetting attendance: ${err.message}`);
  } finally {
    showResetAttendanceModal.value = false;
  }
};

const resetAttendance = async () => {
  try {
    const response = await fetch(`${BASE_URL}/reset_attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Reset attendance successful:', result);
    alert('Attendance has been reset successfully!');
    
    // Refresh data after reset
    await fetchActiveLayouts();
  } catch (err) {
    console.error('Error resetting attendance:', err);
    alert(`Error resetting attendance: ${err.message}`);
  } finally {
    showResetQuotaModal.value = false;
  }
};

const confirmResetAllAttendance = () => {
  resetAllAttendance();
};

const confirmResetAttendance = () => {
  resetAttendance();
};

// Computed stats with correct status values
const totalVendors = computed(() => {
  let count = 0;
  mockData.value.forEach(layout => {
    count += Object.keys(layout.data).length;
  });
  return count;
});

const completeCount = computed(() => {
  let count = 0;
  mockData.value.forEach(layout => {
    Object.values(layout.data).forEach(vendor => {
      if (vendor.status === 'complete') count++;
    });
  });
  return count;
});

const pendingAttendanceCount = computed(() => {
  let count = 0;
  mockData.value.forEach(layout => {
    Object.values(layout.data).forEach(vendor => {
      if (vendor.status === 'pending attendance') count++;
    });
  });
  return count;
});

const pendingPaymentCount = computed(() => {
  let count = 0;
  mockData.value.forEach(layout => {
    Object.values(layout.data).forEach(vendor => {
      if (vendor.status === 'pending payment') count++;
    });
  });
  return count;
});

// Helper functions with correct status values
const getStatusClasses = (status: string) => {
  switch (status) {
    case 'complete':
      return 'bg-green-100 text-green-800';
    case 'pending payment':
      return 'bg-orange-100 text-orange-800';
    case 'pending attendance':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStatusIconClasses = (status: string) => {
  switch (status) {
    case 'complete':
      return 'text-green-400';
    case 'pending payment':
      return 'text-orange-400';
    case 'pending attendance':
      return 'text-yellow-400';
    default:
      return 'text-gray-400';
  }
};

const formatStatus = (status: string) => {
  switch (status) {
    case 'pending attendance':
      return 'Pending Attendance';
    case 'pending payment':
      return 'Pending Payment';
    case 'complete':
      return 'Complete';
    default:
      return status;
  }
};

const getRandomTime = () => {
  const times = ['2 min ago', '5 min ago', '10 min ago', '15 min ago', '30 min ago', '1 hour ago'];
  return times[Math.floor(Math.random() * times.length)];
};

// Lifecycle
onMounted(() => {
  fetchActiveLayouts();
});
</script>