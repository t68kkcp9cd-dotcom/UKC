import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { AuthResponse, User, InventoryItem, Recipe, MealPlan, ShoppingList } from '../types';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle token refresh or logout
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post('/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    household_id?: string;
  }): Promise<AuthResponse> {
    const response = await this.client.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await this.client.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  // Inventory endpoints
  async getInventoryItems(params?: {
    location?: string;
    category?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ data: InventoryItem[]; total: number }> {
    const response = await this.client.get('/inventory', { params });
    return response.data;
  }

  async getInventoryItem(id: string): Promise<InventoryItem> {
    const response = await this.client.get(`/inventory/${id}`);
    return response.data;
  }

  async createInventoryItem(data: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await this.client.post('/inventory', data);
    return response.data;
  }

  async updateInventoryItem(id: string, data: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await this.client.put(`/inventory/${id}`, data);
    return response.data;
  }

  async deleteInventoryItem(id: string): Promise<void> {
    await this.client.delete(`/inventory/${id}`);
  }

  async scanBarcode(barcode: string, location?: string) {
    const response = await this.client.post('/inventory/scan-barcode', {
      barcode,
      location,
    });
    return response.data;
  }

  async getWasteForecast(days_ahead: number = 7): Promise<any> {
    const response = await this.client.get('/inventory/forecast-waste', {
      params: { days_ahead },
    });
    return response.data;
  }

  // Recipe endpoints
  async getRecipes(params?: {
    search?: string;
    cuisine?: string;
    difficulty?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ data: Recipe[]; total: number }> {
    const response = await this.client.get('/recipes', { params });
    return response.data;
  }

  async getRecipe(id: string): Promise<Recipe> {
    const response = await this.client.get(`/recipes/${id}`);
    return response.data;
  }

  async createRecipe(data: Partial<Recipe>): Promise<Recipe> {
    const response = await this.client.post('/recipes', data);
    return response.data;
  }

  async updateRecipe(id: string, data: Partial<Recipe>): Promise<Recipe> {
    const response = await this.client.put(`/recipes/${id}`, data);
    return response.data;
  }

  async deleteRecipe(id: string): Promise<void> {
    await this.client.delete(`/recipes/${id}`);
  }

  async importRecipeFromURL(url: string): Promise<Recipe> {
    const response = await this.client.post('/recipes/import-url', { url });
    return response.data;
  }

  // Meal Planning endpoints
  async getMealPlans(params?: {
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ data: MealPlan[]; total: number }> {
    const response = await this.client.get('/meal-plans', { params });
    return response.data;
  }

  async getMealPlan(id: string): Promise<MealPlan> {
    const response = await this.client.get(`/meal-plans/${id}`);
    return response.data;
  }

  async createMealPlan(data: Partial<MealPlan>): Promise<MealPlan> {
    const response = await this.client.post('/meal-plans', data);
    return response.data;
  }

  async generateMealPlan(data: {
    start_date: string;
    end_date: string;
    dietary_preferences?: string[];
    budget_range?: [number, number];
  }): Promise<MealPlan> {
    const response = await this.client.post('/meal-plans/generate', data);
    return response.data;
  }

  // Shopping List endpoints
  async getShoppingLists(params?: {
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<{ data: ShoppingList[]; total: number }> {
    const response = await this.client.get('/shopping-lists', { params });
    return response.data;
  }

  async getShoppingList(id: string): Promise<ShoppingList> {
    const response = await this.client.get(`/shopping-lists/${id}`);
    return response.data;
  }

  async createShoppingList(data: {
    list_name: string;
    store_id?: string;
  }): Promise<ShoppingList> {
    const response = await this.client.post('/shopping-lists', data);
    return response.data;
  }

  async generateShoppingListFromPlan(plan_id: string): Promise<ShoppingList> {
    const response = await this.client.post(`/shopping-lists/generate-from-plan`, {
      plan_id,
    });
    return response.data;
  }

  // AI endpoints
  async chatWithAI(message: string, context?: string): Promise<any> {
    const response = await this.client.post('/ai/chat', {
      message,
      context: context || 'general',
    });
    return response.data;
  }

  async getRecipeSuggestions(params?: {
    available_ingredients?: string[];
    dietary_restrictions?: string[];
    cuisine_type?: string;
  }): Promise<any> {
    const response = await this.client.get('/ai/suggest-recipes', { params });
    return response.data;
  }

  async adaptRecipe(
    recipe_id: string,
    adaptations: {
      servings?: number;
      dietary_restrictions?: string[];
      available_ingredients?: string[];
    }
  ): Promise<any> {
    const response = await this.client.post('/ai/adapt-recipe', {
      recipe_id,
      adaptations,
    });
    return response.data;
  }

  // Utility methods
  async uploadFile(file: File, type: 'recipe_image' | 'profile_avatar'): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await this.client.post('/uploads', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.url;
  }

  // Error handling
  handleError(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error.response?.data?.message) {
      return error.response.data.message;
    } else if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;