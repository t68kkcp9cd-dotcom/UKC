//
//  User.swift
//  UltimateKitchenCompendium
//
//  User data models and authentication
//

import Foundation
import CoreData

// MARK: - Domain Models

struct User: Codable, Identifiable {
    let id: UUID
    let username: String
    let email: String
    var householdId: UUID?
    let isActive: Bool
    let isPremium: Bool
    let createdAt: Date
    let updatedAt: Date
    var profile: UserProfile?
    
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case householdId = "household_id"
        case isActive = "is_active"
        case isPremium = "is_premium"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case profile
    }
}

struct UserProfile: Codable {
    let id: UUID
    let userId: UUID
    var displayName: String?
    var avatarUrl: URL?
    var dietaryTags: [String]
    var allergens: [String]
    var preferences: [String: AnyCodable]
    var featureToggles: [String: Bool]
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case displayName = "display_name"
        case avatarUrl = "avatar_url"
        case dietaryTags = "dietary_tags"
        case allergens
        case preferences
        case featureToggles = "feature_toggles"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

struct Household: Codable, Identifiable {
    let id: UUID
    var name: String
    let ownerId: UUID
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, name
        case ownerId = "owner_id"
        case createdAt = "created_at"
    }
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String?
    let tokenType: String
    let expiresIn: Int
    let user: User
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
        case user
    }
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct RegisterRequest: Codable {
    let username: String
    let email: String
    let password: String
    let householdId: UUID?
    
    enum CodingKeys: String, CodingKey {
        case username, email, password
        case householdId = "household_id"
    }
}

// MARK: - Core Data Models

extension User {
    @discardableResult
    func toCoreData(context: NSManagedObjectContext) -> UserEntity {
        let entity = UserEntity(context: context)
        entity.id = id
        entity.username = username
        entity.email = email
        entity.householdId = householdId
        entity.isActive = isActive
        entity.isPremium = isPremium
        entity.createdAt = createdAt
        entity.updatedAt = updatedAt
        return entity
    }
}

extension UserEntity {
    func toDomain() -> User {
        return User(
            id: id ?? UUID(),
            username: username ?? "",
            email: email ?? "",
            householdId: householdId,
            isActive: isActive,
            isPremium: isPremium,
            createdAt: createdAt ?? Date(),
            updatedAt: updatedAt ?? Date(),
            profile: profile?.toDomain()
        )
    }
}

// MARK: - User Preferences

enum DietaryTag: String, CaseIterable {
    case vegetarian = "vegetarian"
    case vegan = "vegan"
    case glutenFree = "gluten-free"
    case dairyFree = "dairy-free"
    case keto = "keto"
    case paleo = "paleo"
    case lowCarb = "low-carb"
    case lowSodium = "low-sodium"
    case halal = "halal"
    case kosher = "kosher"
}

enum Allergen: String, CaseIterable {
    case nuts = "nuts"
    case peanuts = "peanuts"
    case dairy = "dairy"
    case eggs = "eggs"
    case soy = "soy"
    case wheat = "wheat"
    case fish = "fish"
    case shellfish = "shellfish"
    case sesame = "sesame"
    case sulfites = "sulfites"
}

// MARK: - Helper Extensions

extension User {
    var displayName: String {
        return profile?.displayName ?? username
    }
    
    var hasPremiumFeatures: Bool {
        return isPremium
    }
    
    var canAddUnlimitedItems: Bool {
        return isPremium
    }
    
    var maxItems: Int {
        return isPremium ? Int.max : 100
    }
    
    var maxRecipes: Int {
        return isPremium ? Int.max : 50
    }
}

extension UserProfile {
    func hasDietaryTag(_ tag: DietaryTag) -> Bool {
        return dietaryTags.contains(tag.rawValue)
    }
    
    func hasAllergen(_ allergen: Allergen) -> Bool {
        return allergens.contains(allergen.rawValue)
    }
    
    func isFeatureEnabled(_ feature: String) -> Bool {
        return featureToggles[feature] ?? false
    }
}

// MARK: - Mock Data for Testing

extension User {
    static func mock() -> User {
        return User(
            id: UUID(),
            username: "testuser",
            email: "test@example.com",
            householdId: UUID(),
            isActive: true,
            isPremium: false,
            createdAt: Date(),
            updatedAt: Date(),
            profile: UserProfile.mock()
        )
    }
}

extension UserProfile {
    static func mock() -> UserProfile {
        return UserProfile(
            id: UUID(),
            userId: UUID(),
            displayName: "Test User",
            avatarUrl: nil,
            dietaryTags: ["vegetarian"],
            allergens: ["nuts"],
            preferences: ["theme": .string("dark")],
            featureToggles: ["ai_suggestions": true],
            createdAt: Date(),
            updatedAt: Date()
        )
    }
}