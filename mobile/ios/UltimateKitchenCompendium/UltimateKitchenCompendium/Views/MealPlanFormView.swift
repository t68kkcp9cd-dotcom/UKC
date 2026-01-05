import SwiftUI

struct MealPlanFormView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var mealPlanService: MealPlanService
    
    @State private var name = ""
    @State private var startDate = Date()
    @State private var endDate = Date().adding(days: 7)
    
    var body: some View {
        Form {
            Section("Plan Details") {
                TextField("Meal Plan Name", text: $name)
                
                DatePicker("Start Date", selection: $startDate, displayedComponents: .date)
                DatePicker("End Date", selection: $endDate, displayedComponents: .date)
            }
            
            Section {
                Button("Create Plan") {
                    createMealPlan()
                }
                .frame(maxWidth: .infinity)
            }
        }
        .navigationTitle("Create Meal Plan")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Cancel") {
                    dismiss()
                }
            }
        }
    }
    
    private func createMealPlan() {
        let mealPlan = MealPlan(
            id: UUID(),
            name: name,
            startDate: startDate,
            endDate: endDate,
            userId: AuthService.shared.currentUser?.id ?? UUID(),
            householdId: UUID(),
            syncStatus: "created",
            createdAt: Date(),
            updatedAt: Date(),
            entries: []
        )
        
        mealPlanService.createMealPlan(mealPlan)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to create meal plan: \(error)")
                    }
                },
                receiveValue: { _ in
                    dismiss()
                }
            )
            .store(in: &mealPlanService.cancellables)
    }
}

struct MealPlanGeneratorView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var mealPlanService: MealPlanService
    
    @State private var startDate = Date()
    @State private var endDate = Date().adding(days: 7)
    @State private var preferences: [String] = []
    @State private var dietaryRestrictions = ""
    @State private var budget = ""
    
    var body: some View {
        Form {
            Section("Date Range") {
                DatePicker("Start Date", selection: $startDate, displayedComponents: .date)
                DatePicker("End Date", selection: $endDate, displayedComponents: .date)
            }
            
            Section("Preferences") {
                TextField("Dietary Restrictions", text: $dietaryRestrictions)
                TextField("Budget (Optional)", text: $budget)
                    .keyboardType(.decimalPad)
            }
            
            Section {
                Button("Generate Meal Plan") {
                    generateMealPlan()
                }
                .frame(maxWidth: .infinity)
            }
        }
        .navigationTitle("Generate Meal Plan")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Cancel") {
                    dismiss()
                }
            }
        }
    }
    
    private func generateMealPlan() {
        var prefs: [String: Any] = [:]
        
        if !dietaryRestrictions.isEmpty {
            prefs["dietary_restrictions"] = dietaryRestrictions
        }
        
        if !budget.isEmpty, let budgetValue = Decimal(string: budget) {
            prefs["budget"] = budgetValue
        }
        
        mealPlanService.generateMealPlan(startDate: startDate, endDate: endDate, preferences: prefs)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to generate meal plan: \(error)")
                    }
                },
                receiveValue: { _ in
                    dismiss()
                }
            )
            .store(in: &mealPlanService.cancellables)
    }
}

struct MealPlanFormView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            MealPlanFormView()
                .environmentObject(MealPlanService.shared)
        }
    }
}

struct MealPlanGeneratorView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            MealPlanGeneratorView()
                .environmentObject(MealPlanService.shared)
        }
    }
}