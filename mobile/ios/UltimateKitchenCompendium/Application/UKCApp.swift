//
//  UKCApp.swift
//  UltimateKitchenCompendium
//
//  Main application entry point for Ultimate Kitchen Compendium
//

import SwiftUI
import CoreData

@main
struct UKCApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    
    let persistenceController = CoreDataStack.shared
    let appCoordinator = AppCoordinator()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appCoordinator)
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}

class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Initialize services
        ServiceLocator.shared.register(AuthService.self) { AuthServiceImpl() }
        ServiceLocator.shared.register(APIService.self) { APIServiceImpl() }
        ServiceLocator.shared.register(PersistenceService.self) { PersistenceServiceImpl() }
        ServiceLocator.shared.register(AIService.self) { AIServiceImpl() }
        
        // Setup notifications
        NotificationService.shared.requestPermission()
        
        // Initialize AI models if available
        Task {
            await AIInitializer.shared.initialize()
        }
        
        return true
    }
    
    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        let configuration = UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
        configuration.delegateClass = SceneDelegate.self
        return configuration
    }
}

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    
    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        
        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = UIHostingController(rootView: ContentView())
        self.window = window
        window.makeKeyAndVisible()
    }
}