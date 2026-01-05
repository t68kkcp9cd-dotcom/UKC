import Foundation
import Combine
import KeychainAccess

class AuthService: ObservableObject {
    static let shared = AuthService()
    
    @Published var isAuthenticated: Bool = false
    @Published var currentUser: User?
    @Published var isLoading: Bool = false
    
    private let keychain = Keychain(service: "com.ultimatekitchencompendium.auth")
    private let userDefaults = UserDefaults.standard
    
    private init() {
        checkAuthStatus()
    }
    
    var accessToken: String? {
        get { try? keychain.get("accessToken") }
        set {
            if let token = newValue {
                try? keychain.set(token, key: "accessToken")
            } else {
                try? keychain.remove("accessToken")
            }
        }
    }
    
    var refreshToken: String? {
        get { try? keychain.get("refreshToken") }
        set {
            if let token = newValue {
                try? keychain.set(token, key: "refreshToken")
            } else {
                try? keychain.remove("refreshToken")
            }
        }
    }
    
    func checkAuthStatus() {
        isAuthenticated = accessToken != nil
        if isAuthenticated {
            loadCurrentUser()
        }
    }
    
    func login(email: String, password: String) -> AnyPublisher<User, APIError> {
        isLoading = true
        
        let parameters: [String: Any] = [
            "email": email,
            "password": password
        ]
        
        return APIService.shared.post("/auth/login", parameters: parameters)
            .flatMap { [weak self] (response: AuthResponse) -> AnyPublisher<User, APIError> in
                guard let self = self else {
                    return Fail(error: APIError.networkError("Self deallocated"))
                        .eraseToAnyPublisher()
                }
                
                self.accessToken = response.accessToken
                self.refreshToken = response.refreshToken
                self.isAuthenticated = true
                
                return self.loadCurrentUser()
            }
            .handleEvents(receiveCompletion: { [weak self] _ in
                self?.isLoading = false
            })
            .eraseToAnyPublisher()
    }
    
    func register(email: String, password: String, fullName: String) -> AnyPublisher<User, APIError> {
        isLoading = true
        
        let parameters: [String: Any] = [
            "email": email,
            "password": password,
            "fullName": fullName
        ]
        
        return APIService.shared.post("/auth/register", parameters: parameters)
            .flatMap { [weak self] (response: AuthResponse) -> AnyPublisher<User, APIError> in
                guard let self = self else {
                    return Fail(error: APIError.networkError("Self deallocated"))
                        .eraseToAnyPublisher()
                }
                
                self.accessToken = response.accessToken
                self.refreshToken = response.refreshToken
                self.isAuthenticated = true
                
                return self.loadCurrentUser()
            }
            .handleEvents(receiveCompletion: { [weak self] _ in
                self?.isLoading = false
            })
            .eraseToAnyPublisher()
    }
    
    func logout() {
        clearTokens()
        currentUser = nil
        isAuthenticated = false
        
        CoreDataManager.shared.context.performAndWait {
            let entities = ["CDUser", "CDHousehold", "CDInventoryItem", "CDRecipe", "CDMealPlan", "CDShoppingList"]
            for entity in entities {
                let fetchRequest = NSFetchRequest<NSFetchRequestResult>(entityName: entity)
                let deleteRequest = NSBatchDeleteRequest(fetchRequest: fetchRequest)
                
                do {
                    try CoreDataManager.shared.context.execute(deleteRequest)
                } catch {
                    print("Failed to clear entity \(entity): \(error)")
                }
            }
            
            try? CoreDataManager.shared.saveContext()
        }
    }
    
    func refreshAccessToken() -> AnyPublisher<String, APIError> {
        guard let refreshToken = refreshToken else {
            return Fail(error: APIError.unauthorized)
                .eraseToAnyPublisher()
        }
        
        let parameters: [String: Any] = [
            "refreshToken": refreshToken
        ]
        
        return APIService.shared.post("/auth/refresh", parameters: parameters)
            .map { [weak self] (response: RefreshResponse) -> String in
                self?.accessToken = response.accessToken
                return response.accessToken
            }
            .eraseToAnyPublisher()
    }
    
    private func loadCurrentUser() -> AnyPublisher<User, APIError> {
        return APIService.shared.get("/users/me")
            .handleEvents(receiveOutput: { [weak self] (user: User) in
                self?.currentUser = user
                
                Task { @MainActor in
                    await CoreDataManager.shared.context.perform {
                        let fetchRequest: NSFetchRequest<CDUser> = CDUser.fetchRequest()
                        fetchRequest.predicate = NSPredicate(format: "id == %@", user.id as CVarArg)
                        
                        if let existingUser = try? CoreDataManager.shared.context.fetch(fetchRequest).first {
                            existingUser.update(from: user)
                        } else {
                            let newUser = CDUser(context: CoreDataManager.shared.context)
                            newUser.update(from: user)
                        }
                        
                        try? CoreDataManager.shared.saveContext()
                    }
                }
            })
            .eraseToAnyPublisher()
    }
    
    private func clearTokens() {
        try? keychain.remove("accessToken")
        try? keychain.remove("refreshToken")
    }
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let expiresIn: Int
}

struct RefreshResponse: Codable {
    let accessToken: String
    let tokenType: String
    let expiresIn: Int
}