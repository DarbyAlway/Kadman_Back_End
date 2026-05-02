<!-- src/components/GridVisualization.vue -->
<template>
  <div class="w-full h-full bg-white border border-gray-100 rounded-xl shadow-sm overflow-hidden">
    <!-- Scrollable container -->
    <div class="w-full h-full p-4 overflow-auto">
      <div class="grid-container">
        <div class="grid">
          <!-- Individual cells -->
          <div
            v-for="cell in visibleCells"
            :key="`cell-${cell.row}-${cell.col}`"
            class="grid-cell"
            :class="{
              'non-interactive': cell.text === 'Go Kart' || cell.text === 'Parking Zone',
              'occupied': cellOccupationStatus[getCellKey(cell.row, cell.col)],
              'drop-zone': !isNonDroppable(cell.text) && !cellOccupationStatus[getCellKey(cell.row, cell.col)]
            }"
            :style="{
              gridRow: cell.row,
              gridColumn: cell.col,
              ...(cell.text === 'Go Kart' || cell.text === 'Parking Zone' 
                ? { backgroundColor: cell.color, borderColor: '#e0e0e0' }
                : cellOccupationStatus[getCellKey(cell.row, cell.col)]
                  ? { backgroundColor: cell.color, borderColor: cell.color }
                  : { borderColor: cell.color })
            }"
            @dragover="handleDragOver"
            @drop="handleDrop($event, cell.row, cell.col)"
            @mouseenter="handleMouseEnter($event, cell.row, cell.col)"
            @mouseleave="handleMouseLeave($event)"
          >
            <span class="cell-text">{{ getCellDisplayText(cell.row, cell.col, cell.text) }}</span>
          </div>

          <!-- Merged cells -->
          <div
            v-for="(area, index) in mergedAreas"
            :key="`merged-${index}`"
            class="grid-cell merged-cell"
            :class="{
              'non-interactive': area.text === 'Go Kart' || area.text === 'Parking Zone',
              'occupied': areaOccupationStatus[getAreaKey(area)],
              'drop-zone': !isNonDroppable(area.text) && !areaOccupationStatus[getAreaKey(area)]
            }"
            :style="{
              gridRow: `${area.minRow} / ${area.maxRow + 1}`,
              gridColumn: `${area.minCol} / ${area.maxCol + 1}`,
              ...(area.text === 'Go Kart' || area.text === 'Parking Zone' 
                ? { backgroundColor: area.color, borderColor: '#e0e0e0' }
                : areaOccupationStatus[getAreaKey(area)]
                  ? { backgroundColor: area.color, borderColor: area.color }
                  : { borderColor: area.color })
            }"
            @dragover="handleDragOver"
            @drop="handleAreaDrop($event, area)"
            @mouseenter="handleAreaMouseEnter($event, area)"
            @mouseleave="handleMouseLeave($event)"
          >
            <span class="merged-text">{{ getAreaDisplayText(area) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Vendor Info Tooltip -->
    <div
      v-if="hoveredVendor && tooltipPosition"
      class="vendor-tooltip"
      :style="{
        left: tooltipPosition.x + 'px',
        top: tooltipPosition.y + 'px'
      }"
      @mouseenter="handleTooltipMouseEnter"
      @mouseleave="handleTooltipMouseLeave"
    >
      <div class="bg-white text-black p-3 rounded-lg shadow-lg border border-gray-200 max-w-xs relative">
        <!-- Remove button -->
        <button
          @click="removeVendor"
          class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-xs font-bold transition-colors duration-200"
          title="Remove vendor"
        >
          ×
        </button>
        
        <h4 class="font-semibold text-sm mb-1 text-gray-900">{{ hoveredSlotLabel }} - {{ hoveredVendor.shop_name }}</h4>
        <p class="text-xs text-gray-500 mb-2">ID: {{ hoveredVendor.vendorID }}</p>
        <div v-if="hoveredVendor.badges.length > 0" class="flex flex-wrap gap-2">
          <span
            v-for="badge in hoveredVendor.badges"
            :key="badge"
            class="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full border border-blue-200"
          >
            {{ badge }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import type { Vendor, AssignedVendor, VendorStore } from '../types/api';

const emit = defineEmits<{
  vendorAssigned: [vendorID: number, cellKey: string];
  vendorRemoved: [cellKey: string];
}>();

const props = defineProps<{
  vendorStore: VendorStore;
  layoutAssignments?: Map<string, AssignedVendor>;
  onVendorAssigned?: (vendorID: number, cellKey: string) => void;
}>();

const gridConfig = {
  colors: {
    "A": "#44B3E1",
    "B": "#F1A983", 
    "C": "#00FF00",
    "D": "#FFFF00",
    "E": "#33CCCC",
    "H": "#D86DCD",
    "Car": "#FFC000",
    "GoKart": "#FFB6C1",
    "Parking": "#E6E6FA"
  },
  cells: [
    ...Array.from({length: 16}, (_, i) => ({
      row: 2, col: 28 + i, text: `A${i + 1}`, color: "A"
    })),
    ...Array.from({length: 16}, (_, i) => ({
      row: 6, col: 28 + i, text: `A${i + 17}`, color: "A"
    })),
    ...Array.from({length: 17}, (_, i) => ({
      row: 2, col: 6 + i, text: `B${i + 1}`, color: "B"
    })),
    ...Array.from({length: 16}, (_, i) => ({
      row: 6, col: 6 + i, text: `B${i + 18}`, color: "B"
    })),
    { row: 3, col: 3, text: "B34", color: "B" },
    ...Array.from({length: 16}, (_, i) => ({
      row: 21, col: 6 + i, text: `C${i + 1}`, color: "C"
    })),
    ...Array.from({length: 16}, (_, i) => ({
      row: 16, col: 6 + i, text: `D${i + 1}`, color: "D"
    })),
    { row: 6, col: 26, text: "E1", color: "E" },
    { row: 7, col: 26, text: "E2", color: "E" },
    { row: 8, col: 26, text: "E3", color: "E" },
    { row: 9, col: 26, text: "E4", color: "E" },
    { row: 6, col: 24, text: "E5", color: "E" },
    { row: 7, col: 24, text: "E6", color: "E" },
    { row: 8, col: 24, text: "E7", color: "E" },
    { row: 9, col: 24, text: "E8", color: "E" },
    ...Array.from({length: 18}, (_, i) => ({
      row: 5 + i, col: 2, text: `E${i + 9}`, color: "E"
    })),
    { row: 4, col: 5, text: "H20", color: "H" },
    { row: 4, col: 6, text: "H20", color: "H" },
    { row: 4, col: 7, text: "H19", color: "H" },
    { row: 4, col: 8, text: "H19", color: "H" },
    { row: 4, col: 9, text: "H18", color: "H" },
    { row: 4, col: 10, text: "H18", color: "H" },
    { row: 4, col: 11, text: "H17", color: "H" },
    { row: 4, col: 12, text: "H17", color: "H" },
    { row: 4, col: 13, text: "H16", color: "H" },
    { row: 4, col: 14, text: "H16", color: "H" },
    { row: 4, col: 15, text: "H15", color: "H" },
    { row: 4, col: 16, text: "H15", color: "H" },
    { row: 4, col: 17, text: "H14", color: "H" },
    { row: 4, col: 18, text: "H14", color: "H" },
    { row: 4, col: 19, text: "H13", color: "H" },
    { row: 4, col: 20, text: "H13", color: "H" },
    { row: 4, col: 21, text: "H12", color: "H" },
    { row: 4, col: 22, text: "H12", color: "H" },
    { row: 4, col: 23, text: "H11", color: "H" },
    { row: 4, col: 24, text: "H11", color: "H" },
    { row: 4, col: 26, text: "H10", color: "H" },
    { row: 4, col: 27, text: "H10", color: "H" },
    { row: 4, col: 28, text: "H9", color: "H" },
    { row: 4, col: 29, text: "H9", color: "H" },
    { row: 4, col: 30, text: "H8", color: "H" },
    { row: 4, col: 31, text: "H8", color: "H" },
    { row: 4, col: 32, text: "H7", color: "H" },
    { row: 4, col: 33, text: "H7", color: "H" },
    { row: 4, col: 34, text: "H6", color: "H" },
    { row: 4, col: 35, text: "H6", color: "H" },
    { row: 4, col: 36, text: "H5", color: "H" },
    { row: 4, col: 37, text: "H5", color: "H" },
    { row: 4, col: 38, text: "H4", color: "H" },
    { row: 4, col: 39, text: "H4", color: "H" },
    { row: 4, col: 40, text: "H3", color: "H" },
    { row: 4, col: 41, text: "H3", color: "H" },
    { row: 4, col: 42, text: "H2", color: "H" },
    { row: 4, col: 43, text: "H2", color: "H" },
    { row: 4, col: 44, text: "H1", color: "H" },
    { row: 4, col: 45, text: "H1", color: "H" },
    { row: 18, col: 4, text: "H21", color: "H" },
    { row: 18, col: 5, text: "H21", color: "H" },
    { row: 18, col: 6, text: "H22", color: "H" },
    { row: 18, col: 7, text: "H22", color: "H" },
    { row: 18, col: 8, text: "H23", color: "H" },
    { row: 18, col: 9, text: "H23", color: "H" },
    { row: 18, col: 10, text: "H24", color: "H" },
    { row: 18, col: 11, text: "H24", color: "H" },
    { row: 18, col: 12, text: "H25", color: "H" },
    { row: 18, col: 13, text: "H25", color: "H" },
    { row: 18, col: 14, text: "H26", color: "H" },
    { row: 18, col: 15, text: "H26", color: "H" },
    { row: 18, col: 16, text: "H27", color: "H" },
    { row: 18, col: 17, text: "H27", color: "H" },
    { row: 18, col: 18, text: "H28", color: "H" },
    { row: 18, col: 19, text: "H28", color: "H" },
    { row: 18, col: 20, text: "H29", color: "H" },
    { row: 18, col: 21, text: "H29", color: "H" },
    { row: 18, col: 22, text: "H30", color: "H" },
    { row: 18, col: 23, text: "H30", color: "H" },
    { row: 23, col: 4, text: "H31", color: "H" },
    { row: 23, col: 5, text: "H31", color: "H" },
    { row: 23, col: 6, text: "H32", color: "H" },
    { row: 23, col: 7, text: "H32", color: "H" },
    { row: 23, col: 8, text: "H33", color: "H" },
    { row: 23, col: 9, text: "H33", color: "H" },
    { row: 23, col: 10, text: "H34", color: "H" },
    { row: 23, col: 11, text: "H34", color: "H" },
    { row: 23, col: 12, text: "H35", color: "H" },
    { row: 23, col: 13, text: "H35", color: "H" },
    { row: 23, col: 14, text: "H36", color: "H" },
    { row: 23, col: 15, text: "H36", color: "H" },
    { row: 23, col: 16, text: "H37", color: "H" },
    { row: 23, col: 17, text: "H37", color: "H" },
    { row: 23, col: 18, text: "H38", color: "H" },
    { row: 23, col: 19, text: "H38", color: "H" },
    { row: 23, col: 20, text: "H39", color: "H" },
    { row: 23, col: 21, text: "H39", color: "H" },
    { row: 23, col: 22, text: "H40", color: "H" },
    { row: 23, col: 23, text: "H40", color: "H" },
    { row: 20, col: 5, text: "Car1", color: "Car" },
    { row: 20, col: 6, text: "Car1", color: "Car" },
    { row: 20, col: 7, text: "Car2", color: "Car" },
    { row: 20, col: 8, text: "Car2", color: "Car" },
    { row: 20, col: 9, text: "Car3", color: "Car" },
    { row: 20, col: 10, text: "Car3", color: "Car" },
    { row: 20, col: 11, text: "Car4", color: "Car" },
    { row: 20, col: 12, text: "Car4", color: "Car" },
    { row: 20, col: 13, text: "Car5", color: "Car" },
    { row: 20, col: 14, text: "Car5", color: "Car" },
    { row: 20, col: 15, text: "Car6", color: "Car" },
    { row: 20, col: 16, text: "Car6", color: "Car" },
    { row: 20, col: 17, text: "Car7", color: "Car" },
    { row: 20, col: 18, text: "Car7", color: "Car" },
    { row: 20, col: 19, text: "Car8", color: "Car" },
    { row: 20, col: 20, text: "Car8", color: "Car" },
    { row: 20, col: 21, text: "Car9", color: "Car" },
    { row: 20, col: 22, text: "Car9", color: "Car" },
    { row: 23, col: 2, text: "Car10", color: "Car" },
    ...Array.from({length: 7}, (_, rowOffset) => 
      Array.from({length: 16}, (_, colOffset) => ({
        row: 8 + rowOffset,
        col: 6 + colOffset,
        text: "Go Kart",
        color: "GoKart"
      }))
    ).flat(),
    ...Array.from({length: 16}, (_, rowOffset) => 
      Array.from({length: 16}, (_, colOffset) => ({
        row: 8 + rowOffset,
        col: 28 + colOffset,
        text: "Parking Zone",
        color: "Parking"
      }))
    ).flat()
  ]
};

const visibleCells = ref([]);
const mergedAreas = ref([]);
const assignedVendors = ref<Map<string, AssignedVendor>>(new Map());
const hoveredVendor = ref<Vendor | null>(null);
const hoveredCellKey = ref<string | null>(null);
const hoveredSlotLabel = ref<string | null>(null);
const tooltipPosition = ref<{x: number, y: number} | null>(null);
const isTooltipHovered = ref(false);
const hideTooltipTimeout = ref<number | null>(null);

// Computed properties for occupation status to reduce repeated calculations
const cellOccupationStatus = computed(() => {
  const status: Record<string, boolean> = {};
  assignedVendors.value.forEach((assignment, cellKey) => {
    status[cellKey] = true;
  });
  return status;
});

const areaOccupationStatus = computed(() => {
  const status: Record<string, boolean> = {};
  mergedAreas.value.forEach(area => {
    const areaKey = getAreaKey(area);
    status[areaKey] = assignedVendors.value.has(areaKey);
  });
  return status;
});

onMounted(() => {
  initializeGrid();
});

// Watch for layout assignments changes from parent
watch(() => props.layoutAssignments, (newAssignments) => {
  console.log('GridVisualization: Watching layoutAssignments change');
  
  if (newAssignments && newAssignments.size > 0) {
    console.log('GridVisualization received layout assignments:', newAssignments.size, 'assignments');
    console.log('Assignment keys:', Array.from(newAssignments.keys()).slice(0, 10), '...');
    
    // Create a new Map to ensure reactivity
    assignedVendors.value = new Map(newAssignments);
    
    console.log('assignedVendors updated, size:', assignedVendors.value.size);
  } else {
    console.log('No layout assignments received or empty, clearing assignments');
    assignedVendors.value.clear();
  }
}, { immediate: true, deep: true });

function initializeGrid() {
  const textGroups = new Map();
  gridConfig.cells.forEach(cell => {
    if (!textGroups.has(cell.text)) {
      textGroups.set(cell.text, []);
    }
    textGroups.get(cell.text).push(cell);
  });

  const mergedCellPositions = new Set();
  const mergedAreasData = [];

  textGroups.forEach((cellsWithSameText, text) => {
    if (cellsWithSameText.length > 1) {
      const areas = findMergeableAreas(cellsWithSameText);
      
      areas.forEach(area => {
        mergedAreasData.push({
          ...area,
          text,
          color: gridConfig.colors[cellsWithSameText[0].color],
          showCoordinates: false
        });

        area.cells.forEach(cell => {
          mergedCellPositions.add(`${cell.row}-${cell.col}`);
        });
      });
    }
  });

  const cells = gridConfig.cells
    .filter(cell => !mergedCellPositions.has(`${cell.row}-${cell.col}`))
    .map(cell => ({
      ...cell,
      color: gridConfig.colors[cell.color],
      showCoordinates: false
    }));

  visibleCells.value = cells;
  mergedAreas.value = mergedAreasData;
}

function findMergeableAreas(cells) {
  const mergedAreas = [];
  const processed = new Set();
  
  cells.forEach(cell => {
    if (processed.has(`${cell.row}-${cell.col}`)) return;
    
    const area = expandArea(cell, cells, processed);
    if (area.cells.length > 1) {
      mergedAreas.push(area);
    }
  });
  
  return mergedAreas;
}

function expandArea(startCell, allCells, processed) {
  const cellSet = new Set(allCells.map(c => `${c.row}-${c.col}`));
  const area = {
    minRow: startCell.row,
    maxRow: startCell.row,
    minCol: startCell.col,
    maxCol: startCell.col,
    cells: []
  };
  
  const queue = [startCell];
  const visited = new Set();
  
  while (queue.length > 0) {
    const current = queue.shift();
    const key = `${current.row}-${current.col}`;
    
    if (visited.has(key)) continue;
    if (!cellSet.has(key)) continue;
    
    visited.add(key);
    processed.add(key);
    area.cells.push(current);
    
    area.minRow = Math.min(area.minRow, current.row);
    area.maxRow = Math.max(area.maxRow, current.row);
    area.minCol = Math.min(area.minCol, current.col);
    area.maxCol = Math.max(area.maxCol, current.col);
    
    const adjacent = [
      {row: current.row - 1, col: current.col},
      {row: current.row + 1, col: current.col},
      {row: current.row, col: current.col - 1},
      {row: current.row, col: current.col + 1}
    ];
    
    adjacent.forEach(adj => {
      const adjKey = `${adj.row}-${adj.col}`;
      if (cellSet.has(adjKey) && !visited.has(adjKey)) {
        queue.push(adj);
      }
    });
  }
  
  return area;
}

function getCellKey(row: number, col: number): string {
  return `${row}-${col}`;
}

function getAreaKey(area: any): string {
  return `${area.minRow}-${area.minCol}-${area.maxRow}-${area.maxCol}`;
}

function isNonDroppable(text: string): boolean {
  return text === 'Go Kart' || text === 'Parking Zone';
}

function getOriginalCellText(row: number, col: number): string {
  const cell = visibleCells.value.find(c => c.row === row && c.col === col);
  if (cell) {
    return cell.text;
  }
  
  // Check if it's part of a merged area
  const originalCell = gridConfig.cells.find(c => c.row === row && c.col === col);
  return originalCell ? originalCell.text : '';
}

function getOriginalAreaText(area: any): string {
  return area.text;
}

function getCellDisplayText(row: number, col: number, originalText: string): string {
  const cellKey = getCellKey(row, col);
  const assigned = assignedVendors.value.get(cellKey);
  if (assigned) {
    const vendor = props.vendorStore[assigned.vendorID];
    return vendor ? vendor.shop_name : `Vendor ${assigned.vendorID}`;
  }
  return originalText;
}

function getAreaDisplayText(area: any): string {
  const areaKey = getAreaKey(area);
  const assigned = assignedVendors.value.get(areaKey);
  if (assigned) {
    const vendor = props.vendorStore[assigned.vendorID];
    return vendor ? vendor.shop_name : `Vendor ${assigned.vendorID}`;
  }
  return area.text;
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy';
  }
}

function handleDrop(event: DragEvent, row: number, col: number) {
  event.preventDefault();
  
  // Find the cell to check if it's droppable
  const cell = visibleCells.value.find(c => c.row === row && c.col === col);
  if (!cell || isNonDroppable(cell.text) || cellOccupationStatus.value[getCellKey(row, col)]) {
    return;
  }

  try {
    const dragData = event.dataTransfer?.getData('application/json');
    if (dragData) {
      const { vendorID } = JSON.parse(dragData);
      const cellKey = getCellKey(row, col);
      
      assignedVendors.value.set(cellKey, {
        vendorID,
        cellKey,
        assignedAt: new Date()
      });

      if (props.onVendorAssigned) {
        props.onVendorAssigned(vendorID, cellKey);
      }
      
      // Emit event to parent
      emit('vendorAssigned', vendorID, cellKey);
    }
  } catch (error) {
    console.error('Error parsing vendor data:', error);
  }
}

function handleAreaDrop(event: DragEvent, area: any) {
  event.preventDefault();
  
  if (isNonDroppable(area.text) || areaOccupationStatus.value[getAreaKey(area)]) {
    return;
  }

  try {
    const dragData = event.dataTransfer?.getData('application/json');
    if (dragData) {
      const { vendorID } = JSON.parse(dragData);
      const areaKey = getAreaKey(area);
      
      assignedVendors.value.set(areaKey, {
        vendorID,
        cellKey: areaKey,
        assignedAt: new Date()
      });

      if (props.onVendorAssigned) {
        props.onVendorAssigned(vendorID, areaKey);
      }
      
      // Emit event to parent
      emit('vendorAssigned', vendorID, areaKey);
    }
  } catch (error) {
    console.error('Error parsing vendor data:', error);
  }
}

function handleMouseEnter(event: MouseEvent, row: number, col: number) {
  const cellKey = getCellKey(row, col);
  const assigned = assignedVendors.value.get(cellKey);
  
  if (assigned) {
    const vendor = props.vendorStore[assigned.vendorID];
    if (vendor) {
      // Clear any pending hide timeout
      if (hideTooltipTimeout.value) {
        clearTimeout(hideTooltipTimeout.value);
        hideTooltipTimeout.value = null;
      }
      
      hoveredVendor.value = vendor;
      hoveredCellKey.value = cellKey;
      hoveredSlotLabel.value = getOriginalCellText(row, col);
      tooltipPosition.value = {
        x: event.clientX + 10,
        y: event.clientY - 10
      };
    }
  }
}

function handleAreaMouseEnter(event: MouseEvent, area: any) {
  const areaKey = getAreaKey(area);
  const assigned = assignedVendors.value.get(areaKey);
  
  if (assigned) {
    const vendor = props.vendorStore[assigned.vendorID];
    if (vendor) {
      // Clear any pending hide timeout
      if (hideTooltipTimeout.value) {
        clearTimeout(hideTooltipTimeout.value);
        hideTooltipTimeout.value = null;
      }
      
      hoveredVendor.value = vendor;
      hoveredCellKey.value = areaKey;
      hoveredSlotLabel.value = getOriginalAreaText(area);
      tooltipPosition.value = {
        x: event.clientX + 10,
        y: event.clientY - 10
      };
    }
  }
}

function handleMouseLeave(event: MouseEvent) {
  // Only hide tooltip if mouse is not moving to the tooltip
  hideTooltipTimeout.value = setTimeout(() => {
    if (!isTooltipHovered.value) {
      hoveredVendor.value = null;
      hoveredCellKey.value = null;
      hoveredSlotLabel.value = null;
      tooltipPosition.value = null;
    }
  }, 100);
}

function handleTooltipMouseEnter() {
  isTooltipHovered.value = true;
  // Clear any pending hide timeout
  if (hideTooltipTimeout.value) {
    clearTimeout(hideTooltipTimeout.value);
    hideTooltipTimeout.value = null;
  }
}

function handleTooltipMouseLeave() {
  isTooltipHovered.value = false;
  // Hide tooltip immediately when leaving tooltip area
  hoveredVendor.value = null;
  hoveredCellKey.value = null;
  hoveredSlotLabel.value = null;
  tooltipPosition.value = null;
}

function removeVendor() {
  if (hoveredCellKey.value) {
    assignedVendors.value.delete(hoveredCellKey.value);
    
    // Emit removal event to parent
    emit('vendorRemoved', hoveredCellKey.value);
    
    hoveredVendor.value = null;
    hoveredCellKey.value = null;
    hoveredSlotLabel.value = null;
    tooltipPosition.value = null;
    isTooltipHovered.value = false;
  }
}
</script>

<style scoped>
.grid-container {
 display: inline-block;
 min-width: 1426px;
 min-height: 720px;
}

.grid {
 display: grid;
 grid-template-columns: repeat(46, 30px);
 grid-template-rows: repeat(24, 30px);
 gap: 1px;
 height: 720px;
 width: 1426px;
}

.grid-cell {
 background-color: white;
 border: 3px solid #e0e0e0;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 10px;
 color: #666;
 box-sizing: border-box;
 position: relative;
 transition: all 0.2s ease;
 overflow: hidden;
}

.grid-cell:not(.merged-cell) {
 width: 30px;
 height: 30px;
}

.cell-text {
 font-size: 8px;
 font-weight: bold;
 color: #333;
 text-align: center;
 line-height: 1;
 overflow: hidden;
 white-space: nowrap;
 text-overflow: ellipsis;
 max-width: 26px;
}

.merged-cell {
 z-index: 10;
 box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
 width: auto !important;
 height: auto !important;
}

.merged-text {
 font-size: 8px;
 font-weight: bold;
 color: #333;
 text-align: center;
 overflow: visible;
 white-space: nowrap;
 padding: 4px;
}

.cell-number {
 position: absolute;
 bottom: 1px;
 right: 1px;
 font-size: 6px;
 background: rgba(255, 255, 255, 0.95);
 padding: 1px 2px;
 border-radius: 2px;
 font-weight: 500;
 z-index: 20;
 color: #555;
 border: 1px solid rgba(0, 0, 0, 0.1);
 pointer-events: none;
}

.grid-cell:hover:not(.non-interactive):not(.occupied) {
 background-color: #e3f2fd;
 border-color: #2196f3;
 transform: scale(1.05);
 z-index: 15;
 box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.non-interactive {
 pointer-events: none;
 cursor: default;
}

.occupied {
 cursor: pointer;
}

.drop-zone {
 cursor: copy;
}

.drop-zone:hover {
 background-color: #e8f5e8 !important;
 border-color: #4caf50 !important;
}

.vendor-tooltip {
 position: fixed;
 z-index: 1000;
}

.vendor-tooltip .bg-white {
 pointer-events: auto;
}
</style>