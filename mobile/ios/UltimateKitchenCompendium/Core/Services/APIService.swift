//
//  APIService.swift
//  UltimateKitchenCompendium
//
//  API client for backend communication
//

import Foundation
import Combine
import Network

protocol APIService {
    // Auth
    func login(username: String, password: String) async throws -> AuthResponse
    func register(userData: RegisterRequest) async throws -> AuthResponse
    func refreshToken(refreshToken: String) async throws -> AuthResponse
    func getCurrentUser() async throws -> User
    
    // Inventory
    func getInventoryItems(limit: Int?, skip: Int?, search: String?, category: String?, location: String?) async throws -> [InventoryItem]
    func getInventoryItem(id: UUID) async throws -> InventoryItem
    func createInventoryItem(_ item: InventoryItem) async throws -> InventoryItem
    func updateInventoryItem(_ item: InventoryItem) async throws -> InventoryItem
    func deleteInventoryItem(id: UUID) async throws
    func scanBarcode(_ barcode: String, location: StorageLocation?) async throws -> BarcodeLookupResponse
    func getWasteForecast(daysAhead: Int) async throws -> WasteForecast
    
    // Recipes
    func getRecipes(limit: Int?, skip: Int?, search: String?, cuisine: String?, difficulty: String?) async throws -> [Recipe]
    func getRecipe(id: UUID) async throws -> Recipe
    func createRecipe(_ recipe: Recipe) async throws -> Recipe
    func updateRecipe(_ recipe: Recipe) async throws -> Recipe
    func deleteRecipe(id: UUID) async throws
    func importRecipeFromURL(_ url: String) async throws -> Recipe
    
    // Meal Planning
    func getMealPlans(limit: Int?, skip: Int?, startDate: Date?, endDate: Date?) async throws -> [MealPlan]
    func getMealPlan(id: UUID) async throws -> MealPlan
    func createMealPlan(_ plan: MealPlan) async throws -> MealPlan
    func updateMealPlan(_ plan: MealPlan) async throws -> MealPlan
    func deleteMealPlan(id: UUID) async throws
    func generateMealPlan(startDate: Date, endDate: Date, dietaryPreferences: [String]?, budgetRange: (min: Double, max: Double)?) async throws -> MealPlan
    
    // Shopping Lists
    func getShoppingLists(limit: Int?, skip: Int?, isActive: Bool?) async throws -> [ShoppingList]
    func getShoppingList(id: UUID) async throws -> ShoppingList
    func createShoppingList(_ list: ShoppingList) async throws -> ShoppingList
    func updateShoppingList(_ list: ShoppingList) async throws -> ShoppingList
    func deleteShoppingList(id: UUID) async throws
    func generateShoppingListFromPlan(planId: UUID) async throws -> ShoppingList
    
    // AI Services
    func chatWithAI(message: String, context: String?) async throws -> AIChatResponse
    func getRecipeSuggestions(availableIngredients: [String]?, dietaryRestrictions: [String]?, cuisineType: String?) async throws -> [RecipeSuggestion]
    func adaptRecipe(recipeId: UUID, adaptations: RecipeAdaptations) async throws -> Recipe
    
    // Uploads
    func uploadImage(_ image: UIImage, type: UploadType) async throws -> String
}

// MARK: - API Service Implementation

class APIServiceImpl: APIService {
    private let baseURL: String
    private let session: URLSession
    private var authToken: String?
    private let monitor = NWPathMonitor()
    private var isConnected = true
    
    init(baseURL: String = "http://localhost:8000/api/v1") {
        self.baseURL = baseURL
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        config.httpShouldSetCookies = true
        config.httpCookieAcceptPolicy = .always
        
        self.session = URLSession(configuration: config)
        
        setupNetworkMonitoring()
    }
    
    private func setupNetworkMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            self?.isConnected = path.status == .satisfied
        }
        monitor.start(queue: DispatchQueue.global())
    }
    
    func setAuthToken(_ token: String) {
        self.authToken = token
    }
    
    func clearAuthToken() {
        self.authToken = nil
    }
    
    // MARK: - Private Methods
    
    private func buildRequest(path: String, method: String = "GET", body: Data? = nil) throws -> URLRequest {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = body
        }
        
        return request
    }
    
    private func executeRequest<T: Decodable>(_ request: URLRequest) async throws -> T {
        if !isConnected {
            throw APIError.noInternetConnection
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            if let errorResponse = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
                throw APIError.serverError(errorResponse.detail ?? "Unknown error")
            }
            throw APIError.httpError(httpResponse.statusCode)
        }
        
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        
        return try decoder.decode(T.self, from: data)
    }
    
    private func executeRequest(_ request: URLRequest) async throws {
        if !isConnected {
            throw APIError.noInternetConnection
        }
        
        let (_, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }
    }
    
    // MARK: - Auth Endpoints
    
    func login(username: String, password: String) async throws -> AuthResponse {
        let requestData = LoginRequest(username: username, password: password)
        let body = try JSONEncoder().encode(requestData)
        let request = try buildRequest(path: "/auth/login", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func register(userData: RegisterRequest) async throws -> AuthResponse {
        let body = try JSONEncoder().encode(userData)
        let request = try buildRequest(path: "/auth/register", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func refreshToken(refreshToken: String) async throws -> AuthResponse {
        let request = try buildRequest(path: "/auth/refresh?refresh_token=\(refreshToken)", method: "POST")
        return try await executeRequest(request)
    }
    
    func getCurrentUser() async throws -> User {
        let request = try buildRequest(path: "/auth/me")
        return try await executeRequest(request)
    }
    
    // MARK: - Inventory Endpoints
    
    func getInventoryItems(limit: Int? = nil, skip: Int? = nil, search: String? = nil, category: String? = nil, location: String? = nil) async throws -> [InventoryItem] {
        var queryItems: [String] = []
        if let limit = limit { queryItems.append("limit=\(limit)") }
        if let skip = skip { queryItems.append("skip=\(skip)") }
        if let search = search { queryItems.append("search=\(search.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")") }
        if let category = category { queryItems.append("category=\(category)") }
        if let location = location { queryItems.append("location=\(location)") }
        
        let query = queryItems.isEmpty ? "" : "?\(queryItems.joined(separator: "&"))"
        let request = try buildRequest(path: "/inventory\(query)")
        return try await executeRequest(request)
    }
    
    func getInventoryItem(id: UUID) async throws -> InventoryItem {
        let request = try buildRequest(path: "/inventory/\(id.uuidString)")
        return try await executeRequest(request)
    }
    
    func createInventoryItem(_ item: InventoryItem) async throws -> InventoryItem {
        let body = try JSONEncoder().encode(item)
        let request = try buildRequest(path: "/inventory", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func updateInventoryItem(_ item: InventoryItem) async throws -> InventoryItem {
        let body = try JSONEncoder().encode(item)
        let request = try buildRequest(path: "/inventory/\(item.id.uuidString)", method: "PUT", body: body)
        return try await executeRequest(request)
    }
    
    func deleteInventoryItem(id: UUID) async throws {
        let request = try buildRequest(path: "/inventory/\(id.uuidString)", method: "DELETE")
        try await executeRequest(request)
    }
    
    func scanBarcode(_ barcode: String, location: StorageLocation?) async throws -> BarcodeLookupResponse {
        let requestData = ["barcode": barcode, "location": location?.rawValue as Any]
        let body = try JSONSerialization.data(withJSONObject: requestData)
        let request = try buildRequest(path: "/inventory/scan-barcode", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func getWasteForecast(daysAhead: Int) async throws -> WasteForecast {
        let request = try buildRequest(path: "/inventory/forecast-waste?days_ahead=\(daysAhead)")
        return try await executeRequest(request)
    }
    
    // MARK: - Recipe Endpoints
    
    func getRecipes(limit: Int? = nil, skip: Int? = nil, search: String? = nil, cuisine: String? = nil, difficulty: String? = nil) async throws -> [Recipe] {
        var queryItems: [String] = []
        if let limit = limit { queryItems.append("limit=\(limit)") }
        if let skip = skip { queryItems.append("skip=\(skip)") }
        if let search = search { queryItems.append("search=\(search.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")") }
        if let cuisine = cuisine { queryItems.append("cuisine=\(cuisine)") }
        if let difficulty = difficulty { queryItems.append("difficulty=\(difficulty)") }
        
        let query = queryItems.isEmpty ? "" : "?\(queryItems.joined(separator: "&"))"
        let request = try buildRequest(path: "/recipes\(query)")
        return try await executeRequest(request)
    }
    
    func getRecipe(id: UUID) async throws -> Recipe {
        let request = try buildRequest(path: "/recipes/\(id.uuidString)")
        return try await executeRequest(request)
    }
    
    func createRecipe(_ recipe: Recipe) async throws -> Recipe {
        let body = try JSONEncoder().encode(recipe)
        let request = try buildRequest(path: "/recipes", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func updateRecipe(_ recipe: Recipe) async throws -> Recipe {
        let body = try JSONEncoder().encode(recipe)
        let request = try buildRequest(path: "/recipes/\(recipe.id.uuidString)", method: "PUT", body: body)
        return try await executeRequest(request)
    }
    
    func deleteRecipe(id: UUID) async throws {
        let request = try buildRequest(path: "/recipes/\(id.uuidString)", method: "DELETE")
        try await executeRequest(request)
    }
    
    func importRecipeFromURL(_ url: String) async throws -> Recipe {
        let requestData = ["url": url]
        let body = try JSONSerialization.data(withJSONObject: requestData)
        let request = try buildRequest(path: "/recipes/import-url", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    // MARK: - Meal Planning Endpoints
    
    func getMealPlans(limit: Int? = nil, skip: Int? = nil, startDate: Date? = nil, endDate: Date? = nil) async throws -> [MealPlan] {
        var queryItems: [String] = []
        if let limit = limit { queryItems.append("limit=\(limit)") }
        if let skip = skip { queryItems.append("skip=\(skip)") }
        if let startDate = startDate { queryItems.append("start_date=\(ISO8601DateFormatter().string(from: startDate))") }
        if let endDate = endDate { queryItems.append("end_date=\(ISO8601DateFormatter().string(from: endDate))") }
        
        let query = queryItems.isEmpty ? "" : "?\(queryItems.joined(separator: "&"))"
        let request = try buildRequest(path: "/meal-plans\(query)")
        return try await executeRequest(request)
    }
    
    func getMealPlan(id: UUID) async throws -> MealPlan {
        let request = try buildRequest(path: "/meal-plans/\(id.uuidString)")
        return try await executeRequest(request)
    }
    
    func createMealPlan(_ plan: MealPlan) async throws -> MealPlan {
        let body = try JSONEncoder().encode(plan)
        let request = try buildRequest(path: "/meal-plans", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func updateMealPlan(_ plan: MealPlan) async throws -> MealPlan {
        let body = try JSONEncoder().encode(plan)
        let request = try buildRequest(path: "/meal-plans/\(plan.id.uuidString)", method: "PUT", body: body)
        return try await executeRequest(request)
    }
    
    func deleteMealPlan(id: UUID) async throws {
        let request = try buildRequest(path: "/meal-plans/\(id.uuidString)", method: "DELETE")
        try await executeRequest(request)
    }
    
    func generateMealPlan(startDate: Date, endDate: Date, dietaryPreferences: [String]?, budgetRange: (min: Double, max: Double)?) async throws -> MealPlan {
        var requestData: [String: Any] = [
            "start_date": ISO8601DateFormatter().string(from: startDate),
            "end_date": ISO8601DateFormatter().string(from: endDate)
        ]
        
        if let preferences = dietaryPreferences {
            requestData["dietary_preferences"] = preferences
        }
        
        if let budget = budgetRange {
            requestData["budget_range"] = [budget.min, budget.max]
        }
        
        let body = try JSONSerialization.data(withJSONObject: requestData)
        let request = try buildRequest(path: "/meal-plans/generate", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    // MARK: - Shopping List Endpoints
    
    func getShoppingLists(limit: Int? = nil, skip: Int? = nil, isActive: Bool? = nil) async throws -> [ShoppingList] {
        var queryItems: [String] = []
        if let limit = limit { queryItems.append("limit=\(limit)") }
        if let skip = skip { queryItems.append("skip=\(skip)") }
        if let isActive = isActive { queryItems.append("is_active=\(isActive)") }
        
        let query = queryItems.isEmpty ? "" : "?\(queryItems.joined(separator: "&"))"
        let request = try buildRequest(path: "/shopping-lists\(query)")
        return try await executeRequest(request)
    }
    
    func getShoppingList(id: UUID) async throws -> ShoppingList {
        let request = try buildRequest(path: "/shopping-lists/\(id.uuidString)")
        return try await executeRequest(request)
    }
    
    func createShoppingList(_ list: ShoppingList) async throws -> ShoppingList {
        let body = try JSONEncoder().encode(list)
        let request = try buildRequest(path: "/shopping-lists", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func updateShoppingList(_ list: ShoppingList) async throws -> ShoppingList {
        let body = try JSONEncoder().encode(list)
        let request = try buildRequest(path: "/shopping-lists/\(list.id.uuidString)", method: "PUT", body: body)
        return try await executeRequest(request)
    }
    
    func deleteShoppingList(id: UUID) async throws {
        let request = try buildRequest(path: "/shopping-lists/\(id.uuidString)", method: "DELETE")
        try await executeRequest(request)
    }
    
    func generateShoppingListFromPlan(planId: UUID) async throws -> ShoppingList {
        let requestData = ["plan_id": planId.uuidString]
        let body = try JSONSerialization.data(withJSONObject: requestData)
        let request = try buildRequest(path: "/shopping-lists/generate-from-plan", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    // MARK: - AI Endpoints
    
    func chatWithAI(message: String, context: String?) async throws -> AIChatResponse {
        var requestData: [String: Any] = ["message": message]
        if let context = context {
            requestData["context"] = context
        }
        
        let body = try JSONSerialization.data(withJSONObject: requestData)
        let request = try buildRequest(path: "/ai/chat", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    func getRecipeSuggestions(availableIngredients: [String]?, dietaryRestrictions: [String]?, cuisineType: String?) async throws -> [RecipeSuggestion] {
        var queryItems: [String] = []
        if let ingredients = availableIngredients {
            queryItems.append("available_ingredients=\(ingredients.joined(separator: ","))")
        }
        if let restrictions = dietaryRestrictions {
            queryItems.append("dietary_restrictions=\(restrictions.joined(separator: ","))")
        }
        if let cuisine = cuisineType {
            queryItems.append("cuisine_type=\(cuisine)")
        }
        
        let query = queryItems.isEmpty ? "" : "?\(queryItems.joined(separator: "&"))"
        let request = try buildRequest(path: "/ai/suggest-recipes\(query)")
        return try await executeRequest(request)
    }
    
    func adaptRecipe(recipeId: UUID, adaptations: RecipeAdaptations) async throws -> Recipe {
        let requestData = [
            "recipe_id": recipeId.uuidString,
            "adaptations": [
                "servings": adaptations.servings as Any,
                "dietary_restrictions": adaptations.dietaryRestrictions as Any,
                "available_ingredients": adaptations.availableIngredients as Any
            ]
        ] as [String: Any]
        
        let body = try JSONSerialization.data(withJSONObject: requestData)
        let request = try buildRequest(path: "/ai/adapt-recipe", method: "POST", body: body)
        return try await executeRequest(request)
    }
    
    // MARK: - Uploads
    
    func uploadImage(_ image: UIImage, type: UploadType) async throws -> String {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            throw APIError.invalidImage
        }
        
        let boundary = UUID().uuidString
        var request = try buildRequest(path: "/uploads", method: "POST")
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"type\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(type.rawValue)\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let response: [String: String] = try await executeRequest(request)
        guard let url = response["url"] else {
            throw APIError.invalidResponse
        }
        return url
    }
}

// MARK: - Error Handling

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(Int)
    case serverError(String)
    case noInternetConnection
    case invalidImage
    case encodingError
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid server response"
        case .httpError(let code):
            return "HTTP Error \(code)"
        case .serverError(let message):
            return message
        case .noInternetConnection:
            return "No internet connection"
        case .invalidImage:
            return "Invalid image data"
        case .encodingError:
            return "Failed to encode request data"
        case .decodingError:
            return "Failed to decode response data"
        }
    }
}

struct APIErrorResponse: Codable {
    let detail: String?
    let message: String?
}

// MARK: - Service Locator

class ServiceLocator {
    static let shared = ServiceLocator()
    private var services: [ObjectIdentifier: Any] = [:]
    
    private init() {}
    
    func register<T>(_ type: T.Type, factory: @escaping () -> T) {
        let key = ObjectIdentifier(type)
        services[key] = factory
    }
    
    func resolve<T>(_ type: T.Type) -> T? {
        let key = ObjectIdentifier(type)
        guard let factory = services[key] as? () -> T else { return nil }
        return factory()
    }
}

// MARK: - Upload Types

enum UploadType: String {
    case recipeImage = "recipe_image"
    case profileAvatar = "profile_avatar"
    case mealPhoto = "meal_photo"
}