import SwiftUI

struct RecipeImportView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var recipeService: RecipeService
    
    @State private var url = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        Form {
            Section("Recipe URL") {
                TextField("https://example.com/recipe", text: $url)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                    .keyboardType(.URL)
            }
            
            Section("Supported Sites") {
                Text("We support recipes from popular cooking websites including AllRecipes, Food Network, Bon Appétit, and many more.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            if let errorMessage = errorMessage {
                Section {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                }
            }
        }
        .navigationTitle("Import Recipe")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Cancel") {
                    dismiss()
                }
            }
            
            ToolbarItem(placement: .navigationBarTrailing) {
                if isLoading {
                    ProgressView()
                } else {
                    Button("Import") {
                        importRecipe()
                    }
                    .disabled(url.isEmpty)
                }
            }
        }
    }
    
    private func importRecipe() {
        guard let recipeURL = URL(string: url), recipeURL.scheme != nil else {
            errorMessage = "Please enter a valid URL"
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        recipeService.importRecipe(from: url)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case .failure(let error) = completion {
                        errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { _ in
                    dismiss()
                }
            )
            .store(in: &recipeService.cancellables)
    }
}

struct RecipeImportView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            RecipeImportView()
                .environmentObject(RecipeService.shared)
        }
    }
}