import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authService: AuthService
    
    var body: some View {
        Group {
            if authService.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
    }
}

struct MainTabView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            InventoryView()
                .tabItem {
                    Image(systemName: "cube.box.fill")
                    Text("Inventory")
                }
                .tag(0)
            
            RecipesView()
                .tabItem {
                    Image(systemName: "book.closed.fill")
                    Text("Recipes")
                }
                .tag(1)
            
            MealPlanningView()
                .tabItem {
                    Image(systemName: "calendar")
                    Text("Meal Plans")
                }
                .tag(2)
            
            ShoppingListsView()
                .tabItem {
                    Image(systemName: "list.bullet.rectangle")
                    Text("Shopping")
                }
                .tag(3)
            
            SettingsView()
                .tabItem {
                    Image(systemName: "gear")
                    Text("Settings")
                }
                .tag(4)
        }
        .accentColor(.appPrimary)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AuthService.shared)
    }
}