import SwiftUI

struct RecipeFormView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var recipeService: RecipeService
    
    @State private var name = ""
    @State private var description = ""
    @State private var difficulty = RecipeDifficulty.easy
    @State private var servings = "4"
    @State private var prepTime = "30"
    @State private var cookTime = "30"
    @State private var cuisine = ""
    @State private var instructions: [String] = [""]
    @State private var ingredients: [Ingredient] = []
    @State private var tags: [String] = []
    @State private var notes = ""
    @State private var source = ""
    
    var body: some View {
        Form {
            Section("Basic Information") {
                TextField("Recipe Name", text: $name)
                TextField("Description", text: $description, axis: .vertical)
                    .lineLimit(2...4)
                
                Picker("Difficulty", selection: $difficulty) {
                    ForEach(RecipeDifficulty.allCases, id: \.self) { difficulty in
                        Text(difficulty.rawValue).tag(difficulty)
                    }
                }
                
                HStack {
                    TextField("Servings", text: $servings)
                        .keyboardType(.numberPad)
                    Spacer()
                    Text("people")
                        .foregroundColor(.secondary)
                }
            }
            
            Section("Timing") {
                HStack {
                    TextField("Prep Time", text: $prepTime)
                        .keyboardType(.numberPad)
                    Spacer()
                    Text("minutes")
                        .foregroundColor(.secondary)
                }
                
                HStack {
                    TextField("Cook Time", text: $cookTime)
                        .keyboardType(.numberPad)
                    Spacer()
                    Text("minutes")
                        .foregroundColor(.secondary)
                }
                
                HStack {
                    Text("Total Time")
                    Spacer()
                    Text("\\(totalTime) minutes")
                        .foregroundColor(.secondary)
                }
            }
            
            Section("Details") {
                TextField("Cuisine (Optional)", text: $cuisine)
                TextField("Source (Optional)", text: $source)
            }
            
            Section("Ingredients") {
                ForEach(ingredients.indices, id: \.self) { index in
                    IngredientRow(ingredient: $ingredients[index]) {
                        ingredients.remove(at: index)
                    }
                }
                
                Button {
                    ingredients.append(Ingredient(
                        id: UUID(),
                        name: "",
                        quantity: "",
                        unit: "",
                        notes: nil,
                        isOptional: false
                    ))
                } label: {
                    Label("Add Ingredient", systemImage: "plus")
                }
            }
            
            Section("Instructions") {
                ForEach(instructions.indices, id: \.self) { index in
                    InstructionRow(
                        step: index + 1,
                        instruction: $instructions[index]
                    ) {
                        instructions.remove(at: index)
                    }
                }
                
                Button {
                    instructions.append("")
                } label: {
                    Label("Add Step", systemImage: "plus")
                }
            }
            
            Section("Notes") {
                TextField("Recipe notes...", text: $notes, axis: .vertical)
                    .lineLimit(3...6)
            }
        }
        .navigationTitle("Create Recipe")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Cancel") {
                    dismiss()
                }
            }
            
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Save") {
                    saveRecipe()
                }
                .disabled(!isFormValid)
            }
        }
    }
    
    private var totalTime: Int {
        (Int(prepTime) ?? 0) + (Int(cookTime) ?? 0)
    }
    
    private var isFormValid: Bool {
        !name.isEmpty && 
        !servings.isEmpty &&
        !prepTime.isEmpty &&
        !cookTime.isEmpty &&
        !ingredients.isEmpty &&
        !instructions.filter({ !$0.isEmpty }).isEmpty
    }
    
    private func saveRecipe() {
        let recipe = Recipe(
            id: UUID(),
            name: name,
            description: description.isEmpty ? nil : description,
            ingredients: ingredients,
            instructions: instructions.filter { !$0.isEmpty },
            cookTime: Int(cookTime) ?? 0,
            prepTime: Int(prepTime) ?? 0,
            totalTime: totalTime,
            servings: Int(servings) ?? 4,
            difficulty: difficulty.rawValue,
            cuisine: cuisine.isEmpty ? nil : cuisine,
            tags: tags.isEmpty ? nil : tags,
            nutrition: nil,
            imageUrl: nil,
            notes: notes.isEmpty ? nil : notes,
            source: source.isEmpty ? nil : source,
            isPublic: false,
            rating: nil,
            userId: AuthService.shared.currentUser?.id ?? UUID(),
            householdId: UUID(),
            syncStatus: "created",
            createdAt: Date(),
            updatedAt: Date(),
            reviews: nil
        )
        
        recipeService.createRecipe(recipe)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to create recipe: \(error)")
                    }
                },
                receiveValue: { _ in
                    dismiss()
                }
            )
            .store(in: &recipeService.cancellables)
    }
}

struct IngredientRow: View {
    @Binding var ingredient: Ingredient
    let onDelete: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                TextField("Quantity", text: Binding(
                    get: { ingredient.quantity },
                    set: { ingredient.quantity = $0 }
                ))
                .frame(width: 60)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                
                TextField("Unit", text: Binding(
                    get: { ingredient.unit },
                    set: { ingredient.unit = $0 }
                ))
                .frame(width: 60)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                
                TextField("Ingredient", text: Binding(
                    get: { ingredient.name },
                    set: { ingredient.name = $0 }
                ))
                .textFieldStyle(RoundedBorderTextFieldStyle())
            }
            
            HStack {
                Toggle("Optional", isOn: Binding(
                    get: { ingredient.isOptional },
                    set: { ingredient.isOptional = $0 }
                ))
                
                Spacer()
                
                Button(role: .destructive) {
                    onDelete()
                } label: {
                    Image(systemName: "trash")
                }
            }
            
            if !ingredient.isOptional {
                TextField("Notes (optional)", text: Binding(
                    get: { ingredient.notes ?? "" },
                    set: { ingredient.notes = $0.isEmpty ? nil : $0 }
                ))
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .font(.caption)
            }
        }
        .padding(.vertical, 4)
    }
}

struct InstructionRow: View {
    let step: Int
    @Binding var instruction: String
    let onDelete: () -> Void
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\\(step)")
                .font(.headline)
                .foregroundColor(.appPrimary)
                .frame(width: 24, height: 24)
                .background(Color.appPrimary.opacity(0.1))
                .cornerRadius(12)
                .padding(.top, 6)
            
            TextField("Enter instruction...", text: $instruction, axis: .vertical)
                .lineLimit(2...4)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            Button(role: .destructive) {
                onDelete()
            } label: {
                Image(systemName: "trash")
                    .padding(.top, 8)
            }
        }
        .padding(.vertical, 4)
    }
}

struct RecipeFormView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            RecipeFormView()
                .environmentObject(RecipeService.shared)
        }
    }
}