import SwiftUI
import CoreData

struct RecipesView: View {
    @StateObject private var recipeService = RecipeService.shared
    @State private var searchText = ""
    @State private var selectedCuisine: String? = nil
    @State private var selectedDifficulty: String? = nil
    @State private var showingAddRecipe = false
    @State private var showingImportRecipe = false
    
    private let cuisines = ["All", "Italian", "Mexican", "Asian", "American", "Mediterranean", "Indian", "French"]
    private let difficulties = ["All"] + RecipeDifficulty.allCases.map { $0.rawValue }
    
    var filteredRecipes: [Recipe] {
        recipeService.searchRecipes(
            query: searchText,
            cuisine: selectedCuisine == "All" ? nil : selectedCuisine,
            difficulty: selectedDifficulty == "All" ? nil : selectedDifficulty
        )
    }
    
    var body: some View {
        NavigationView {
            VStack {
                if recipeService.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if filteredRecipes.isEmpty {
                    EmptyRecipesView()
                } else {
                    List {
                        ForEach(filteredRecipes) { recipe in
                            NavigationLink {
                                RecipeDetailView(recipe: recipe)
                            } label: {
                                RecipeRow(recipe: recipe)
                            }
                            .swipeActions(edge: .trailing) {
                                Button(role: .destructive) {
                                    deleteRecipe(recipe)
                                } label: {
                                    Label("Delete", systemImage: "trash")
                                }
                                
                                Button {
                                    editRecipe(recipe)
                                } label: {
                                    Label("Edit", systemImage: "pencil")
                                }
                                .tint(.blue)
                            }
                        }
                    }
                    .refreshable {
                        await syncRecipes()
                    }
                }
            }
            .navigationTitle("Recipes")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        Picker("Cuisine", selection: Binding(
                            get: { selectedCuisine ?? "All" },
                            set: { selectedCuisine = $0 == "All" ? nil : $0 }
                        )) {
                            ForEach(cuisines, id: \.self) { cuisine in
                                Text(cuisine).tag(cuisine)
                            }
                        }
                        
                        Picker("Difficulty", selection: Binding(
                            get: { selectedDifficulty ?? "All" },
                            set: { selectedDifficulty = $0 == "All" ? nil : $0 }
                        )) {
                            ForEach(difficulties, id: \.self) { difficulty in
                                Text(difficulty).tag(difficulty)
                            }
                        }
                    } label: {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button {
                            showingAddRecipe = true
                        } label: {
                            Label("Create Recipe", systemImage: "plus")
                        }
                        
                        Button {
                            showingImportRecipe = true
                        } label: {
                            Label("Import from URL", systemImage: "link")
                        }
                        
                        Button {
                            generateRecipe()
                        } label: {
                            Label("Generate with AI", systemImage: "wand.and.stars")
                        }
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .searchable(text: $searchText, placement: .automatic, prompt: "Search recipes...")
            .sheet(isPresented: $showingAddRecipe) {
                NavigationView {
                    RecipeFormView()
                }
            }
            .sheet(isPresented: $showingImportRecipe) {
                NavigationView {
                    RecipeImportView()
                }
            }
        }
    }
    
    private func deleteRecipe(_ recipe: Recipe) {
        recipeService.deleteRecipe(recipe)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to delete recipe: \(error)")
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &recipeService.cancellables)
    }
    
    private func editRecipe(_ recipe: Recipe) {
        showingAddRecipe = true
    }
    
    private func generateRecipe() {
        recipeService.generateRecipe(from: ["chicken", "rice", "vegetables"])
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to generate recipe: \(error)")
                    }
                },
                receiveValue: { recipe in
                    print("Generated recipe: \(recipe.name)")
                }
            )
            .store(in: &recipeService.cancellables)
    }
    
    private func syncRecipes() async {
        recipeService.syncRecipes()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to sync recipes: \(error)")
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &recipeService.cancellables)
    }
}

struct RecipeRow: View {
    let recipe: Recipe
    
    var body: some View {
        HStack(spacing: 12) {
            recipeImage
            
            VStack(alignment: .leading, spacing: 4) {
                Text(recipe.name)
                    .font(.headline)
                    .lineLimit(1)
                
                if let description = recipe.description {
                    Text(description)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                
                HStack {
                    Label("\\(recipe.totalTime) min", systemImage: "clock")
                        .font(.caption)
                    
                    Spacer()
                    
                    if let rating = recipe.rating, rating > 0 {
                        HStack(spacing: 2) {
                            Image(systemName: "star.fill")
                                .foregroundColor(.yellow)
                            Text(String(format: "%.1f", rating.doubleValue))
                                .font(.caption)
                        }
                    }
                    
                    Text(recipe.difficulty)
                        .font(.caption)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(difficultyColor)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                
                if let cuisine = recipe.cuisine {
                    Text(cuisine)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 8)
    }
    
    private var recipeImage: some View {
        Group {
            if let imageUrl = recipe.imageUrl, let url = URL(string: imageUrl) {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image.resizable()
                            .scaledToFill()
                    default:
                        Image(systemName: "fork.knife.circle")
                            .resizable()
                            .scaledToFit()
                            .foregroundColor(.gray)
                    }
                }
            } else {
                Image(systemName: "fork.knife.circle")
                    .resizable()
                    .scaledToFit()
                    .foregroundColor(.gray)
            }
        }
        .frame(width: 60, height: 60)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
    
    private var difficultyColor: Color {
        switch recipe.difficulty {
        case "Easy":
            return .green
        case "Medium":
            return .orange
        case "Hard":
            return .red
        default:
            return .gray
        }
    }
}

struct EmptyRecipesView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "book.closed")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))
            
            Text("No recipes yet")
                .font(.title2)
                .foregroundColor(.gray)
            
            Text("Create your first recipe or import one from the web")
                .font(.subheadline)
                .foregroundColor(.gray.opacity(0.8))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }
}

struct RecipesView_Previews: PreviewProvider {
    static var previews: some View {
        RecipesView()
            .environmentObject(RecipeService.shared)
    }
}