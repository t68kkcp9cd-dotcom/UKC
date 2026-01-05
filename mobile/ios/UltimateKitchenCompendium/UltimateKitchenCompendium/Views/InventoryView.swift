import SwiftUI
import CoreData

struct InventoryView: View {
    @StateObject private var inventoryService = InventoryService.shared
    @State private var showingAddItem = false
    @State private var showingBarcodeScanner = false
    @State private var searchText = ""
    @State private var selectedCategory = "All"
    @State private var selectedLocation = "All"
    
    private let categories = ["All"] + InventoryCategory.allCases.map { $0.rawValue }
    private let locations = ["All"] + InventoryLocation.allCases.map { $0.rawValue }
    
    var filteredItems: [InventoryItem] {
        inventoryService.searchItems(
            query: searchText,
            category: selectedCategory == "All" ? nil : selectedCategory,
            location: selectedLocation == "All" ? nil : selectedLocation
        )
    }
    
    var body: some View {
        NavigationView {
            VStack {
                if inventoryService.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if filteredItems.isEmpty {
                    EmptyInventoryView()
                } else {
                    List {
                        ForEach(filteredItems) { item in
                            InventoryItemRow(item: item)
                                .swipeActions(edge: .trailing) {
                                    Button(role: .destructive) {
                                        deleteItem(item)
                                    } label: {
                                        Label("Delete", systemImage: "trash")
                                    }
                                    
                                    Button {
                                        editItem(item)
                                    } label: {
                                        Label("Edit", systemImage: "pencil")
                                    }
                                    .tint(.blue)
                                }
                                .contextMenu {
                                    Button {
                                        toggleOpened(item)
                                    } label: {
                                        Label(item.opened ? "Mark Unopened" : "Mark Opened", 
                                              systemImage: item.opened ? "seal" : "seal.open")
                                    }
                                }
                        }
                    }
                    .refreshable {
                        await syncInventory()
                    }
                }
            }
            .navigationTitle("Inventory")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        Picker("Category", selection: $selectedCategory) {
                            ForEach(categories, id: \.self) { category in
                                Text(category).tag(category)
                            }
                        }
                        
                        Picker("Location", selection: $selectedLocation) {
                            ForEach(locations, id: \.self) { location in
                                Text(location).tag(location)
                            }
                        }
                    } label: {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    HStack {
                        Button {
                            showingBarcodeScanner = true
                        } label: {
                            Image(systemName: "barcode.viewfinder")
                        }
                        
                        Button {
                            showingAddItem = true
                        } label: {
                            Image(systemName: "plus")
                        }
                    }
                }
            }
            .searchable(text: $searchText, placement: .automatic, prompt: "Search inventory...")
            .sheet(isPresented: $showingAddItem) {
                NavigationView {
                    InventoryItemFormView()
                }
            }
            .sheet(isPresented: $showingBarcodeScanner) {
                NavigationView {
                    BarcodeScannerView()
                }
            }
        }
    }
    
    private func deleteItem(_ item: InventoryItem) {
        inventoryService.deleteItem(item)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to delete item: \(error)")
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &inventoryService.cancellables)
    }
    
    private func editItem(_ item: InventoryItem) {
        showingAddItem = true
    }
    
    private func toggleOpened(_ item: InventoryItem) {
        var updatedItem = item
        updatedItem.opened = !item.opened
        updatedItem.openedAt = !item.opened ? Date() : nil
        
        inventoryService.updateItem(updatedItem)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to update item: \(error)")
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &inventoryService.cancellables)
    }
    
    private func syncInventory() async {
        inventoryService.syncItems()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to sync inventory: \(error)")
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &inventoryService.cancellables)
    }
}

struct InventoryItemRow: View {
    let item: InventoryItem
    
    var body: some View {
        HStack(spacing: 12) {
            itemStatusIndicator
            
            VStack(alignment: .leading, spacing: 4) {
                Text(item.name)
                    .font(.headline)
                    .lineLimit(1)
                
                HStack {
                    Text("\\(item.quantity.formattedString()) \\(item.unit)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text(item.location)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.appPrimary.opacity(0.1))
                        .foregroundColor(.appPrimary)
                        .cornerRadius(8)
                }
                
                if let expiresAt = item.expiresAt {
                    Text("Expires: \(expiresAt.formatted(date: .abbreviated, time: .omitted))")
                        .font(.caption)
                        .foregroundColor(item.isExpired ? .red : item.isExpiringSoon ? .orange : .secondary)
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 8)
    }
    
    private var itemStatusIndicator: some View {
        Group {
            if item.isExpired {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(.red)
            } else if item.isExpiringSoon {
                Image(systemName: "clock.badge.exclamationmark")
                    .foregroundColor(.orange)
            } else if item.opened {
                Image(systemName: "seal.open")
                    .foregroundColor(.blue)
            } else {
                Image(systemName: "cube.box.fill")
                    .foregroundColor(.green)
            }
        }
        .font(.title2)
    }
}

struct EmptyInventoryView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "cube.box")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))
            
            Text("Your pantry is empty")
                .font(.title2)
                .foregroundColor(.gray)
            
            Text("Add your first item to start tracking your inventory")
                .font(.subheadline)
                .foregroundColor(.gray.opacity(0.8))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }
}

struct InventoryView_Previews: PreviewProvider {
    static var previews: some View {
        InventoryView()
            .environmentObject(InventoryService.shared)
    }
}