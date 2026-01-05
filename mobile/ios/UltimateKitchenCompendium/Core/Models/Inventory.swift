//
//  Inventory.swift
//  UltimateKitchenCompendium
//
//  Inventory and pantry management models
//

import Foundation
import CoreData
import UIKit

// MARK: - Domain Models

struct InventoryItem: Codable, Identifiable {
    let id: UUID
    let householdId: UUID
    var barcode: String?
    var name: String
    var category: String?
    var quantity: Double
    var unit: String
    var expirationDate: Date?
    var purchaseDate: Date?
    var purchasePrice: Double?
    var location: StorageLocation
    var nutritionData: [String: AnyCodable]?
    var priceHistory: [PriceHistoryEntry]
    let addedBy: UUID
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, name, category, quantity, unit
        case barcode = "barcode"
        case expirationDate = "expiration_date"
        case purchaseDate = "purchase_date"
        case purchasePrice = "purchase_price"
        case location
        case nutritionData = "nutrition_data"
        case priceHistory = "price_history"
        case addedBy = "added_by"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case householdId = "household_id"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(UUID.self, forKey: .id)
        householdId = try container.decode(UUID.self, forKey: .householdId)
        barcode = try container.decodeIfPresent(String.self, forKey: .barcode)
        name = try container.decode(String.self, forKey: .name)
        category = try container.decodeIfPresent(String.self, forKey: .category)
        quantity = try container.decode(Double.self, forKey: .quantity)
        unit = try container.decode(String.self, forKey: .unit)
        
        let expirationDateStr = try container.decodeIfPresent(String.self, forKey: .expirationDate)
        expirationDate = expirationDateStr != nil ? ISO8601DateFormatter().date(from: expirationDateStr!) : nil
        
        let purchaseDateStr = try container.decodeIfPresent(String.self, forKey: .purchaseDate)
        purchaseDate = purchaseDateStr != nil ? ISO8601DateFormatter().date(from: purchaseDateStr!) : nil
        
        purchasePrice = try container.decodeIfPresent(Double.self, forKey: .purchasePrice)
        
        let locationStr = try container.decode(String.self, forKey: .location)
        location = StorageLocation(rawValue: locationStr) ?? .pantry
        
        nutritionData = try container.decodeIfPresent([String: AnyCodable].self, forKey: .nutritionData)
        priceHistory = try container.decode([PriceHistoryEntry].self, forKey: .priceHistory)
        addedBy = try container.decode(UUID.self, forKey: .addedBy)
        createdAt = try container.decode(Date.self, forKey: .createdAt)
        updatedAt = try container.decode(Date.self, forKey: .updatedAt)
    }
}

struct PriceHistoryEntry: Codable {
    let date: Date
    let price: Double
    let store: String?
    
    enum CodingKeys: String, CodingKey {
        case date, price, store
    }
}

struct ConsumptionLog: Codable, Identifiable {
    let id: UUID
    let itemId: UUID
    let userId: UUID
    let quantityUsed: Double
    let usedAt: Date
    let wasteReason: WasteReason?
    
    enum CodingKeys: String, CodingKey {
        case id
        case itemId = "item_id"
        case userId = "user_id"
        case quantityUsed = "quantity_used"
        case usedAt = "used_at"
        case wasteReason = "waste_reason"
    }
}

enum StorageLocation: String, CaseIterable, Codable {
    case pantry = "pantry"
    case fridge = "fridge"
    case freezer = "freezer"
    case counter = "counter"
    case cupboard = "cupboard"
    
    var iconName: String {
        switch self {
        case .pantry: return "archivebox.fill"
        case .fridge: return "snowflake"
        case .freezer: return "thermometer.snowflake"
        case .counter: return "stove.fill"
        case .cupboard: return "cabinet.fill"
        }
    }
    
    var displayName: String {
        switch self {
        case .pantry: return "Pantry"
        case .fridge: return "Refrigerator"
        case .freezer: return "Freezer"
        case .counter: return "Counter"
        case .cupboard: return "Cupboard"
        }
    }
}

enum WasteReason: String, CaseIterable, Codable {
    case expired = "expired"
    case spoiled = "spoiled"
    case overbought = "overbought"
    case forgot = "forgot"
    case damaged = "damaged"
    case donated = "donated"
    
    var displayName: String {
        switch self {
        case .expired: return "Expired"
        case .spoiled: return "Spoiled"
        case .overbought: return "Overbought"
        case .forgot: return "Forgot"
        case .damaged: return "Damaged"
        case .donated: return "Donated"
        }
    }
}

enum ItemCategory: String, CaseIterable {
    case produce = "Produce"
    case dairy = "Dairy"
    case meat = "Meat & Seafood"
    case pantry = "Pantry"
    case frozen = "Frozen"
    case beverages = "Beverages"
    case snacks = "Snacks"
    case condiments = "Condiments"
    case baking = "Baking"
    case cleaning = "Cleaning"
    case other = "Other"
    
    var iconName: String {
        switch self {
        case .produce: return "leaf.fill"
        case .dairy: return "carton.fill"
        case .meat: return "fork.knife"
        case .pantry: return "archivebox.fill"
        case .frozen: return "snowflake"
        case .beverages: return "wineglass.fill"
        case .snacks: return "popcorn.fill"
        case .condiments: return "bottle.fill"
        case .baking: return "birthday.cake.fill"
        case .cleaning: return "spray.bottle.fill"
        case .other: return "questionmark.circle.fill"
        }
    }
}

// MARK: - Computed Properties

extension InventoryItem {
    var daysUntilExpiration: Int? {
        guard let expirationDate = expirationDate else { return nil }
        let calendar = Calendar.current
        let components = calendar.dateComponents([.day], from: Date(), to: expirationDate)
        return components.day
    }
    
    var isExpiringSoon: Bool {
        guard let days = daysUntilExpiration else { return false }
        return days <= 3 && days >= 0
    }
    
    var isExpired: Bool {
        guard let days = daysUntilExpiration else { return false }
        return days < 0
    }
    
    var displayQuantity: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.maximumFractionDigits = 2
        
        if let formattedQuantity = formatter.string(from: NSNumber(value: quantity)) {
            return "\(formattedQuantity) \(unit)"
        }
        return "\(quantity) \(unit)"
    }
    
    var displayPrice: String? {
        guard let price = purchasePrice else { return nil }
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        return formatter.string(from: NSNumber(value: price))
    }
}

// MARK: - Core Data Extensions

extension InventoryItem {
    @discardableResult
    func toCoreData(context: NSManagedObjectContext) -> InventoryItemEntity {
        let entity = InventoryItemEntity(context: context)
        entity.id = id
        entity.householdId = householdId
        entity.barcode = barcode
        entity.name = name
        entity.category = category
        entity.quantity = quantity
        entity.unit = unit
        entity.expirationDate = expirationDate
        entity.purchaseDate = purchaseDate
        entity.purchasePrice = purchasePrice ?? 0
        entity.location = location.rawValue
        entity.addedBy = addedBy
        entity.createdAt = createdAt
        entity.updatedAt = updatedAt
        entity.isSynced = true
        return entity
    }
}

extension InventoryItemEntity {
    func toDomain() -> InventoryItem {
        return InventoryItem(
            id: id ?? UUID(),
            householdId: householdId ?? UUID(),
            barcode: barcode,
            name: name ?? "",
            category: category,
            quantity: quantity,
            unit: unit ?? "piece",
            expirationDate: expirationDate,
            purchaseDate: purchaseDate,
            purchasePrice: purchasePrice > 0 ? purchasePrice : nil,
            location: StorageLocation(rawValue: location ?? "pantry") ?? .pantry,
            nutritionData: nil,
            priceHistory: [],
            addedBy: addedBy ?? UUID(),
            createdAt: createdAt ?? Date(),
            updatedAt: updatedAt ?? Date()
        )
    }
}

// MARK: - Barcode Lookup Response

struct BarcodeLookupResponse: Codable {
    let barcode: String
    let productName: String
    let brand: String?
    let category: String?
    let imageUrl: URL?
    let nutritionData: [String: AnyCodable]
    let allergens: [String]
    let ingredients: [String]
    let source: String
    
    enum CodingKeys: String, CodingKey {
        case barcode
        case productName = "product_name"
        case brand, category
        case imageUrl = "image_url"
        case nutritionData = "nutrition_data"
        case allergens, ingredients, source
    }
}

// MARK: - Mock Data

extension InventoryItem {
    static func mock() -> InventoryItem {
        return InventoryItem(
            id: UUID(),
            householdId: UUID(),
            barcode: "1234567890123",
            name: "Organic Tomatoes",
            category: "Produce",
            quantity: 5,
            unit: "pieces",
            expirationDate: Calendar.current.date(byAdding: .day, value: 3, to: Date()),
            purchaseDate: Date(),
            purchasePrice: 3.99,
            location: .fridge,
            nutritionData: nil,
            priceHistory: [],
            addedBy: UUID(),
            createdAt: Date(),
            updatedAt: Date()
        )
    }
}