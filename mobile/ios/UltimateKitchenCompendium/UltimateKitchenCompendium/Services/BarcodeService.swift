import Foundation
import AVFoundation
import Vision
import Combine

class BarcodeService: ObservableObject {
    static let shared = BarcodeService()
    
    @Published var detectedBarcode: String?
    @Published var isScanning: Bool = false
    @Published var error: String?
    
    private var captureSession: AVCaptureSession?
    private var previewLayer: AVCaptureVideoPreviewLayer?
    
    func startScanning(previewView: UIView) -> AVCaptureVideoPreviewLayer? {
        isScanning = true
        error = nil
        
        guard let captureDevice = AVCaptureDevice.default(for: .video) else {
            error = "Camera not available"
            isScanning = false
            return nil
        }
        
        do {
            let input = try AVCaptureDeviceInput(device: captureDevice)
            let captureSession = AVCaptureSession()
            
            if captureSession.canAddInput(input) {
                captureSession.addInput(input)
            }
            
            let output = AVCaptureVideoDataOutput()
            output.setSampleBufferDelegate(self, queue: DispatchQueue(label: "videoQueue"))
            
            if captureSession.canAddOutput(output) {
                captureSession.addOutput(output)
            }
            
            let previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
            previewLayer.frame = previewView.bounds
            previewLayer.videoGravity = .resizeAspectFill
            
            previewView.layer.addSublayer(previewLayer)
            
            self.captureSession = captureSession
            self.previewLayer = previewLayer
            
            captureSession.startRunning()
            
            return previewLayer
        } catch {
            self.error = "Failed to setup camera: \(error.localizedDescription)"
            isScanning = false
            return nil
        }
    }
    
    func stopScanning() {
        captureSession?.stopRunning()
        captureSession = nil
        previewLayer?.removeFromSuperlayer()
        previewLayer = nil
        isScanning = false
        detectedBarcode = nil
    }
    
    func lookupBarcode(_ barcode: String) -> AnyPublisher<ProductInfo, APIError> {
        let parameters: [String: Any] = ["barcode": barcode]
        
        return APIService.shared.get("/barcode/lookup", parameters: parameters)
            .eraseToAnyPublisher()
    }
}

extension BarcodeService: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let requestHandler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up, options: [:])
        
        let request = VNDetectBarcodesRequest { [weak self] request, error in
            if let error = error {
                self?.error = "Barcode detection error: \(error.localizedDescription)"
                return
            }
            
            guard let results = request.results as? [VNBarcodeObservation], 
                  let firstResult = results.first,
                  let payload = firstResult.payloadStringValue else {
                return
            }
            
            DispatchQueue.main.async {
                self?.detectedBarcode = payload
                self?.stopScanning()
            }
        }
        
        do {
            try requestHandler.perform([request])
        } catch {
            self.error = "Failed to perform barcode detection: \(error.localizedDescription)"
        }
    }
}

struct ProductInfo: Codable {
    let name: String
    let brand: String?
    let category: String?
    let imageUrl: String?
    let nutritionalInfo: [String: String]?
    let description: String?
}