import Foundation
import CoreData

extension CDUser {
    func toUser() -> User {
        return User(
            id: self.id ?? UUID(),
            email: self.email ?? "",
            fullName: self.fullName ?? "",
            avatarUrl: self.avatarUrl,
            isActive: self.isActive,
            isPremium: self.isPremium,
            preferences: self.preferences as? [String: String],
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date(),
            households: self.households?.compactMap { ($0 as? CDHousehold)?.toHousehold() }
        )
    }
    
    func update(from user: User) {
        self.id = user.id
        self.email = user.email
        self.fullName = user.fullName
        self.avatarUrl = user.avatarUrl
        self.isActive = user.isActive
        self.isPremium = user.isPremium
        self.preferences = user.preferences as NSObject?
        self.createdAt = user.createdAt
        self.updatedAt = user.updatedAt
    }
}

extension CDHousehold {
    func toHousehold() -> Household {
        return Household(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            ownerId: self.ownerId ?? UUID(),
            invitationCode: self.invitationCode ?? "",
            settings: self.settings as? [String: String],
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date(),
            members: self.members?.compactMap { ($0 as? CDUser)?.toUser() }
        )
    }
    
    func update(from household: Household) {
        self.id = household.id
        self.name = household.name
        self.ownerId = household.ownerId
        self.invitationCode = household.invitationCode
        self.settings = household.settings as NSObject?
        self.createdAt = household.createdAt
        self.updatedAt = household.updatedAt
    }
}

extension CDInventoryItem {
    func toInventoryItem() -> InventoryItem {
        return InventoryItem(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            category: self.category ?? "",
            quantity: self.quantity as Decimal? ?? 1.0,
            unit: self.unit ?? "",
            location: self.location ?? "",
            expiresAt: self.expiresAt,
            openedAt: self.openedAt,
            opened: self.opened,
            barcode: self.barcode,
            price: self.price as Decimal?,
            status: self.status ?? "active",
            imageUrl: self.imageUrl,
            notes: self.notes,
            nutritionalInfo: self.nutritionalInfo as? [String: String],
            userId: self.userId ?? UUID(),
            householdId: self.household?.id ?? UUID(),
            syncStatus: self.syncStatus ?? "synced",
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date()
        )
    }
    
    func update(from item: InventoryItem) {
        self.id = item.id
        self.name = item.name
        self.category = item.category
        self.quantity = item.quantity as NSDecimalNumber
        self.unit = item.unit
        self.location = item.location
        self.expiresAt = item.expiresAt
        self.openedAt = item.openedAt
        self.opened = item.opened
        self.barcode = item.barcode
        self.price = item.price as NSDecimalNumber?
        self.status = item.status
        self.imageUrl = item.imageUrl
        self.notes = item.notes
        self.nutritionalInfo = item.nutritionalInfo as NSObject?
        self.userId = item.userId
        self.syncStatus = item.syncStatus
        self.createdAt = item.createdAt
        self.updatedAt = item.updatedAt
    }
}

extension CDRecipe {
    func toRecipe() -> Recipe {
        let ingredientsData = self.ingredients ?? Data()
        let ingredients = try? JSONDecoder().decode([Ingredient].self, from: ingredientsData)
        
        let instructionsData = self.instructions ?? Data()
        let instructions = try? JSONDecoder().decode([String].self, from: instructionsData)
        
        return Recipe(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            description: self.description,
            ingredients: ingredients ?? [],
            instructions: instructions ?? [],
            cookTime: Int(self.cookTime),
            prepTime: Int(self.prepTime),
            totalTime: Int(self.totalTime),
            servings: Int(self.servings),
            difficulty: self.difficulty ?? "Easy",
            cuisine: self.cuisine,
            tags: self.tags as? [String],
            nutrition: self.nutrition as? [String: String],
            imageUrl: self.imageUrl,
            notes: self.notes,
            source: self.source,
            isPublic: self.isPublic,
            rating: self.rating as Decimal?,
            userId: self.userId ?? UUID(),
            householdId: self.household?.id ?? UUID(),
            syncStatus: self.syncStatus ?? "synced",
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date(),
            reviews: self.reviews?.compactMap { ($0 as? CDRecipeReview)?.toRecipeReview() }
        )
    }
    
    func update(from recipe: Recipe) {
        self.id = recipe.id
        self.name = recipe.name
        self.description = recipe.description
        self.cookTime = Int32(recipe.cookTime)
        self.prepTime = Int32(recipe.prepTime)
        self.totalTime = Int32(recipe.totalTime)
        self.servings = Int32(recipe.servings)
        self.difficulty = recipe.difficulty
        self.cuisine = recipe.cuisine
        self.imageUrl = recipe.imageUrl
        self.notes = recipe.notes
        self.source = recipe.source
        self.isPublic = recipe.isPublic
        self.rating = recipe.rating as NSDecimalNumber?
        self.userId = recipe.userId
        self.syncStatus = recipe.syncStatus
        self.createdAt = recipe.createdAt
        self.updatedAt = recipe.updatedAt
        
        if let ingredientsData = try? JSONEncoder().encode(recipe.ingredients) {
            self.ingredients = ingredientsData
        }
        
        if let instructionsData = try? JSONEncoder().encode(recipe.instructions) {
            self.instructions = instructionsData
        }
        
        self.tags = recipe.tags as NSObject?
        self.nutrition = recipe.nutrition as NSObject?
    }
}

extension CDRecipeReview {
    func toRecipeReview() -> RecipeReview {
        return RecipeReview(
            id: self.id ?? UUID(),
            rating: self.rating as Decimal? ?? 0.0,
            comment: self.comment,
            userId: self.userId ?? UUID(),
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date()
        )
    }
    
    func update(from review: RecipeReview) {
        self.id = review.id
        self.rating = review.rating as NSDecimalNumber
        self.comment = review.comment
        self.userId = review.userId
        self.createdAt = review.createdAt
        self.updatedAt = review.updatedAt
    }
}

extension CDMealPlan {
    func toMealPlan() -> MealPlan {
        return MealPlan(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            startDate: self.startDate ?? Date(),
            endDate: self.endDate ?? Date(),
            userId: self.userId ?? UUID(),
            householdId: self.household?.id ?? UUID(),
            syncStatus: self.syncStatus ?? "synced",
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date(),
            entries: self.entries?.compactMap { ($0 as? CDMealPlanEntry)?.toMealPlanEntry() }
        )
    }
    
    func update(from mealPlan: MealPlan) {
        self.id = mealPlan.id
        self.name = mealPlan.name
        self.startDate = mealPlan.startDate
        self.endDate = mealPlan.endDate
        self.userId = mealPlan.userId
        self.syncStatus = mealPlan.syncStatus
        self.createdAt = mealPlan.createdAt
        self.updatedAt = mealPlan.updatedAt
    }
}

extension CDMealPlanEntry {
    func toMealPlanEntry() -> MealPlanEntry {
        return MealPlanEntry(
            id: self.id ?? UUID(),
            date: self.date ?? Date(),
            mealType: self.mealType ?? "dinner",
            servings: Int(self.servings),
            notes: self.notes,
            recipeId: self.recipe?.id,
            mealPlanId: self.mealPlan?.id ?? UUID(),
            syncStatus: self.syncStatus ?? "synced",
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date(),
            recipe: self.recipe?.toRecipe()
        )
    }
    
    func update(from entry: MealPlanEntry) {
        self.id = entry.id
        self.date = entry.date
        self.mealType = entry.mealType
        self.servings = Int32(entry.servings)
        self.notes = entry.notes
        self.syncStatus = entry.syncStatus
        self.createdAt = entry.createdAt
        self.updatedAt = entry.updatedAt
    }
}

extension CDShoppingList {
    func toShoppingList() -> ShoppingList {
        return ShoppingList(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            userId: self.userId ?? UUID(),
            householdId: self.household?.id ?? UUID(),
            syncStatus: self.syncStatus ?? "synced",
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date(),
            items: self.items?.compactMap { ($0 as? CDShoppingItem)?.toShoppingItem() }
        )
    }
    
    func update(from shoppingList: ShoppingList) {
        self.id = shoppingList.id
        self.name = shoppingList.name
        self.userId = shoppingList.userId
        self.syncStatus = shoppingList.syncStatus
        self.createdAt = shoppingList.createdAt
        self.updatedAt = shoppingList.updatedAt
    }
}

extension CDShoppingItem {
    func toShoppingItem() -> ShoppingItem {
        return ShoppingItem(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            category: self.category ?? "",
            quantity: self.quantity as Decimal? ?? 1.0,
            unit: self.unit ?? "",
            completed: self.completed,
            price: self.price as Decimal?,
            notes: self.notes,
            userId: self.userId ?? UUID(),
            shoppingListId: self.shoppingList?.id ?? UUID(),
            syncStatus: self.syncStatus ?? "synced",
            createdAt: self.createdAt ?? Date(),
            updatedAt: self.updatedAt ?? Date()
        )
    }
    
    func update(from item: ShoppingItem) {
        self.id = item.id
        self.name = item.name
        self.category = item.category
        self.quantity = item.quantity as NSDecimalNumber
        self.unit = item.unit
        self.completed = item.completed
        self.price = item.price as NSDecimalNumber?
        self.notes = item.notes
        self.userId = item.userId
        self.syncStatus = item.syncStatus
        self.createdAt = item.createdAt
        self.updatedAt = item.updatedAt
    }
}

extension CDAchievement {
    func toAchievement() -> Achievement {
        return Achievement(
            id: self.id ?? UUID(),
            name: self.name ?? "",
            description: self.description ?? "",
            icon: self.icon ?? "",
            category: self.category ?? "",
            points: Int(self.points),
            requirement: self.requirement ?? "",
            unlockedAt: self.unlockedAt,
            userId: self.userId ?? UUID()
        )
    }
    
    func update(from achievement: Achievement) {
        self.id = achievement.id
        self.name = achievement.name
        self.description = achievement.description
        self.icon = achievement.icon
        self.category = achievement.category
        self.points = Int32(achievement.points)
        self.requirement = achievement.requirement
        self.unlockedAt = achievement.unlockedAt
        self.userId = achievement.userId
    }
}

extension String {
    var isValidEmail: Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        return NSPredicate(format: "SELF MATCHES %@", emailRegex).evaluate(with: self)
    }
    
    var isValidPassword: Bool {
        return self.count >= 8
    }
}

extension Decimal {
    func formattedString(maximumFractionDigits: Int = 2) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.maximumFractionDigits = maximumFractionDigits
        return formatter.string(from: self as NSDecimalNumber) ?? ""
    }
}

extension UUID {
    static func fromString(_ string: String) -> UUID? {
        return UUID(uuidString: string)
    }
}

extension Data {
    func toString() -> String? {
        return String(data: self, encoding: .utf8)
    }
}