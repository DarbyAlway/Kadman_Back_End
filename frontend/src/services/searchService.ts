// src/services/searchService.ts
import type { Vendor } from '../types/api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

export class SearchService {
  static async search(params: { q?: string }): Promise<Vendor[]> {
    try {
      const url = new URL(`${BASE_URL}/search`);
      // Always add the q parameter, even if empty
      url.searchParams.append('q', params.q || '');
      
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Return the array directly since your API returns an array, not an object with results
      return await response.json();
    } catch (error) {
      console.error('Search error:', error);
      throw error;
    }
  }
}