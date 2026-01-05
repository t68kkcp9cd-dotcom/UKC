import SwiftUI

struct RecipeDetailView: View {
    let recipe: Recipe
    @State private var showingRating = false
    @State private var rating = 0.0
    @State private var reviewComment = ""
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                recipeHeader
                
                recipeInfo
                
                Divider()
                
                ingredientsSection
                
                Divider()
                
                instructionsSection
                
                if !recipe.notes.isEmpty {
                    Divider()
                    notesSection
                }
                
                if let nutrition = recipe.nutrition {
                    Divider()
                    nutritionSection(nutrition: nutrition)
                }
            }
            .padding()
        }
        .navigationTitle(recipe.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    showingRating = true
                } label: {
                    Image(systemName: "star")
                }
            }
        }
        .sheet(isPresented: $showingRating) {
            NavigationView {
                RecipeRatingView(recipe: recipe, rating: $rating, comment: $reviewComment)
            }
        }
    }
    
    private var recipeHeader: some View {
        VStack(alignment: .leading, spacing: 8) {
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
                .frame(maxWidth: .infinity)
                .frame(height: 200)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
            }
            
            Text(recipe.name)
                .font(.largeTitle)
                .fontWeight(.bold)
            
            if let description = recipe.description {
                Text(description)
                    .font(.body)
                    .foregroundColor(.secondary)
            }
        }
    }
    
    private var recipeInfo: some View {
        HStack(spacing: 20) {
            VStack {
                Image(systemName: "clock")
                Text("\\(recipe.totalTime) min")
                    .font(.caption)
            }
            
            VStack {
                Image(systemName: "person.2")
                Text("\\(recipe.servings) servings")
                    .font(.caption)
            }
            
            VStack {
                Image(systemName: "chart.bar")
                Text(recipe.difficulty)
                    .font(.caption)
            }
            
            if let rating = recipe.rating, rating > 0 {
                VStack {
                    Image(systemName: "star.fill")
                        .foregroundColor(.yellow)
                    Text(String(format: "%.1f", rating.doubleValue))
                        .font(.caption)
                }
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private var ingredientsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Ingredients")
                .font(.title2)
                .fontWeight(.bold)
            
            ForEach(recipe.ingredients) { ingredient in
                HStack(alignment: .top, spacing: 12) {
                    Circle()
                        .fill(Color.appPrimary)
                        .frame(width: 8, height: 8)
                        .padding(.top, 6)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\\(ingredient.quantity) \\(ingredient.unit) \\(ingredient.name)")
                            .font(.body)
                        
                        if let notes = ingredient.notes {
                            Text(notes)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        if ingredient.isOptional {
                            Text("Optional")
                                .font(.caption2)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.blue.opacity(0.1))
                                .foregroundColor(.blue)
                                .cornerRadius(8)
                        }
                    }
                    
                    Spacer()
                }
            }
        }
    }
    
    private var instructionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Instructions")
                .font(.title2)
                .fontWeight(.bold)
            
            ForEach(Array(recipe.instructions.enumerated()), id: \.offset) { index, instruction in
                HStack(alignment: .top, spacing: 12) {
                    Text("\\(index + 1)")
                        .font(.headline)
                        .foregroundColor(.appPrimary)
                        .frame(width: 24, height: 24)
                        .background(Color.appPrimary.opacity(0.1))
                        .cornerRadius(12)
                    
                    Text(instruction)
                        .font(.body)
                        .lineSpacing(4)
                    
                    Spacer()
                }
            }
        }
    }
    
    private var notesSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Notes")
                .font(.title2)
                .fontWeight(.bold)
            
            Text(recipe.notes)
                .font(.body)
                .lineSpacing(4)
        }
    }
    
    private func nutritionSection(nutrition: [String: String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Nutrition Information")
                .font(.title2)
                .fontWeight(.bold)
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ForEach(Array(nutrition.sorted(by: { $0.key < $1.key })), id: \.key) { key, value in
                    VStack {
                        Text(key)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(value)
                            .font(.headline)
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                }
            }
        }
    }
}

struct RecipeRatingView: View {
    let recipe: Recipe
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var recipeService: RecipeService
    
    @Binding var rating: Double
    @Binding var comment: String
    
    var body: some View {
        Form {
            Section("Rate this recipe") {
                VStack(alignment: .center, spacing: 20) {
                    Text(recipe.name)
                        .font(.headline)
                        .multilineTextAlignment(.center)
                    
                    HStack(spacing: 4) {
                        ForEach(1...5, id: \.self) { star in
                            Image(systemName: star <= Int(rating) ? "star.fill" : "star")
                                .font(.system(size: 30))
                                .foregroundColor(.yellow)
                                .onTapGesture {
                                    rating = Double(star)
                                }
                        }
                    }
                    
                    Text("\\(rating, specifier: "%.1f\") out of 5")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 20)
            }
            
            Section("Review (Optional)") {
                TextField("Share your thoughts...", text: $comment, axis: .vertical)
                    .lineLimit(3...6)
            }
        }
        .navigationTitle("Rate Recipe")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Cancel") {
                    dismiss()
                }
            }
            
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Submit") {
                    submitRating()
                }
                .disabled(rating == 0)
            }
        }
    }
    
    private func submitRating() {
        recipeService.rateRecipe(recipe.id, rating: Decimal(rating), comment: comment.isEmpty ? nil : comment)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to submit rating: \(error)")
                    }
                },
                receiveValue: { _ in
                    dismiss()
                }
            )
            .store(in: &recipeService.cancellables)
    }
}

struct RecipeDetailView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            RecipeDetailView(recipe: Recipe(
                id: UUID(),
                name: "Test Recipe",
                description: "A delicious test recipe",
                ingredients: [
                    Ingredient(id: UUID(), name: "Flour", quantity: "2", unit: "cups", notes: nil, isOptional: false),
                    Ingredient(id: UUID(), name: "Sugar", quantity: "1", unit: "cup", notes: nil, isOptional: false)
                ],
                instructions: ["Mix ingredients", "Bake at 350°F for 30 minutes"],
                cookTime: 30,
                prepTime: 15,
                totalTime: 45,
                servings: 4,
                difficulty: "Easy",
                cuisine: "American",
                tags: ["dessert", "baking"],
                nutrition: ["Calories": "250", "Protein": "5g"],
                imageUrl: nil,
                notes: "This is a test recipe for preview purposes",
                source: nil,
                isPublic: false,
                rating: Decimal(4.5),
                userId: UUID(),
                householdId: UUID(),
                syncStatus: "synced",
                createdAt: Date(),
                updatedAt: Date(),
                reviews: []
            ))
        }
    }
}