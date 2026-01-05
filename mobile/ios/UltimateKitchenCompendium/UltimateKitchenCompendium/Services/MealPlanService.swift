import Foundation
import Combine
import CoreData

class MealPlanService: ObservableObject {
    static let shared = MealPlanService()
    
    @Published var mealPlans: [MealPlan] = []
    @Published var isLoading: Bool = false
    @Published var lastSyncDate: Date?
    
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        loadLocalMealPlans()
    }
    
    func loadLocalMealPlans() {
        Task { @MainActor in
            do {
                let localMealPlans = try await CoreDataManager.shared.fetch(CDMealPlan.self)
                self.mealPlans = localMealPlans.map { $0.toMealPlan() }
            } catch {
                print("Failed to load local meal plans: \(error)")
            }
        }
    }
    
    func syncMealPlans() -> AnyPublisher<Void, APIError> {
        isLoading = true
        
        let unsyncedMealPlans = mealPlans.filter { $0.syncStatus != "synced" }
        
        var publishers: [AnyPublisher<Void, APIError>] = []
        
        for mealPlan in unsyncedMealPlans {
            switch mealPlan.syncStatus {
            case "created":
                publishers.append(createMealPlanOnServer(mealPlan))
            case "updated":
                publishers.append(updateMealPlanOnServer(mealPlan))
            case "deleted":
                publishers.append(deleteMealPlanOnServer(mealPlan))
            default:
                break
            }
        }
        
        publishers.append(fetchMealPlansFromServer())
        
        return Publishers.MergeMany(publishers)
            .collect()
            .map { _ in () }
            .handleEvents(receiveCompletion: { [weak self] _ in
                self?.isLoading = false
                self?.lastSyncDate = Date()
            })
            .eraseToAnyPublisher()
    }
    
    func createMealPlan(_ mealPlan: MealPlan) -> AnyPublisher<MealPlan, APIError> {
        var newMealPlan = mealPlan
        newMealPlan.syncStatus = "created"
        
        return APIService.shared.post("/meal-plans", parameters: newMealPlan.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdMealPlan: MealPlan) in
                self?.updateLocalMealPlan(createdMealPlan)
            })
            .eraseToAnyPublisher()
    }
    
    func updateMealPlan(_ mealPlan: MealPlan) -> AnyPublisher<MealPlan, APIError> {
        var updatedMealPlan = mealPlan
        updatedMealPlan.syncStatus = "updated"
        
        return APIService.shared.put("/meal-plans/\(mealPlan.id)", parameters: updatedMealPlan.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedMealPlan: MealPlan) in
                self?.updateLocalMealPlan(updatedMealPlan)
            })
            .eraseToAnyPublisher()
    }
    
    func deleteMealPlan(_ mealPlan: MealPlan) -> AnyPublisher<Void, APIError> {
        if mealPlan.syncStatus == "created" {
            removeLocalMealPlan(mealPlan)
            return Just(()).setFailureType(to: APIError.self).eraseToAnyPublisher()
        } else {
            var deletedMealPlan = mealPlan
            deletedMealPlan.syncStatus = "deleted"
            
            return APIService.shared.delete("/meal-plans/\(mealPlan.id)")
                .handleEvents(receiveOutput: { [weak self] _ in
                    self?.removeLocalMealPlan(mealPlan)
                })
                .eraseToAnyPublisher()
        }
    }
    
    func createMealPlanEntry(_ entry: MealPlanEntry) -> AnyPublisher<MealPlanEntry, APIError> {
        var newEntry = entry
        newEntry.syncStatus = "created"
        
        return APIService.shared.post("/meal-plans/\(entry.mealPlanId)/entries", parameters: newEntry.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdEntry: MealPlanEntry) in
                self?.updateLocalMealPlanEntry(createdEntry)
            })
            .eraseToAnyPublisher()
    }
    
    func updateMealPlanEntry(_ entry: MealPlanEntry) -> AnyPublisher<MealPlanEntry, APIError> {
        var updatedEntry = entry
        updatedEntry.syncStatus = "updated"
        
        return APIService.shared.put("/meal-plans/\(entry.mealPlanId)/entries/\(entry.id)", parameters: updatedEntry.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedEntry: MealPlanEntry) in
                self?.updateLocalMealPlanEntry(updatedEntry)
            })
            .eraseToAnyPublisher()
    }
    
    func deleteMealPlanEntry(_ entry: MealPlanEntry) -> AnyPublisher<Void, APIError> {
        if entry.syncStatus == "created" {
            removeLocalMealPlanEntry(entry)
            return Just(()).setFailureType(to: APIError.self).eraseToAnyPublisher()
        } else {
            return APIService.shared.delete("/meal-plans/\(entry.mealPlanId)/entries/\(entry.id)")
                .handleEvents(receiveOutput: { [weak self] _ in
                    self?.removeLocalMealPlanEntry(entry)
                })
                .eraseToAnyPublisher()
        }
    }
    
    func generateMealPlan(startDate: Date, endDate: Date, preferences: [String: Any]?) -> AnyPublisher<MealPlan, APIError> {
        var parameters: [String: Any] = [
            "start_date": ISO8601DateFormatter().string(from: startDate),
            "end_date": ISO8601DateFormatter().string(from: endDate)
        ]
        
        if let preferences = preferences {
            parameters["preferences"] = preferences
        }
        
        return APIService.shared.post("/ai/meal-plans/generate", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (mealPlan: MealPlan) in
                self?.updateLocalMealPlan(mealPlan)
            })
            .eraseToAnyPublisher()
    }
    
    func getMealPlanForWeek(starting date: Date) -> MealPlan? {
        let weekStart = date.startOfWeek()
        let weekEnd = date.endOfWeek()
        
        return mealPlans.first { mealPlan in
            let mealPlanStart = mealPlan.startDate
            let mealPlanEnd = mealPlan.endDate
            
            return (mealPlanStart...mealPlanEnd).overlaps(weekStart...weekEnd) && mealPlan.syncStatus != "deleted"
        }
    }
    
    func getMealPlanEntries(for date: Date) -> [MealPlanEntry] {
        let calendar = Calendar.current
        let dayStart = calendar.startOfDay(for: date)
        let dayEnd = calendar.date(byAdding: .day, value: 1, to: dayStart) ?? date
        
        var entries: [MealPlanEntry] = []
        
        for mealPlan in mealPlans {
            let planEntries = mealPlan.entries?.filter { entry in
                entry.date >= dayStart && entry.date < dayEnd && entry.syncStatus != "deleted"
            } ?? []
            entries.append(contentsOf: planEntries)
        }
        
        return entries.sorted { $0.mealType < $1.mealType }
    }
    
    private func createMealPlanOnServer(_ mealPlan: MealPlan) -> AnyPublisher<Void, APIError> {
        return APIService.shared.post("/meal-plans", parameters: mealPlan.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (createdMealPlan: MealPlan) in
                self?.updateLocalMealPlan(createdMealPlan)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateMealPlanOnServer(_ mealPlan: MealPlan) -> AnyPublisher<Void, APIError> {
        return APIService.shared.put("/meal-plans/\(mealPlan.id)", parameters: mealPlan.toDictionary())
            .handleEvents(receiveOutput: { [weak self] (updatedMealPlan: MealPlan) in
                self?.updateLocalMealPlan(updatedMealPlan)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func deleteMealPlanOnServer(_ mealPlan: MealPlan) -> AnyPublisher<Void, APIError> {
        return APIService.shared.delete("/meal-plans/\(mealPlan.id)")
            .handleEvents(receiveOutput: { [weak self] _ in
                self?.removeLocalMealPlan(mealPlan)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func fetchMealPlansFromServer() -> AnyPublisher<Void, APIError> {
        var parameters: [String: Any] = [:]
        if let lastSync = lastSyncDate {
            parameters["updated_after"] = ISO8601DateFormatter().string(from: lastSync)
        }
        
        return APIService.shared.get("/meal-plans", parameters: parameters)
            .handleEvents(receiveOutput: { [weak self] (response: PaginatedResponse<MealPlan>) in
                self?.mergeServerMealPlans(response.items)
            })
            .map { _ in () }
            .eraseToAnyPublisher()
    }
    
    private func updateLocalMealPlan(_ mealPlan: MealPlan) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDMealPlan> = CDMealPlan.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", mealPlan.id as CVarArg)
                
                if let existingMealPlan = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    existingMealPlan.update(from: mealPlan)
                } else {
                    let newMealPlan = CDMealPlan(context: CoreDataManager.shared.context)
                    newMealPlan.update(from: mealPlan)
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalMealPlans()
            } catch {
                print("Failed to update local meal plan: \(error)")
            }
        }
    }
    
    private func removeLocalMealPlan(_ mealPlan: MealPlan) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDMealPlan> = CDMealPlan.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", mealPlan.id as CVarArg)
                
                if let existingMealPlan = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    try await CoreDataManager.shared.delete(existingMealPlan)
                    loadLocalMealPlans()
                }
            } catch {
                print("Failed to remove local meal plan: \(error)")
            }
        }
    }
    
    private func updateLocalMealPlanEntry(_ entry: MealPlanEntry) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDMealPlanEntry> = CDMealPlanEntry.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", entry.id as CVarArg)
                
                if let existingEntry = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    existingEntry.update(from: entry)
                } else {
                    let newEntry = CDMealPlanEntry(context: CoreDataManager.shared.context)
                    newEntry.update(from: entry)
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalMealPlans()
            } catch {
                print("Failed to update local meal plan entry: \(error)")
            }
        }
    }
    
    private func removeLocalMealPlanEntry(_ entry: MealPlanEntry) {
        Task { @MainActor in
            do {
                let fetchRequest: NSFetchRequest<CDMealPlanEntry> = CDMealPlanEntry.fetchRequest()
                fetchRequest.predicate = NSPredicate(format: "id == %@", entry.id as CVarArg)
                
                if let existingEntry = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                    try await CoreDataManager.shared.delete(existingEntry)
                    loadLocalMealPlans()
                }
            } catch {
                print("Failed to remove local meal plan entry: \(error)")
            }
        }
    }
    
    private func mergeServerMealPlans(_ serverMealPlans: [MealPlan]) {
        Task { @MainActor in
            do {
                let localMealPlans = try await CoreDataManager.shared.fetch(CDMealPlan.self)
                
                for serverMealPlan in serverMealPlans {
                    let fetchRequest: NSFetchRequest<CDMealPlan> = CDMealPlan.fetchRequest()
                    fetchRequest.predicate = NSPredicate(format: "id == %@", serverMealPlan.id as CVarArg)
                    
                    if let localMealPlan = try CoreDataManager.shared.context.fetch(fetchRequest).first {
                        localMealPlan.update(from: serverMealPlan)
                    } else {
                        let newMealPlan = CDMealPlan(context: CoreDataManager.shared.context)
                        newMealPlan.update(from: serverMealPlan)
                    }
                }
                
                try await CoreDataManager.shared.saveContext()
                loadLocalMealPlans()
            } catch {
                print("Failed to merge server meal plans: \(error)")
            }
        }
    }
}

extension MealPlan {
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "name": name,
            "start_date": ISO8601DateFormatter().string(from: startDate),
            "end_date": ISO8601DateFormatter().string(from: endDate),
            "user_id": userId.uuidString,
            "household_id": householdId.uuidString,
            "sync_status": syncStatus
        ]
        
        dict["created_at"] = ISO8601DateFormatter().string(from: createdAt)
        dict["updated_at"] = ISO8601DateFormatter().string(from: updatedAt)
        
        return dict
    }
}

extension MealPlanEntry {
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "date": ISO8601DateFormatter().string(from: date),
            "meal_type": mealType,
            "servings": servings,
            "meal_plan_id": mealPlanId.uuidString,
            "sync_status": syncStatus
        ]
        
        if let notes = notes {
            dict["notes"] = notes
        }
        
        if let recipeId = recipeId {
            dict["recipe_id"] = recipeId.uuidString
        }
        
        dict["created_at"] = ISO8601DateFormatter().string(from: createdAt)
        dict["updated_at"] = ISO8601DateFormatter().string(from: updatedAt)
        
        return dict
    }
}