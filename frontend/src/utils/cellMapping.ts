// src/utils/cellMapping.ts
export interface CellMapping {
  semanticKey: string;  // Backend format: "A1", "B1", "Car1", etc.
  gridKey: string;      // Frontend format: "2-28", "6-6", etc.
  row: number;
  col: number;
}

// Create mapping between semantic keys and grid coordinates
export function createCellMappings(): Map<string, CellMapping> {
  const mappings = new Map<string, CellMapping>();
  
  // A section mappings (A1-A32)
  // A1-A16: row 2, cols 28-43
  for (let i = 1; i <= 16; i++) {
    const semanticKey = `A${i}`;
    const row = 2;
    const col = 27 + i; // A1 starts at col 28
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // A17-A32: row 6, cols 28-43
  for (let i = 17; i <= 32; i++) {
    const semanticKey = `A${i}`;
    const row = 6;
    const col = 11 + i; // A17 starts at col 28
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // B section mappings (B1-B34)
  // B1-B17: row 2, cols 6-22
  for (let i = 1; i <= 17; i++) {
    const semanticKey = `B${i}`;
    const row = 2;
    const col = 5 + i; // B1 starts at col 6
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // B18-B33: row 6, cols 6-21
  for (let i = 18; i <= 33; i++) {
    const semanticKey = `B${i}`;
    const row = 6;
    const col = i - 12; // B18 starts at col 6
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // B34: special case at row 3, col 3
  mappings.set('B34', { 
    semanticKey: 'B34', 
    gridKey: '3-3', 
    row: 3, 
    col: 3 
  });
  
  // C section mappings (C1-C16)
  // C1-C16: row 21, cols 6-21
  for (let i = 1; i <= 16; i++) {
    const semanticKey = `C${i}`;
    const row = 21;
    const col = 5 + i; // C1 starts at col 6
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // D section mappings (D1-D16)
  // D1-D16: row 16, cols 6-21
  for (let i = 1; i <= 16; i++) {
    const semanticKey = `D${i}`;
    const row = 16;
    const col = 5 + i; // D1 starts at col 6
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // E section mappings (E1-E26)
  // E1-E4: cols 26, rows 6-9
  for (let i = 1; i <= 4; i++) {
    const semanticKey = `E${i}`;
    const row = 5 + i; // E1 starts at row 6
    const col = 26;
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // E5-E8: cols 24, rows 6-9
  for (let i = 5; i <= 8; i++) {
    const semanticKey = `E${i}`;
    const row = 1 + i; // E5 starts at row 6
    const col = 24;
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // E9-E26: col 2, rows 5-22
  for (let i = 9; i <= 26; i++) {
    const semanticKey = `E${i}`;
    const row = i - 4; // E9 starts at row 5
    const col = 2;
    const gridKey = `${row}-${col}`;
    mappings.set(semanticKey, { semanticKey, gridKey, row, col });
  }
  
  // H section mappings (H1-H40) - these are MERGED cells using area key format
  // H1-H20: row 4, paired columns (merged cells)
  const hRow4Mappings = [
    { num: 20, cols: [5, 6] },   // H20: cols 5-6
    { num: 19, cols: [7, 8] },   // H19: cols 7-8
    { num: 18, cols: [9, 10] },  // H18: cols 9-10
    { num: 17, cols: [11, 12] }, // H17: cols 11-12
    { num: 16, cols: [13, 14] }, // H16: cols 13-14
    { num: 15, cols: [15, 16] }, // H15: cols 15-16
    { num: 14, cols: [17, 18] }, // H14: cols 17-18
    { num: 13, cols: [19, 20] }, // H13: cols 19-20
    { num: 12, cols: [21, 22] }, // H12: cols 21-22
    { num: 11, cols: [23, 24] }, // H11: cols 23-24
    { num: 10, cols: [26, 27] }, // H10: cols 26-27
    { num: 9, cols: [28, 29] },  // H9: cols 28-29
    { num: 8, cols: [30, 31] },  // H8: cols 30-31
    { num: 7, cols: [32, 33] },  // H7: cols 32-33
    { num: 6, cols: [34, 35] },  // H6: cols 34-35
    { num: 5, cols: [36, 37] },  // H5: cols 36-37
    { num: 4, cols: [38, 39] },  // H4: cols 38-39
    { num: 3, cols: [40, 41] },  // H3: cols 40-41
    { num: 2, cols: [42, 43] },  // H2: cols 42-43
    { num: 1, cols: [44, 45] }   // H1: cols 44-45
  ];
  
  hRow4Mappings.forEach(({ num, cols }) => {
    const semanticKey = `H${num}`;
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    const gridKey = `4-${minCol}-4-${maxCol}`; // Area key format: minRow-minCol-maxRow-maxCol
    mappings.set(semanticKey, { 
      semanticKey, 
      gridKey, 
      row: 4, 
      col: minCol 
    });
  });
  
  // H21-H30: row 18, paired columns (merged cells)
  const hRow18Mappings = [
    { num: 21, cols: [4, 5] },   // H21: cols 4-5
    { num: 22, cols: [6, 7] },   // H22: cols 6-7
    { num: 23, cols: [8, 9] },   // H23: cols 8-9
    { num: 24, cols: [10, 11] }, // H24: cols 10-11
    { num: 25, cols: [12, 13] }, // H25: cols 12-13
    { num: 26, cols: [14, 15] }, // H26: cols 14-15
    { num: 27, cols: [16, 17] }, // H27: cols 16-17
    { num: 28, cols: [18, 19] }, // H28: cols 18-19
    { num: 29, cols: [20, 21] }, // H29: cols 20-21
    { num: 30, cols: [22, 23] }  // H30: cols 22-23
  ];
  
  hRow18Mappings.forEach(({ num, cols }) => {
    const semanticKey = `H${num}`;
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    const gridKey = `18-${minCol}-18-${maxCol}`; // Area key format
    mappings.set(semanticKey, { 
      semanticKey, 
      gridKey, 
      row: 18, 
      col: minCol 
    });
  });
  
  // H31-H40: row 23, paired columns (merged cells)
  const hRow23Mappings = [
    { num: 31, cols: [4, 5] },   // H31: cols 4-5
    { num: 32, cols: [6, 7] },   // H32: cols 6-7
    { num: 33, cols: [8, 9] },   // H33: cols 8-9
    { num: 34, cols: [10, 11] }, // H34: cols 10-11
    { num: 35, cols: [12, 13] }, // H35: cols 12-13
    { num: 36, cols: [14, 15] }, // H36: cols 14-15
    { num: 37, cols: [16, 17] }, // H37: cols 16-17
    { num: 38, cols: [18, 19] }, // H38: cols 18-19
    { num: 39, cols: [20, 21] }, // H39: cols 20-21
    { num: 40, cols: [22, 23] }  // H40: cols 22-23
  ];
  
  hRow23Mappings.forEach(({ num, cols }) => {
    const semanticKey = `H${num}`;
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    const gridKey = `23-${minCol}-23-${maxCol}`; // Area key format
    mappings.set(semanticKey, { 
      semanticKey, 
      gridKey, 
      row: 23, 
      col: minCol 
    });
  });
  
  // Car section mappings (Car1-Car9) - these are MERGED cells using area key format
  const carMappings = [
    { num: 1, cols: [5, 6] },   // Car1: cols 5-6
    { num: 2, cols: [7, 8] },   // Car2: cols 7-8
    { num: 3, cols: [9, 10] },  // Car3: cols 9-10
    { num: 4, cols: [11, 12] }, // Car4: cols 11-12
    { num: 5, cols: [13, 14] }, // Car5: cols 13-14
    { num: 6, cols: [15, 16] }, // Car6: cols 15-16
    { num: 7, cols: [17, 18] }, // Car7: cols 17-18
    { num: 8, cols: [19, 20] }, // Car8: cols 19-20
    { num: 9, cols: [21, 22] }  // Car9: cols 21-22
  ];
  
  carMappings.forEach(({ num, cols }) => {
    const semanticKey = `Car${num}`;
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    const gridKey = `20-${minCol}-20-${maxCol}`; // Area key format for merged cells
    mappings.set(semanticKey, { 
      semanticKey, 
      gridKey, 
      row: 20, 
      col: minCol 
    });
  });
  
  // Car10: special case at row 23, col 2
  mappings.set('Car10', { 
    semanticKey: 'Car10', 
    gridKey: '23-2', 
    row: 23, 
    col: 2 
  });
  
  return mappings;
}

// Convert semantic key to grid key
export function semanticToGrid(semanticKey: string): string | null {
  const mappings = createCellMappings();
  const mapping = mappings.get(semanticKey);
  return mapping ? mapping.gridKey : null;
}

// Convert grid key to semantic key
export function gridToSemantic(gridKey: string): string | null {
  const mappings = createCellMappings();
  for (const [semanticKey, mapping] of mappings) {
    if (mapping.gridKey === gridKey) {
      return semanticKey;
    }
  }
  return null;
}

// Get all mappings for debugging
export function getAllMappings(): CellMapping[] {
  const mappings = createCellMappings();
  return Array.from(mappings.values());
}