import Foundation
import SwiftUI

struct User: Codable, Identifiable, Equatable {
    let id: UUID
    var email: String
    var fullName: String
    var avatarUrl: String?
    var isActive: Bool
    var isPremium: Bool
    var preferences: [String: String]?
    var createdAt: Date
    var updatedAt: Date
    var households: [Household]?
    
    static func == (lhs: User, rhs: User) -> Bool {
        lhs.id == rhs.id
    }
}

struct Household: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var ownerId: UUID
    var invitationCode: String
    var settings: [String: String]?
    var createdAt: Date
    var updatedAt: Date
    var members: [User]?
    
    static func == (lhs: Household, rhs: Household) -> Bool {
        lhs.id == rhs.id
    }
}

struct InventoryItem: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var category: String
    var quantity: Decimal
    var unit: String
    var location: String
    var expiresAt: Date?
    var openedAt: Date?
    var opened: Bool
    var barcode: String?
    var price: Decimal?
    var status: String
    var imageUrl: String?
    var notes: String?
    var nutritionalInfo: [String: String]?
    var userId: UUID
    var householdId: UUID
    var syncStatus: String
    var createdAt: Date
    var updatedAt: Date
    
    var isExpiringSoon: Bool {
        guard let expiresAt = expiresAt else { return false }
        let daysUntilExpiry = Calendar.current.dateComponents([.day], from: Date(), to: expiresAt).day ?? 0
        return daysUntilExpiry <= 3 && daysUntilExpiry >= 0
    }
    
    var isExpired: Bool {
        guard let expiresAt = expiresAt else { return false }
        return expiresAt < Date()
    }
    
    static func == (lhs: InventoryItem, rhs: InventoryItem) -> Bool {
        lhs.id == rhs.id
    }
}

struct Ingredient: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var quantity: String
    var unit: String
    var notes: String?
    var isOptional: Bool
    
    static func == (lhs: Ingredient, rhs: Ingredient) -> Bool {
        lhs.id == rhs.id
    }
}

struct Recipe: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var description: String?
    var ingredients: [Ingredient]
    var instructions: [String]
    var cookTime: Int
    var prepTime: Int
    var totalTime: Int
    var servings: Int
    var difficulty: String
    var cuisine: String?
    var tags: [String]?
    var nutrition: [String: String]?
    var imageUrl: String?
    var notes: String?
    var source: String?
    var isPublic: Bool
    var rating: Decimal?
    var userId: UUID
    var householdId: UUID
    var syncStatus: String
    var createdAt: Date
    var updatedAt: Date
    var reviews: [RecipeReview]?
    
    static func == (lhs: Recipe, rhs: Recipe) -> Bool {
        lhs.id == rhs.id
    }
}

struct RecipeReview: Codable, Identifiable, Equatable {
    let id: UUID
    var rating: Decimal
    var comment: String?
    var userId: UUID
    var createdAt: Date
    var updatedAt: Date
    
    static func == (lhs: RecipeReview, rhs: RecipeReview) -> Bool {
        lhs.id == rhs.id
    }
}

struct MealPlan: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var startDate: Date
    var endDate: Date
    var userId: UUID
    var householdId: UUID
    var syncStatus: String
    var createdAt: Date
    var updatedAt: Date
    var entries: [MealPlanEntry]?
    
    static func == (lhs: MealPlan, rhs: MealPlan) -> Bool {
        lhs.id == rhs.id
    }
}

struct MealPlanEntry: Codable, Identifiable, Equatable {
    let id: UUID
    var date: Date
    var mealType: String
    var servings: Int
    var notes: String?
    var recipeId: UUID?
    var mealPlanId: UUID
    var syncStatus: String
    var createdAt: Date
    var updatedAt: Date
    var recipe: Recipe?
    
    static func == (lhs: MealPlanEntry, rhs: MealPlanEntry) -> Bool {
        lhs.id == rhs.id
    }
}

struct ShoppingList: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var userId: UUID
    var householdId: UUID
    var syncStatus: String
    var createdAt: Date
    var updatedAt: Date
    var items: [ShoppingItem]?
    
    static func == (lhs: ShoppingList, rhs: ShoppingList) -> Bool {
        lhs.id == rhs.id
    }
}

struct ShoppingItem: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var category: String
    var quantity: Decimal
    var unit: String
    var completed: Bool
    var price: Decimal?
    var notes: String?
    var userId: UUID
    var shoppingListId: UUID
    var syncStatus: String
    var createdAt: Date
    var updatedAt: Date
    
    static func == (lhs: ShoppingItem, rhs: ShoppingItem) -> Bool {
        lhs.id == rhs.id
    }
}

struct Achievement: Codable, Identifiable, Equatable {
    let id: UUID
    var name: String
    var description: String
    var icon: String
    var category: String
    var points: Int
    var requirement: String
    var unlockedAt: Date?
    var userId: UUID
    
    static func == (lhs: Achievement, rhs: Achievement) -> Bool {
        lhs.id == rhs.id
    }
}

struct AuthToken: Codable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let expiresIn: Int
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable {
    let email: String
    let password: String
    let fullName: String
}

struct RefreshTokenRequest: Codable {
    let refreshToken: String
}

struct PaginatedResponse<T: Codable>: Codable {
    let items: [T]
    let total: Int
    let page: Int
    let size: Int
    let pages: Int
}

struct APIError: Codable, LocalizedError {
    let detail: String
    let code: String?
    
    var errorDescription: String? {
        return detail
    }
}

enum SyncStatus: String, Codable {
    case synced = "synced"
    case created = "created"
    case updated = "updated"
    case deleted = "deleted"
    case error = "error"
}

enum InventoryLocation: String, CaseIterable, Codable {
    case pantry = "Pantry"
    case refrigerator = "Refrigerator"
    case freezer = "Freezer"
    case counter = "Counter"
    case spiceRack = "Spice Rack"
    case wineCellar = "Wine Cellar"
    case other = "Other"
}

enum InventoryCategory: String, CaseIterable, Codable {
    case dairy = "Dairy"
    case meat = "Meat & Seafood"
    case produce = "Produce"
    case grains = "Grains & Cereals"
    case canned = "Canned Goods"
    case frozen = "Frozen Foods"
    case snacks = "Snacks"
    case beverages = "Beverages"
    case condiments = "Condiments"
    case baking = "Baking"
    case spices = "Spices"
    case other = "Other"
}

enum RecipeDifficulty: String, CaseIterable, Codable {
    case easy = "Easy"
    case medium = "Medium"
    case hard = "Hard"
}

enum MealType: String, CaseIterable, Codable {
    case breakfast = "Breakfast"
    case lunch = "Lunch"
    case dinner = "Dinner"
    case snack = "Snack"
    case dessert = "Dessert"
}

enum ShoppingCategory: String, CaseIterable, Codable {
    case produce = "Produce"
    case dairy = "Dairy"
    case meat = "Meat & Seafood"
    case bakery = "Bakery"
    case frozen = "Frozen"
    case pantry = "Pantry"
    case beverages = "Beverages"
    case household = "Household"
    case personal = "Personal Care"
    case other = "Other"
}

extension Decimal {
    var doubleValue: Double {
        return NSDecimalNumber(decimal: self).doubleValue
    }
}

extension Date {
    var isToday: Bool {
        return Calendar.current.isDateInToday(self)
    }
    
    var isTomorrow: Bool {
        return Calendar.current.isDateInTomorrow(self)
    }
    
    var isYesterday: Bool {
        return Calendar.current.isDateInYesterday(self)
    }
    
    func adding(days: Int) -> Date {
        return Calendar.current.date(byAdding: .day, value: days, to: self) ?? self
    }
    
    func startOfWeek() -> Date {
        let calendar = Calendar.current
        let components = calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: self)
        return calendar.date(from: components) ?? self
    }
    
    func endOfWeek() -> Date {
        return Calendar.current.date(byAdding: .day, value: 6, to: startOfWeek()) ?? self
    }
}