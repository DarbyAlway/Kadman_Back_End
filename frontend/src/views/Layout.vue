<!-- src/views/Layout.vue -->
<template>
  <div class="h-full flex bg-gray-50">
    <!-- Left Sidebar - 20% width -->
    <div class="w-[20%] bg-white border-r border-gray-100 flex flex-col">
      <!-- Search Bar Section - Fixed Height (72px - 10% smaller) -->
      <div class="h-18 p-5 border-b border-gray-100 flex items-center flex-shrink-0">
        <SearchBar @search="handleSearch" />
      </div>
      
      <!-- Search Results Section - Remaining height -->
      <div class="flex-1 min-h-0">
        <div class="h-full overflow-y-auto p-5">
          <SearchResults 
            :results="searchResults" 
            :loading="isLoading"
            :error="errorMessage"
            :vendor-store="vendorStore"
            @vendor-updated="handleVendorUpdated"
          />
        </div>
      </div>
    </div>
    
    <!-- Right Content - 80% width -->
    <div class="w-[80%] flex flex-col">
      <!-- Header - Fixed Height (72px - 10% smaller) -->
      <div class="h-18 flex-shrink-0">
        <LayoutHeader 
          ref="layoutHeaderRef"
          @layout-selected="handleLayoutSelected" 
        />
      </div>
      
      <!-- Main Content Area - Grid Visualization -->
      <div class="flex-1 min-h-0 p-5">
        <GridVisualization 
          :vendor-store="vendorStore"
          :layout-assignments="layoutAssignments"
          @vendor-assigned="handleVendorAssigned"
          @vendor-removed="handleVendorRemoved"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import SearchBar from '../components/SearchBar.vue';
import SearchResults from '../components/SearchResults.vue';
import LayoutHeader from '../components/LayoutHeader.vue';
import GridVisualization from '../components/GridVisualization.vue';
import { SearchService } from '../services/searchService';
import { semanticToGrid, gridToSemantic } from '../utils/cellMapping';
import type { Vendor, AssignedVendor, VendorStore, Layout } from '../types/api';

const searchResults = ref<Vendor[]>([]);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const assignedVendors = ref<AssignedVendor[]>([]);
const vendorStore = ref<VendorStore>({});
const selectedLayout = ref<Layout | null>(null);
const layoutAssignments = ref<Map<string, AssignedVendor>>(new Map());
const layoutHeaderRef = ref();

const handleSearch = async (query: string) => {
  isLoading.value = true;
  errorMessage.value = null;
  
  try {
    const results = await SearchService.search({ q: query });
    searchResults.value = results;
    
    // Update vendor store with search results
    results.forEach(vendor => {
      vendorStore.value[vendor.vendorID] = vendor;
    });
  } catch (error) {
    errorMessage.value = 'Failed to search vendors';
    searchResults.value = [];
    console.error('Search error:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleVendorAssigned = (vendorID: number, cellKey: string) => {
  const existingIndex = assignedVendors.value.findIndex(av => av.cellKey === cellKey);
  
  const newAssignment: AssignedVendor = {
    vendorID,
    cellKey,
    assignedAt: new Date()
  };

  if (existingIndex >= 0) {
    assignedVendors.value[existingIndex] = newAssignment;
  } else {
    assignedVendors.value.push(newAssignment);
  }

  // Also update the layoutAssignments map
  layoutAssignments.value.set(cellKey, newAssignment);

  console.log('Vendor assigned:', vendorID, 'to cell:', cellKey);
  
  // Only update header when there's an actual change (not during initial layout load)
  updateHeaderWithCurrentData();
};

const handleVendorRemoved = (cellKey: string) => {
  // Remove from assignedVendors array
  const existingIndex = assignedVendors.value.findIndex(av => av.cellKey === cellKey);
  if (existingIndex >= 0) {
    assignedVendors.value.splice(existingIndex, 1);
  }

  // Remove from layoutAssignments map
  layoutAssignments.value.delete(cellKey);

  console.log('Vendor removed from cell:', cellKey);
  
  // Update header with current layout data to detect unsaved changes
  updateHeaderWithCurrentData();
};

const handleVendorUpdated = (updatedVendor: Vendor) => {
  // Update vendor store when a vendor is edited
  vendorStore.value[updatedVendor.vendorID] = updatedVendor;
  
  // Update search results if the vendor is in current results
  const resultIndex = searchResults.value.findIndex(v => v.vendorID === updatedVendor.vendorID);
  if (resultIndex !== -1) {
    searchResults.value[resultIndex] = updatedVendor;
  }
};

const handleLayoutSelected = async (layout: Layout) => {
  console.log('Layout selected in Layout.vue:', layout);
  console.log('Layout data structure:', layout.data);
  
  selectedLayout.value = layout;
  
  // Clear existing assignments
  assignedVendors.value = [];
  layoutAssignments.value.clear();
  
  // Process layout data and create assignments with cell mapping
  const newAssignments = new Map<string, AssignedVendor>();
  const vendorIdsNeeded = new Set<number>();
  const mappingLog: Array<{semantic: string, grid: string | null, vendor: number}> = [];
  
  // First pass: collect all vendor IDs and create assignments using cell mapping
  Object.entries(layout.data).forEach(([semanticKey, cellData]) => {
    console.log('Processing semantic key:', semanticKey, 'with data:', cellData);
    
    if (cellData.vendorID !== null && cellData.vendorID !== undefined) {
      // Convert semantic key (A1, B1, Car1, etc.) to grid key (2-28, 6-6, etc.)
      const gridKey = semanticToGrid(semanticKey);
      
      mappingLog.push({
        semantic: semanticKey,
        grid: gridKey,
        vendor: cellData.vendorID
      });
      
      if (gridKey) {
        const assignment: AssignedVendor = {
          vendorID: cellData.vendorID,
          cellKey: gridKey, // Use the mapped grid key
          assignedAt: new Date()
        };
        
        newAssignments.set(gridKey, assignment);
        vendorIdsNeeded.add(cellData.vendorID);
        
        console.log('Mapped:', semanticKey, '->', gridKey, 'vendor:', cellData.vendorID);
      } else {
        console.warn('Could not map semantic key to grid key:', semanticKey);
      }
    }
  });
  
  console.log('Cell mapping results:');
  console.table(mappingLog.slice(0, 20)); // Show first 20 mappings
  console.log('Total successful mappings:', newAssignments.size);
  console.log('Vendor IDs needed:', Array.from(vendorIdsNeeded));
  
  // Fetch vendor data for any missing vendors
  if (vendorIdsNeeded.size > 0) {
    await fetchMissingVendors(vendorIdsNeeded);
  }
  
  // Apply assignments
  assignedVendors.value = Array.from(newAssignments.values());
  layoutAssignments.value = newAssignments;
  
  console.log('Final assigned vendors:', assignedVendors.value.length);
  console.log('Final layout assignments map size:', layoutAssignments.value.size);
  console.log('First 5 grid assignments:', Array.from(layoutAssignments.value.entries()).slice(0, 5));
  
  // DON'T update header data here - let the header manage its own state
  // The header will initialize with the correct original data from the layout parameter
};

const fetchMissingVendors = async (vendorIds: Set<number>) => {
  console.log('Fetching missing vendors:', Array.from(vendorIds));
  
  // Check which vendors we don't have in store
  const missingVendorIds = Array.from(vendorIds).filter(id => !vendorStore.value[id]);
  
  if (missingVendorIds.length === 0) {
    console.log('All vendors already in store');
    return;
  }
  
  console.log('Missing vendor IDs:', missingVendorIds);
  
  try {
    // Fetch vendors by searching for them
    // You might need to implement a specific endpoint for fetching vendors by IDs
    // For now, we'll search for each vendor individually
    for (const vendorId of missingVendorIds) {
      try {
        // This is a workaround - you might want to implement a specific endpoint
        // to fetch vendors by ID array
        const searchResults = await SearchService.search({ q: vendorId.toString() });
        const vendor = searchResults.find(v => v.vendorID === vendorId);
        
        if (vendor) {
          vendorStore.value[vendorId] = vendor;
          console.log('Found and stored vendor:', vendor);
        } else {
          console.warn('Could not find vendor with ID:', vendorId);
          // Create a placeholder vendor
          vendorStore.value[vendorId] = {
            vendorID: vendorId,
            shop_name: `Vendor ${vendorId}`,
            badges: [],
            shop_name_syllables: []
          };
        }
      } catch (error) {
        console.error('Error fetching vendor', vendorId, ':', error);
        // Create a placeholder vendor
        vendorStore.value[vendorId] = {
          vendorID: vendorId,
          shop_name: `Vendor ${vendorId}`,
          badges: [],
          shop_name_syllables: []
        };
      }
    }
  } catch (error) {
    console.error('Error in fetchMissingVendors:', error);
  }
};

// Convert current grid assignments back to semantic format for saving
const getCurrentLayoutData = () => {
  const layoutData: any = {};
  
  // Convert grid assignments back to semantic keys
  layoutAssignments.value.forEach((assignment, gridKey) => {
    const semanticKey = gridToSemantic(gridKey);
    if (semanticKey && vendorStore.value[assignment.vendorID]) {
      layoutData[semanticKey] = {
        vendorID: assignment.vendorID,
        shop_name: vendorStore.value[assignment.vendorID].shop_name
      };
    }
  });
  
  return layoutData;
};

// Update header with current layout data for unsaved changes detection
const updateHeaderWithCurrentData = () => {
  if (layoutHeaderRef.value) {
    const currentData = getCurrentLayoutData();
    layoutHeaderRef.value.updateCurrentLayoutData(currentData);
  }
};

onMounted(() => {
  handleSearch('');
});
</script>