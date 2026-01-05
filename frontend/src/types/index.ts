export interface User {
  id: string;
  username: string;
  email: string;
  household_id?: string;
  is_active: boolean;
  is_premium: boolean;
  created_at: string;
  updated_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  id: string;
  user_id: string;
  display_name?: string;
  avatar_url?: string;
  dietary_tags: string[];
  allergens: string[];
  preferences: Record<string, any>;
  feature_toggles: Record<string, boolean>;
  created_at: string;
  updated_at: string;
}

export interface InventoryItem {
  id: string;
  household_id: string;
  barcode?: string;
  name: string;
  category?: string;
  quantity: number;
  unit: string;
  expiration_date?: string;
  purchase_date?: string;
  purchase_price?: number;
  location: string;
  nutrition_data?: Record<string, any>;
  price_history: any[];
  added_by: string;
  created_at: string;
  updated_at: string;
  days_until_expiration?: number;
}

export interface Recipe {
  id: string;
  title: string;
  description?: string;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  cuisine_type?: string;
  dietary_tags: string[];
  nutrition_estimates?: Record<string, any>;
  cost_estimate?: number;
  carbon_footprint?: number;
  source_url?: string;
  imported_from?: string;
  created_by: string;
  is_public: boolean;
  average_rating?: number;
  total_ratings: number;
  ingredients: RecipeIngredient[];
  steps: RecipeStep[];
  reviews: RecipeReview[];
  created_at: string;
  updated_at: string;
}

export interface RecipeIngredient {
  id: string;
  recipe_id: string;
  ingredient_name: string;
  quantity?: number;
  unit?: string;
  notes?: string;
  order_index: number;
}

export interface RecipeStep {
  id: string;
  recipe_id: string;
  step_number: number;
  instruction: string;
  timer_seconds?: number;
  image_url?: string;
}

export interface RecipeReview {
  id: string;
  recipe_id: string;
  user_id: string;
  rating: number;
  review_text?: string;
  created_at: string;
}

export interface MealPlan {
  id: string;
  household_id: string;
  plan_name: string;
  start_date: string;
  end_date: string;
  generated_by_ai: boolean;
  created_by: string;
  entries: MealPlanEntry[];
  created_at: string;
  updated_at: string;
}

export interface MealPlanEntry {
  id: string;
  plan_id: string;
  meal_date: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  recipe_id?: string;
  recipe?: Recipe;
  servings_planned: number;
  prep_notes?: string;
}

export interface ShoppingList {
  id: string;
  household_id: string;
  list_name: string;
  store_id?: string;
  store?: Store;
  is_active: boolean;
  created_by: string;
  items: ShoppingListItem[];
  created_at: string;
  updated_at: string;
}

export interface ShoppingListItem {
  id: string;
  list_id: string;
  item_name: string;
  quantity?: number;
  unit?: string;
  category?: string;
  estimated_price?: number;
  best_price_found?: number;
  best_store_id?: string;
  is_checked: boolean;
  added_from_inventory: boolean;
  order_index: number;
}

export interface Store {
  id: string;
  name: string;
  chain?: string;
  address?: string;
  zip_code?: string;
  latitude?: number;
  longitude?: number;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface FilterParams {
  search?: string;
  category?: string;
  location?: string;
  expires_before?: string;
  expires_after?: string;
}

export interface ApiResponse<T> {
  data: T;
  total?: number;
  skip?: number;
  limit?: number;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface WasteForecast {
  household_id: string;
  forecast_period_days: number;
  total_items_at_risk: number;
  estimated_waste_value: number;
  items_at_risk: any[];
  recommendations: string[];
  confidence_score: number;
}

export interface BarcodeLookupResponse {
  barcode: string;
  product_name: string;
  brand?: string;
  category?: string;
  image_url?: string;
  nutrition_data: Record<string, any>;
  allergens: string[];
  ingredients: string[];
  source: string;
}