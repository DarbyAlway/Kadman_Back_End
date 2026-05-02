// src/types/api.ts
export interface Vendor {
  vendorID: number;
  shop_name: string;
  badges: string[];
  shop_name_syllables: string[];
}

export interface SearchParams {
  q?: string;
}

export interface AssignedVendor {
  vendorID: number; // Store only vendor ID instead of full vendor object
  cellKey: string;
  assignedAt: Date;
}

export interface CellPosition {
  row: number;
  col: number;
}

export interface VendorStore {
  [vendorID: number]: Vendor;
}

export interface Layout {
  id: number;
  name: string;
  data: {
    [key: string]: {
      vendorID: number | null;
      shop_name: string | null;
    };
  };
}