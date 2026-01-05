import Foundation
import Combine
import CoreData

class RecipeService: ObservableObject {
    static let shared = RecipeService()
    
    @Published var recipes: [Recipe] = []
    @Published var isLoading: Bool = false
    @Published var lastSyncDate: Date?
    
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        loadLocalRecipes()
    }
    
    func loadLocalRecipes() {
        Task { @MainActor in
            do {
                let localRecipes = try await CoreDataManager.shared.fetch(CDRecipe.self)
                self.recipes = localRecipes.map { $0.toRecipe() }
            } catch {
                print("Failed to load local recipes: \(error)")
            }
        }
    }
    
    func syncRecipes() -> AnyPublisher<Void, APIError> {
        isLoading = true
        
        let unsyncedRecipes = recipes.filter { $0.syncStatus != "synced" }
        
        var publishers: [AnyPublisher<Void, APIError>] = []
        
        for recipe in unsyncedRecipes {
            switch recipe.syncStatus {
            case "created":
                publishers.append(createRecipeOnServer(recipe))
            case "updated":
                publishers.append(updateRecipeOnServer(recipe))
            case "deleted":
                publishers.append(deleteRecipeOnServer(recipe))
            default:
                break
            }
        }
        
        publishers.append(fetchRecipesFromServer())
        
        return Publishers.MergeMany(publishers)
            .collect()
            .map { _ in () }
            .handleEvents(receiveCompletion: { [weak self] _ in
                self?.isLoading = false
                self?.lastSyncDate = Date()
            })
            .eraseToAnyPublisher()
    }
    
    func createRecipe(_ recipe: Recipe) -> AnyPublisher<Recipe, APIError> {
        var newRecipe = recipe
        newRecipe.syncStatus = "created"
        
        return APIService.shared.post("/recipes", parameters: newRecipe.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdRecipe: Recipe) in
                self?.updateLocalRecipe(createdRecipe)
            })
            .eraseToAnyPublisher()
    }
    
    func updateRecipe(_ recipe: Recipe) -> AnyPublisher<Recipe, APIError> {
        var updatedRecipe = recipe
        updatedRecipe.syncStatus = "updated"
        
        return APIService.shared.put("/recipes/\(recipe.id)", parameters: updatedRecipe.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedRecipe: Recipe) in
                self?.updateLocalRecipe(updatedRecipe)
            })
            .eraseToAnyPublisher()
    }
    
    func deleteRecipe(_ recipe: Recipe) -> AnyPublisher<Void, APIError> {
        if recipe.syncStatus == "created" {
            removeLocalRecipe(recipe)
            return Just(()).setFailureType(to: APIError.self).eraseToAnyPublisher()
        } else {
            var deletedRecipe = recipe
            deletedRecipe.syncStatus = "deleted"
            
            return APIService.shared.delete("/recipes/\(recipe.id)")
                .handleEvents(receiveOutput: { [weak self] _ in
                    self?.removeLocalRecipe(recipe)
                })
                .eraseToAnyPublisher()
        }
    }
    
    func searchRecipes(query: String? = nil, cuisine: String? = nil, difficulty: String? = nil) -> [Recipe] {
        return recipes.filter { recipe in
            let matchesQuery = query == nil || query!.isEmpty || 
                             recipe.name.localizedCaseInsensitiveContains(query!) ||
                             recipe.description?.localizedCaseInsensitiveContains(query!) == true ||
                             recipe.tags?.contains { $0.localizedCaseInsensitiveContains(query!) } == true
            
            let matchesCuisine = cuisine == nil || recipe.cuisine == cuisine
            let matchesDifficulty = difficulty == nil || recipe.difficulty == difficulty
            
            return matchesQuery && matchesCuisine && matchesDifficulty && recipe.syncStatus != "deleted"
        }
    }
    
    func getRecipesByIngredients(_ ingredients: [String]) -> [Recipe] {
        return recipes.filter { recipe in
            let recipeIngredients = recipe.ingredients.map { $0.name.lowercased() }
            return ingredients.contains { ingredient in
                recipeIngredients.contains { $0.contains(ingredient.lowercased()) }
            }
        }
    }
    
    func rateRecipe(_ recipeId: UUID, rating: Decimal, comment: String?) -> AnyPublisher<RecipeReview, APIError> {
        let parameters: [String: Any] = [
            "rating": rating.doubleValue,
            "comment": comment as Any
        ]
        
        return APIService.shared.post("/recipes/\(recipeId)/reviews", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (review: RecipeReview) in
                self?.refreshRecipe(recipeId)
            })
            .eraseToAnyPublisher()
    }
    
    func importRecipe(from url: String) -> AnyPublisher<Recipe, APIError> {
        let parameters: [String: Any] = ["url": url]
        
        return APIService.shared.post("/recipes/import", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (recipe: Recipe) in
                self?.updateLocalRecipe(recipe)
            })
            .eraseToAnyPublisher()
    }
    
    func generateRecipe(from ingredients: [String]) -> AnyPublisher<Recipe, APIError> {
        let parameters: [String: Any] = ["ingredients": ingredients]
        
        return APIService.shared.post("/ai/recipes/generate", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (recipe: Recipe) in
                self?.updateLocalRecipe(recipe)
            })
            .eraseToAnyPublisher()
    }
    
    private func createRecipeOnServer(_ recipe: Recipe) -> AnyPublisher<Void, APIError> {
        return APIService.shared.post("/recipes", parameters: recipe.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdRecipe: Recipe) in
                self?.updateLocalRecipe(createdRecipe)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateRecipeOnServer(_ recipe: Recipe) -> AnyPublisher<Void, APIError> {
        return APIService.shared.put("/recipes/\(recipe.id)", parameters: recipe.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedRecipe: Recipe) in
                self?.updateLocalRecipe(updatedRecipe)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func deleteRecipeOnServer(_ recipe: Recipe) -> AnyPublisher<Void, APIError> {
        return APIService.shared.delete("/recipes/\(recipe.id)")
            .handleEvents(receiveOutput: { [weak self] _ in
                self?.removeLocalRecipe(recipe)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func fetchRecipesFromServer() -> AnyPublisher<Void, APIError> {
        var parameters: [String: Any] = [:]
        if let lastSync = lastSyncDate {
            parameters["updated_after"] = ISO8601DateFormatter().string(from: lastSync)
        }
        
        return APIService.shared.get("/recipes", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (response: PaginatedResponse<Recipe>) in
                self?.mergeServerRecipes(response.items)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func refreshRecipe(_ recipeId: UUID) {
        APIService.shared.get("/recipes/\(recipeId)")
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] (recipe: Recipe) in
                    self?.updateLocalRecipe(recipe)
                }
            )
            .store(in: &cancellables)
    }
    
    private func updateLocalRecipe(_ recipe: Recipe) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDRecipe> = CDRecipe.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", recipe.id as CVarArg)
                
                if let existingRecipe = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    existingRecipe.update(from: recipe)
                } else {
                    let newRecipe = CDRecipe(context: CoreDataManager.shared.context)
                    newRecipe.update(from: recipe)
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalRecipes()
            } catch {
                print("Failed to update local recipe: \(error)")
            }
        }
    }
    
    private func removeLocalRecipe(_ recipe: Recipe) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDRecipe> = CDRecipe.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", recipe.id as CVarArg)
                
                if let existingRecipe = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    try await CoreDataManager.shared.delete(existingRecipe)
                    loadLocalRecipes()
                }
            } catch {
                print("Failed to remove local recipe: \(error)")
            }
        }
    }
    
    private func mergeServerRecipes(_ serverRecipes: [Recipe]) {
        Task { @MainActor in
            do {
                let localRecipes = try await CoreDataManager.shared.fetch(CDRecipe.self)
                
                for serverRecipe in serverRecipes {
                    let fetchRequest: NSFetchRequest<CDRecipe> = CDRecipe.fetchRequest()
                    fetchRequest.predicate = NSPredicate(format: "id == %@", serverRecipe.id as CVarArg)
                    
                    if let localRecipe = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                        localRecipe.update(from: serverRecipe)
                    } else {
                        let newRecipe = CDRecipe(context: CoreDataManager.shared.context)
                        newRecipe.update(from: serverRecipe)
                    }
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalRecipes()
            } catch {
                print("Failed to merge server recipes: \(error)")
            }
        }
    }
}

extension Recipe {
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "name": name,
            "difficulty": difficulty,
            "servings": servings,
            "cook_time": cookTime,
            "prep_time": prepTime,
            "total_time": totalTime,
            "is_public": isPublic,
            "user_id": userId.uuidString,
            "household_id": householdId.uuidString,
            "sync_status": syncStatus
        ]
        
        if let description = description {
            dict["description"] = description
        }
        
        if let cuisine = cuisine {
            dict["cuisine"] = cuisine
        }
        
        if let imageUrl = imageUrl {
            dict["image_url"] = imageUrl
        }
        
        if let notes = notes {
            dict["notes"] = notes
        }
        
        if let source = source {
            dict["source"] = source
        }
        
        if let rating = rating {
            dict["rating"] = rating.doubleValue
        }
        
        dict["ingredients"] = ingredients.map { ingredient in
            [
                "id": ingredient.id.uuidString,
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "unit": ingredient.unit,
                "notes": ingredient.notes as Any,
                "is_optional": ingredient.isOptional
            ]
        }
        
        dict["instructions"] = instructions
        dict["tags"] = tags ?? []
        dict["nutrition"] = nutrition ?? [:]
        
        dict["created_at"] = ISO8601DateFormatter().string(from: createdAt)
        dict["updated_at"] = ISO8601DateFormatter().string(from: updatedAt)
        
        return dict
    }
}