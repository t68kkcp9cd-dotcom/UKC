import SwiftUI
import CoreData

struct MealPlanningView: View {
    @StateObject private var mealPlanService = MealPlanService.shared
    @State private var selectedDate = Date()
    @State private var showingCreatePlan = false
    @State private var showingGeneratePlan = false
    
    private let calendar = Calendar.current
    private let daysInWeek = 7
    
    var weekDates: [Date] {
        let startOfWeek = selectedDate.startOfWeek()
        return (0..<daysInWeek).map { startOfWeek.adding(days: $0) }
    }
    
    var currentMealPlan: MealPlan? {
        mealPlanService.getMealPlanForWeek(starting: selectedDate)
    }
    
    var body: some View {
        NavigationView {
            VStack {
                weekSelector
                
                if mealPlanService.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let mealPlan = currentMealPlan {
                    mealPlanView(mealPlan: mealPlan)
                } else {
                    EmptyMealPlanView()
                }
            }
            .navigationTitle("Meal Planning")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button {
                            showingCreatePlan = true
                        } label: {
                            Label("Create Plan", systemImage: "plus")
                        }
                        
                        Button {
                            showingGeneratePlan = true
                        } label: {
                            Label("Generate with AI", systemImage: "wand.and.stars")
                        }
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingCreatePlan) {
                NavigationView {
                    MealPlanFormView()
                }
            }
            .sheet(isPresented: $showingGeneratePlan) {
                NavigationView {
                    MealPlanGeneratorView()
                }
            }
        }
    }
    
    private var weekSelector: some View {
        VStack {
            HStack {
                Button {
                    selectedDate = calendar.date(byAdding: .weekOfYear, value: -1, to: selectedDate) ?? selectedDate
                } label: {
                    Image(systemName: "chevron.left")
                }
                
                Spacer()
                
                Text("Week of \(selectedDate.startOfWeek().formatted(date: .abbreviated, time: .omitted))")
                    .font(.headline)
                
                Spacer()
                
                Button {
                    selectedDate = calendar.date(byAdding: .weekOfYear, value: 1, to: selectedDate) ?? selectedDate
                } label: {
                    Image(systemName: "chevron.right")
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(weekDates, id: \.self) { date in
                        DayView(
                            date: date,
                            isSelected: calendar.isDate(date, inSameDayAs: selectedDate),
                            entries: mealPlanService.getMealPlanEntries(for: date)
                        )
                        .onTapGesture {
                            selectedDate = date
                        }
                    }
                }
                .padding(.horizontal)
            }
        }
        .background(Color(.systemBackground))
    }
    
    private func mealPlanView(mealPlan: MealPlan) -> some View {
        ScrollView {
            VStack(spacing: 16) {
                ForEach(MealType.allCases, id: \.self) { mealType in
                    if let entries = mealPlan.entries?.filter({ $0.mealType == mealType.rawValue.lowercased() }) {
                        MealSection(
                            mealType: mealType,
                            entries: entries,
                            selectedDate: selectedDate
                        )
                    }
                }
            }
            .padding()
        }
        .refreshable {
            await syncMealPlans()
        }
    }
    
    private func syncMealPlans() async {
        mealPlanService.syncMealPlans()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to sync meal plans: \(error)")
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &mealPlanService.cancellables)
    }
}

struct DayView: View {
    let date: Date
    let isSelected: Bool
    let entries: [MealPlanEntry]
    
    var body: some View {
        VStack(spacing: 4) {
            Text(date.formatted(.dateTime.weekday()))
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(date.formatted(.dateTime.day()))
                .font(.title2)
                .fontWeight(.bold)
            
            if !entries.isEmpty {
                HStack(spacing: 2) {
                    ForEach(0..<min(entries.count, 3), id: \.self) { _ in
                        Circle()
                            .fill(Color.appPrimary)
                            .frame(width: 4, height: 4)
                    }
                }
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(isSelected ? Color.appPrimary : Color(.systemBackground))
        )
        .foregroundColor(isSelected ? .white : .primary)
    }
}

struct MealSection: View {
    let mealType: MealType
    let entries: [MealPlanEntry]
    let selectedDate: Date
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(mealType.rawValue)
                    .font(.headline)
                    .textCase(.uppercase)
                
                Spacer()
                
                Button {
                    
                } label: {
                    Image(systemName: "plus.circle")
                }
            }
            .padding(.horizontal)
            
            if entries.isEmpty {
                Text("No meals planned")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .padding(.horizontal)
                    .padding(.vertical, 20)
                    .frame(maxWidth: .infinity)
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
            } else {
                ForEach(entries) { entry in
                    MealPlanEntryRow(entry: entry)
                }
            }
        }
    }
}

struct MealPlanEntryRow: View {
    let entry: MealPlanEntry
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                if let recipe = entry.recipe {
                    Text(recipe.name)
                        .font(.headline)
                    
                    HStack {
                        Text("\\(recipe.totalTime) min")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text("•")
                            .foregroundColor(.secondary)
                        
                        Text("\\(entry.servings) servings")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                } else {
                    Text("Meal")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
                
                if let notes = entry.notes, !notes.isEmpty {
                    Text(notes)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            if let recipe = entry.recipe {
                NavigationLink {
                    RecipeDetailView(recipe: recipe)
                } label: {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 1)
    }
}

struct EmptyMealPlanView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "calendar.badge.plus")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))
            
            Text("No meal plan for this week")
                .font(.title2)
                .foregroundColor(.gray)
            
            Text("Create a meal plan to start organizing your meals")
                .font(.subheadline)
                .foregroundColor(.gray.opacity(0.8))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }
}

struct MealPlanningView_Previews: PreviewProvider {
    static var previews: some View {
        MealPlanningView()
            .environmentObject(MealPlanService.shared)
    }
}