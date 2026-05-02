// src/services/layoutService.ts
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

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

export class LayoutService {
  static async getAllLayouts(): Promise<Layout[]> {
    try {
      const response = await fetch(`${BASE_URL}/show_all_layouts`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Layout fetch error:', error);
      throw error;
    }
  }

  static async updateLayout(id: number, name: string, data: any): Promise<void> {
    try {
      const response = await fetch(`${BASE_URL}/update_layout/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name,
          data: data
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      console.log('Layout updated successfully');
    } catch (error) {
      console.error('Update layout error:', error);
      throw error;
    }
  }

  static async insertLayout(name: string, data: any): Promise<number> {
    try {
      const response = await fetch(`${BASE_URL}/insert_layout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name,
          data: data
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Layout inserted successfully, ID:', result.id);
      return result.id;
    } catch (error) {
      console.error('Insert layout error:', error);
      throw error;
    }
  }
  static async deleteLayout(id: number): Promise<void> {
    try {
      const response = await fetch(`${BASE_URL}/delete_layout/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      console.log('Layout deleted successfully');
    } catch (error) {
      console.error('Delete layout error:', error);
      throw error;
    }
  }
  static async sendNotification(id: number): Promise<any> {
    try {
      const response = await fetch(`${BASE_URL}/send_notification/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Notification sent successfully:', result);
      return result;
    } catch (error) {
      console.error('Send notification error:', error);
      throw error;
    }
  }
}