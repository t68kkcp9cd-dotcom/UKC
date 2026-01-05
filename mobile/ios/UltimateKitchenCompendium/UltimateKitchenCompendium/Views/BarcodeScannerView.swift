import SwiftUI
import AVFoundation
import Combine

struct BarcodeScannerView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var barcodeService: BarcodeService
    @EnvironmentObject var inventoryService: InventoryService
    
    @State private var showAddItem = false
    @State private var scannedProduct: ProductInfo?
    
    var body: some View {
        ZStack {
            CameraPreviewView()
                .edgesIgnoringSafeArea(.all)
            
            VStack {
                Spacer()
                
                Text("Position barcode within the frame")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(10)
                
                Spacer()
                
                if let barcode = barcodeService.detectedBarcode {
                    VStack {
                        Text("Scanned: \(barcode)")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.green.opacity(0.8))
                            .cornerRadius(10)
                            .padding(.bottom, 20)
                        
                        if let product = scannedProduct {
                            Text(product.name)
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.blue.opacity(0.8))
                                .cornerRadius(10)
                                .padding(.bottom, 20)
                        }
                        
                        HStack(spacing: 20) {
                            Button("Cancel") {
                                barcodeService.stopScanning()
                                dismiss()
                            }
                            .padding()
                            .background(Color.gray.opacity(0.8))
                            .foregroundColor(.white)
                            .cornerRadius(10)
                            
                            Button("Add Item") {
                                showAddItem = true
                            }
                            .padding()
                            .background(Color.appPrimary)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                        .padding(.bottom, 40)
                    }
                } else {
                    Button("Cancel") {
                        barcodeService.stopScanning()
                        dismiss()
                    }
                    .padding()
                    .background(Color.gray.opacity(0.8))
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .padding(.bottom, 40)
                }
            }
            .padding()
        }
        .onAppear {
            barcodeService.startScanning()
        }
        .onDisappear {
            barcodeService.stopScanning()
        }
        .onReceive(Just(barcodeService.detectedBarcode)) { barcode in
            if let barcode = barcode, scannedProduct == nil {
                lookupProduct(barcode: barcode)
            }
        }
        .sheet(isPresented: $showAddItem) {
            NavigationView {
                InventoryItemFormView(barcode: barcodeService.detectedBarcode)
            }
        }
    }
    
    private func lookupProduct(barcode: String) {
        barcodeService.lookupBarcode(barcode)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to lookup product: \(error)")
                    }
                },
                receiveValue: { product in
                    scannedProduct = product
                }
            )
            .store(in: &barcodeService.cancellables)
    }
}

struct CameraPreviewView: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let view = UIView()
        
        DispatchQueue.main.async {
            if let layer = BarcodeService.shared.startScanning(previewView: view) {
                view.layer.addSublayer(layer)
            }
        }
        
        return view
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {
    }
}

struct BarcodeScannerView_Previews: PreviewProvider {
    static var previews: some View {
        BarcodeScannerView()
            .environmentObject(BarcodeService.shared)
            .environmentObject(InventoryService.shared)
    }
}