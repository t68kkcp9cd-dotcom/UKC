import SwiftUI

struct InventoryItemFormView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var inventoryService: InventoryService
    
    @State private var name = ""
    @State private var category = InventoryCategory.other
    @State private var quantity = "1"
    @State private var unit = ""
    @State private var location = InventoryLocation.pantry
    @State private var expiresAt: Date?
    @State private var price: String = ""
    @State private var barcode: String?
    @State private var notes = ""
    
    private let units = ["piece", "kg", "g", "lb", "oz", "l", "ml", "cup", "tbsp", "tsp"]
    
    var body: some View {
        Form {
            Section("Basic Information") {
                TextField("Item Name", text: $name)
                
                Picker("Category", selection: $category) {
                    ForEach(InventoryCategory.allCases, id: \.self) { category in
                        Text(category.rawValue).tag(category)
                    }
                }
                
                Picker("Location", selection: $location) {
                    ForEach(InventoryLocation.allCases, id: \.self) { location in
                        Text(location.rawValue).tag(location)
                    }
                }
            }
            
            Section("Quantity") {
                HStack {
                    TextField("Quantity", text: $quantity)
                        .keyboardType(.decimalPad)
                    
                    Picker("Unit", selection: $unit) {
                        ForEach(units, id: \.self) { unit in
                            Text(unit).tag(unit)
                        }
                    }
                    .pickerStyle(.menu)
                }
            }
            
            Section("Optional Details") {
                if let barcode = barcode {
                    HStack {
                        Text("Barcode")
                        Spacer()
                        Text(barcode)
                            .foregroundColor(.secondary)
                    }
                }
                
                DatePicker("Expires On", selection: Binding(
                    get: { expiresAt ?? Date().adding(days: 7) },
                    set: { expiresAt = $0 }
                ), displayedComponents: .date)
                
                TextField("Price", text: $price)
                    .keyboardType(.decimalPad)
                
                TextField("Notes", text: $notes, axis: .vertical)
                    .lineLimit(3...6)
            }
        }
        .navigationTitle("Add Item")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Cancel") {
                    dismiss()
                }
            }
            
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Save") {
                    saveItem()
                }
                .disabled(!isFormValid)
            }
        }
    }
    
    private var isFormValid: Bool {
        !name.isEmpty && !quantity.isEmpty && !unit.isEmpty
    }
    
    private func saveItem() {
        guard let quantityValue = Decimal(string: quantity),
              let priceValue = price.isEmpty ? nil : Decimal(string: price) else {
            return
        }
        
        let item = InventoryItem(
            id: UUID(),
            name: name,
            category: category.rawValue,
            quantity: quantityValue,
            unit: unit,
            location: location.rawValue,
            expiresAt: expiresAt,
            openedAt: nil,
            opened: false,
            barcode: barcode,
            price: priceValue,
            status: "active",
            imageUrl: nil,
            notes: notes.isEmpty ? nil : notes,
            nutritionalInfo: nil,
            userId: AuthService.shared.currentUser?.id ?? UUID(),
            householdId: UUID(),
            syncStatus: "created",
            createdAt: Date(),
            updatedAt: Date()
        )
        
        inventoryService.createItem(item)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to create item: \(error)")
                    }
                },
                receiveValue: { _ in
                    dismiss()
                }
            )
            .store(in: &inventoryService.cancellables)
    }
}

struct InventoryItemFormView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            InventoryItemFormView()
                .environmentObject(InventoryService.shared)
        }
    }
}