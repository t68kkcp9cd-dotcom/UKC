import Foundation
import CoreData
import Combine

class CoreDataManager {
    static let shared = CoreDataManager()
    
    private init() {}
    
    lazy var persistentContainer: NSPersistentCloudKitContainer = {
        let container = NSPersistentCloudKitContainer(name: "UltimateKitchenCompendium")
        
        container.loadPersistentStores { _, error in
            if let error = error as NSError? {
                fatalError("Unresolved error \(error), \(error.userInfo)")
            }
        }
        
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        
        return container
    }()
    
    var context: NSManagedObjectContext {
        return persistentContainer.viewContext
    }
    
    func saveContext() async throws {
        if context.hasChanges {
            try context.save()
        }
    }
    
    func delete(_ object: NSManagedObject) async throws {
        context.delete(object)
        try await saveContext()
    }
    
    func fetch<T: NSManagedObject>(_ type: T.Type, predicate: NSPredicate? = nil, sortDescriptors: [NSSortDescriptor]? = nil) async throws -> [T] {
        let request = T.fetchRequest()
        request.predicate = predicate
        request.sortDescriptors = sortDescriptors
        
        return try context.fetch(request) as? [T] ?? []
    }
    
    func syncEntities<T: NSManagedObject>(localEntities: [T], remoteEntities: [T], syncKey: String = "id") async throws {
        let localIds = Set(localEntities.compactMap { $0.value(forKey: syncKey) as? UUID })
        let remoteIds = Set(remoteEntities.compactMap { $0.value(forKey: syncKey) as? UUID })
        
        let idsToDelete = localIds.subtracting(remoteIds)
        let idsToAdd = remoteIds.subtracting(localIds)
        
        for entity in localEntities {
            if let id = entity.value(forKey: syncKey) as? UUID, idsToDelete.contains(id) {
                context.delete(entity)
            }
        }
        
        for entity in remoteEntities {
            if let id = entity.value(forKey: syncKey) as? UUID, idsToAdd.contains(id) {
                context.insert(entity)
            }
        }
        
        try await saveContext()
    }
}

@propertyWrapper
struct CoreDataContext: DynamicProperty {
    @Environment(\.managedObjectContext) var context
    
    var wrappedValue: NSManagedObjectContext {
        get { context }
    }
}