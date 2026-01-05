import Foundation
import Combine
import CoreData

class ShoppingListService: ObservableObject {
    static let shared = ShoppingListService()
    
    @Published var shoppingLists: [ShoppingList] = []
    @Published var isLoading: Bool = false
    @Published var lastSyncDate: Date?
    
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        loadLocalShoppingLists()
    }
    
    func loadLocalShoppingLists() {
        Task { @MainActor in
            do {
                let localLists = try await CoreDataManager.shared.fetch(CDShoppingList.self)
                self.shoppingLists = localLists.map { $0.toShoppingList() }
            } catch {
                print("Failed to load local shopping lists: \(error)")
            }
        }
    }
    
    func syncShoppingLists() -> AnyPublisher<Void, APIError> {
        isLoading = true
        
        let unsyncedLists = shoppingLists.filter { $0.syncStatus != "synced" }
        
        var publishers: [AnyPublisher<Void, APIError>] = []
        
        for list in unsyncedLists {
            switch list.syncStatus {
            case "created":
                publishers.append(createShoppingListOnServer(list))
            case "updated":
                publishers.append(updateShoppingListOnServer(list))
            case "deleted":
                publishers.append(deleteShoppingListOnServer(list))
            default:
                break
            }
        }
        
        publishers.append(fetchShoppingListsFromServer())
        
        return Publishers.MergeMany(publishers)
            .collect()
            .map { _ in () }
            .handleEvents(receiveCompletion: { [weak self] _ in
                self?.isLoading = false
                self?.lastSyncDate = Date()
            })
            .eraseToAnyPublisher()
    }
    
    func createShoppingList(_ list: ShoppingList) -> AnyPublisher<ShoppingList, APIError> {
        var newList = list
        newList.syncStatus = "created"
        
        return APIService.shared.post("/shopping-lists", parameters: newList.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdList: ShoppingList) in
                self?.updateLocalShoppingList(createdList)
            })
            .eraseToAnyPublisher()
    }
    
    func updateShoppingList(_ list: ShoppingList) -> AnyPublisher<ShoppingList, APIError> {
        var updatedList = list
        updatedList.syncStatus = "updated"
        
        return APIService.shared.put("/shopping-lists/\(list.id)", parameters: updatedList.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedList: ShoppingList) in
                self?.updateLocalShoppingList(updatedList)
            })
            .eraseToAnyPublisher()
    }
    
    func deleteShoppingList(_ list: ShoppingList) -> AnyPublisher<Void, APIError> {
        if list.syncStatus == "created" {
            removeLocalShoppingList(list)
            return Just(()).setFailureType(to: APIError.self).eraseToAnyPublisher()
        } else {
            var deletedList = list
            deletedList.syncStatus = "deleted"
            
            return APIService.shared.delete("/shopping-lists/\(list.id)")
                .handleEvents(receiveOutput: { [weak self] _ in
                    self?.removeLocalShoppingList(list)
                })
                .eraseToAnyPublisher()
        }
    }
    
    func createShoppingItem(_ item: ShoppingItem) -> AnyPublisher<ShoppingItem, APIError> {
        var newItem = item
        newItem.syncStatus = "created"
        
        return APIService.shared.post("/shopping-lists/\(item.shoppingListId)/items", parameters: newItem.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdItem: ShoppingItem) in
                self?.updateLocalShoppingItem(createdItem)
            })
            .eraseToAnyPublisher()
    }
    
    func updateShoppingItem(_ item: ShoppingItem) -> AnyPublisher<ShoppingItem, APIError> {
        var updatedItem = item
        updatedItem.syncStatus = "updated"
        
        return APIService.shared.put("/shopping-lists/\(item.shoppingListId)/items/\(item.id)", parameters: updatedItem.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedItem: ShoppingItem) in
                self?.updateLocalShoppingItem(updatedItem)
            })
            .eraseToAnyPublisher()
    }
    
    func deleteShoppingItem(_ item: ShoppingItem) -> AnyPublisher<Void, APIError> {
        if item.syncStatus == "created" {
            removeLocalShoppingItem(item)
            return Just(()).setFailureType(to: APIError.self).eraseToAnyPublisher()
        } else {
            return APIService.shared.delete("/shopping-lists/\(item.shoppingListId)/items/\(item.id)")
                .handleEvents(receiveOutput: { [weak self] _ in
                    self?.removeLocalShoppingItem(item)
                })
                .eraseToAnyPublisher()
        }
    }
    
    func generateShoppingList(fromMealPlan mealPlanId: UUID) -> AnyPublisher<ShoppingList, APIError> {
        let parameters: [String: Any] = ["meal_plan_id": mealPlanId.uuidString]
        
        return APIService.shared.post("/shopping-lists/generate", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (shoppingList: ShoppingList) in
                self?.updateLocalShoppingList(shoppingList)
            })
            .eraseToAnyPublisher()
    }
    
    func searchShoppingItems(query: String, category: String? = nil) -> [ShoppingItem] {
        var allItems: [ShoppingItem] = []
        
        for list in shoppingLists {
            if let items = list.items {
                allItems.append(contentsOf: items)
            }
        }
        
        return allItems.filter { item in
            let matchesQuery = query.isEmpty || item.name.localizedCaseInsensitiveContains(query)
            let matchesCategory = category == nil || item.category == category
            
            return matchesQuery && matchesCategory && item.syncStatus != "deleted"
        }
    }
    
    func getCompletedItems(for listId: UUID) -> [ShoppingItem] {
        guard let list = shoppingLists.first(where: { $0.id == listId }),
              let items = list.items else {
            return []
        }
        
        return items.filter { $0.completed && $0.syncStatus != "deleted" }
    }
    
    func getPendingItems(for listId: UUID) -> [ShoppingItem] {
        guard let list = shoppingLists.first(where: { $0.id == listId }),
              let items = list.items else {
            return []
        }
        
        return items.filter { !$0.completed && $0.syncStatus != "deleted" }
            .sorted { $0.category < $1.category }
    }
    
    private func createShoppingListOnServer(_ list: ShoppingList) -> AnyPublisher<Void, APIError> {
        return APIService.shared.post("/shopping-lists", parameters: list.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdList: ShoppingList) in
                self?.updateLocalShoppingList(createdList)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateShoppingListOnServer(_ list: ShoppingList) -> AnyPublisher<Void, APIError> {
        return APIService.shared.put("/shopping-lists/\(list.id)", parameters: list.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedList: ShoppingList) in
                self?.updateLocalShoppingList(updatedList)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func deleteShoppingListOnServer(_ list: ShoppingList) -> AnyPublisher<Void, APIError> {
        return APIService.shared.delete("/shopping-lists/\(list.id)")
            .handleEvents(receiveOutput: { [weak self] _ in
                self?.removeLocalShoppingList(list)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func fetchShoppingListsFromServer() -> AnyPublisher<Void, APIError> {
        var parameters: [String: Any] = [:]
        if let lastSync = lastSyncDate {
            parameters["updated_after"] = ISO8601DateFormatter().string(from: lastSync)
        }
        
        return APIService.shared.get("/shopping-lists", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (response: PaginatedResponse<ShoppingList>) in
                self?.mergeServerShoppingLists(response.items)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateLocalShoppingList(_ list: ShoppingList) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDShoppingList> = CDShoppingList.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", list.id as CVarArg)
                
                if let existingList = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    existingList.update(from: list)
                } else {
                    let newList = CDShoppingList(context: CoreDataManager.shared.context)
                    newList.update(from: list)
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalShoppingLists()
            } catch {
                print("Failed to update local shopping list: \(error)")
            }
        }
    }
    
    private func removeLocalShoppingList(_ list: ShoppingList) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDShoppingList> = CDShoppingList.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", list.id as CVarArg)
                
                if let existingList = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    try await CoreDataManager.shared.delete(existingList)
                    loadLocalShoppingLists()
                }
            } catch {
                print("Failed to remove local shopping list: \(error)")
            }
        }
    }
    
    private func updateLocalShoppingItem(_ item: ShoppingItem) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDShoppingItem> = CDShoppingItem.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", item.id as CVarArg)
                
                if let existingItem = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    existingItem.update(from: item)
                } else {
                    let newItem = CDShoppingItem(context: CoreDataManager.shared.context)
                    newItem.update(from: item)
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalShoppingLists()
            } catch {
                print("Failed to update local shopping item: \(error)")
            }
        }
    }
    
    private func removeLocalShoppingItem(_ item: ShoppingItem) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDShoppingItem> = CDShoppingItem.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", item.id as CVarArg)
                
                if let existingItem = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    try await CoreDataManager.shared.delete(existingItem)
                    loadLocalShoppingLists()
                }
            } catch {
                print("Failed to remove local shopping item: \(error)")
            }
        }
    }
    
    private func mergeServerShoppingLists(_ serverLists: [ShoppingList]) {
        Task { @MainActor in
            do {
                let localLists = try await CoreDataManager.shared.fetch(CDShoppingList.self)
                
                for serverList in serverLists {
                    let fetchRequest: NSFetchRequest<CDShoppingList> = CDShoppingList.fetchRequest()
                    fetchRequest.predicate = NSPredicate(format: "id == %@", serverList.id as CVarArg)
                    
                    if let localList = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                        localList.update(from: serverList)
                    } else {
                        let newList = CDShoppingList(context: CoreDataManager.shared.context)
                        newList.update(from: serverList)
                    }
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalShoppingLists()
            } catch {
                print("Failed to merge server shopping lists: \(error)")
            }
        }
    }
}

extension ShoppingList {
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "name": name,
            "user_id": userId.uuidString,
            "household_id": householdId.uuidString,
            "sync_status": syncStatus
        ]
        
        dict["created_at"] = ISO8601DateFormatter().string(from: createdAt)
        dict["updated_at"] = ISO8601DateFormatter().string(from: updatedAt)
        
        return dict
    }
}

extension ShoppingItem {
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "name": name,
            "category": category,
            "quantity": quantity.doubleValue,
            "unit": unit,
            "completed": completed,
            "user_id": userId.uuidString,
            "shopping_list_id": shoppingListId.uuidString,
            "sync_status": syncStatus
        ]
        
        if let price = price {
            dict["price"] = price.doubleValue
        }
        
        if let notes = notes {
            dict["notes"] = notes
        }
        
        dict["created_at"] = ISO8601DateFormatter().string(from: createdAt)
        dict["updated_at"] = ISO8601DateFormatter().string(from: updatedAt)
        
        return dict
    }
}