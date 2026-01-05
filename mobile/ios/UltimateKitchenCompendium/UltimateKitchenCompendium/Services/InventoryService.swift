import Foundation
import Combine
import CoreData

class InventoryService: ObservableObject {
    static let shared = InventoryService()
    
    @Published var items: [InventoryItem] = []
    @Published var isLoading: Bool = false
    @Published var lastSyncDate: Date?
    
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        loadLocalItems()
    }
    
    func loadLocalItems() {
        Task { @MainActor in
            do {
                let localItems = try await CoreDataManager.shared.fetch(CDInventoryItem.self)
                self.items = localItems.map { $0.toInventoryItem() }
            } catch {
                print("Failed to load local items: \(error)")
            }
        }
    }
    
    func syncItems() -> AnyPublisher<Void, APIError> {
        isLoading = true
        
        let unsyncedItems = items.filter { $0.syncStatus != "synced" }
        
        var publishers: [AnyPublisher<Void, APIError>] = []
        
        for item in unsyncedItems {
            switch item.syncStatus {
            case "created":
                publishers.append(createItemOnServer(item))
            case "updated":
                publishers.append(updateItemOnServer(item))
            case "deleted":
                publishers.append(deleteItemOnServer(item))
            default:
                break
            }
        }
        
        publishers.append(fetchItemsFromServer())
        
        return Publishers.MergeMany(publishers)
            .collect()
            .map { _ in () }
            .handleEvents(receiveCompletion: { [weak self] _ in
                self?.isLoading = false
                self?.lastSyncDate = Date()
            })
            .eraseToAnyPublisher()
    }
    
    func createItem(_ item: InventoryItem) -> AnyPublisher<InventoryItem, APIError> {
        var newItem = item
        newItem.syncStatus = "created"
        
        return APIService.shared.post("/inventory", parameters: newItem.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdItem: InventoryItem) in
                self?.updateLocalItem(createdItem)
            })
            .eraseToAnyPublisher()
    }
    
    func updateItem(_ item: InventoryItem) -> AnyPublisher<InventoryItem, APIError> {
        var updatedItem = item
        updatedItem.syncStatus = "updated"
        
        return APIService.shared.put("/inventory/\(item.id)", parameters: updatedItem.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedItem: InventoryItem) in
                self?.updateLocalItem(updatedItem)
            })
            .eraseToAnyPublisher()
    }
    
    func deleteItem(_ item: InventoryItem) -> AnyPublisher<Void, APIError> {
        if item.syncStatus == "created" {
            removeLocalItem(item)
            return Just(()).setFailureType(to: APIError.self).eraseToAnyPublisher()
        } else {
            var deletedItem = item
            deletedItem.syncStatus = "deleted"
            
            return APIService.shared.delete("/inventory/\(item.id)")
                .handleEvents(receiveOutput: { [weak self] _ in
                    self?.removeLocalItem(item)
                })
                .eraseToAnyPublisher()
        }
    }
    
    func searchItems(query: String, category: String? = nil, location: String? = nil) -> [InventoryItem] {
        return items.filter { item in
            let matchesQuery = query.isEmpty || item.name.localizedCaseInsensitiveContains(query)
            let matchesCategory = category == nil || item.category == category
            let matchesLocation = location == nil || item.location == location
            
            return matchesQuery && matchesCategory && matchesLocation && item.syncStatus != "deleted"
        }
    }
    
    func getExpiringItems(days: Int = 7) -> [InventoryItem] {
        let upcomingDate = Calendar.current.date(byAdding: .day, value: days, to: Date()) ?? Date()
        
        return items.filter { item in
            guard let expiresAt = item.expiresAt else { return false }
            return expiresAt <= upcomingDate && expiresAt > Date() && item.syncStatus != "deleted"
        }
        .sorted { ($0.expiresAt ?? Date()) < ($1.expiresAt ?? Date()) }
    }
    
    func getLowStockItems(minimumQuantity: Decimal = 1.0) -> [InventoryItem] {
        return items.filter { $0.quantity < minimumQuantity && $0.syncStatus != "deleted" }
    }
    
    private func createItemOnServer(_ item: InventoryItem) -> AnyPublisher<Void, APIError> {
        return APIService.shared.post("/inventory", parameters: item.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdItem: InventoryItem) in
                self?.updateLocalItem(createdItem)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateItemOnServer(_ item: InventoryItem) -> AnyPublisher<Void, APIError> {
        return APIService.shared.put("/inventory/\(item.id)", parameters: item.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedItem: InventoryItem) in
                self?.updateLocalItem(updatedItem)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func deleteItemOnServer(_ item: InventoryItem) -> AnyPublisher<Void, APIError> {
        return APIService.shared.delete("/inventory/\(item.id)")
            .handleEvents(receiveOutput: { [weak self] _ in
                self?.removeLocalItem(item)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func fetchItemsFromServer() -> AnyPublisher<Void, APIError> {
        var parameters: [String: Any] = [:]
        if let lastSync = lastSyncDate {
            parameters["updated_after"] = ISO8601DateFormatter().string(from: lastSync)
        }
        
        return APIService.shared.get("/inventory", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (response: PaginatedResponse<InventoryItem>) in
                self?.mergeServerItems(response.items)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateLocalItem(_ item: InventoryItem) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDInventoryItem> = CDInventoryItem.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", item.id as CVarArg)
                
                if let existingItem = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    existingItem.update(from: item)
                } else {
                    let newItem = CDInventoryItem(context: CoreDataManager.shared.context)
                    newItem.update(from: item)
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalItems()
            } catch {
                print("Failed to update local item: \(error)")
            }
        }
    }
    
    private func removeLocalItem(_ item: InventoryItem) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDInventoryItem> = CDInventoryItem.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", item.id as CVarArg)
                
                if let existingItem = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    try await CoreDataManager.shared.delete(existingItem)
                    loadLocalItems()
                }
            } catch {
                print("Failed to remove local item: \(error)")
            }
        }
    }
    
    private func mergeServerItems(_ serverItems: [InventoryItem]) {
        Task { @MainActor in
            do {
                let localItems = try await CoreDataManager.shared.fetch(CDInventoryItem.self)
                
                for serverItem in serverItems {
                    let fetchRequest: NSFetchRequest<CDInventoryItem> = CDInventoryItem.fetchRequest()
                    fetchRequest.predicate = NSPredicate(format: "id == %@", serverItem.id as CVarArg)
                    
                    if let localItem = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                        localItem.update(from: serverItem)
                    } else {
                        let newItem = CDInventoryItem(context: CoreDataManager.shared.context)
                        newItem.update(from: serverItem)
                    }
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalItems()
            } catch {
                print("Failed to merge server items: \(error)")
            }
        }
    }
}

extension InventoryItem {
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "name": name,
            "category": category,
            "quantity": quantity.doubleValue,
            "unit": unit,
            "location": location,
            "opened": opened,
            "status": status,
            "user_id": userId.uuidString,
            "household_id": householdId.uuidString,
            "sync_status": syncStatus
        ]
        
        if let expiresAt = expiresAt {
            dict["expires_at"] = ISO8601DateFormatter().string(from: expiresAt)
        }
        
        if let openedAt = openedAt {
            dict["opened_at"] = ISO8601DateFormatter().string(from: openedAt)
        }
        
        if let barcode = barcode {
            dict["barcode"] = barcode
        }
        
        if let price = price {
            dict["price"] = price.doubleValue
        }
        
        if let imageUrl = imageUrl {
            dict["image_url"] = imageUrl
        }
        
        if let notes = notes {
            dict["notes"] = notes
        }
        
        if let nutritionalInfo = nutritionalInfo {
            dict["nutritional_info"] = nutritionalInfo
        }
        
        dict["created_at"] = ISO8601DateFormatter().string(from: createdAt)
        dict["updated_at"] = ISO8601DateFormatter().string(from: updatedAt)
        
        return dict
    }
}