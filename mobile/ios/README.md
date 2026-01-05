# Ultimate Kitchen Compendium - iOS App

## Project Structure

```
UltimateKitchenCompendium/
├── Application/
│   ├── UKCApp.swift                    # Main app entry
│   ├── AppDelegate.swift               # Background processing
│   └── SceneDelegate.swift             # Multi-window support
├── Core/
│   ├── Models/                         # Data models
│   │   ├── User.swift
│   │   ├── InventoryItem.swift
│   │   ├── Recipe.swift
│   │   └── ShoppingList.swift
│   ├── Services/                       # Business logic
│   │   ├── APIService.swift
│   │   ├── AuthService.swift
│   │   ├── PersistenceService.swift
│   │   └── AIService.swift
│   ├── Utils/                          # Utilities
│   │   ├── Constants.swift
│   │   ├── Extensions.swift
│   │   └── Validators.swift
│   └── Coordinators/                   # Navigation
│       ├── AppCoordinator.swift
│       └── TabCoordinator.swift
├── Features/
│   ├── Authentication/
│   ├── Inventory/
│   ├── Recipes/
│   ├── MealPlanning/
│   ├── Shopping/
│   └── Settings/
├── UI/
│   ├── Components/                     # Reusable UI
│   │   ├── BarcodeScannerView.swift
│   │   ├── VoiceInputView.swift
│   │   └── LoadingView.swift
│   ├── Themes/                         # Design system
│   │   ├── Colors.swift
│   │   ├── Fonts.swift
│   │   └── Styles.swift
│   └── Resources/                      # Assets, strings
└── Persistence/                        # Core Data
    ├── CoreDataStack.swift
    ├── Entities/
    └── Migrations/
```

## Setup Instructions

1. **Prerequisites**
   - macOS 14.0+
   - Xcode 15.0+
   - iOS 16.0+ deployment target
   - Swift 5.9+

2. **Clone and Setup**
   ```bash
   cd mobile/ios
   pod install  # If using CocoaPods
   ```

3. **Configuration**
   - Copy `Config.template.xcconfig` to `Config.xcconfig`
   - Update API endpoint URLs
   - Configure app bundle identifier

4. **Build and Run**
   - Open `UltimateKitchenCompendium.xcworkspace` in Xcode
   - Select target device/simulator
   - Build and run (⌘+R)

## Key Features Implementation

### 1. Barcode Scanning
```swift
import AVFoundation
import Vision

class BarcodeScannerViewModel: ObservableObject {
    @Published var scannedCode: String?
    @Published var isScanning = false
    
    func handleBarcodeDetection(request: VNRequest, error: Error?) {
        guard let results = request.results as? [VNBarcodeObservation],
              let payload = results.first?.payloadStringValue else { return }
        
        scannedCode = payload
        lookupProduct(barcode: payload)
    }
}
```

### 2. Offline Support with Core Data
```swift
class PersistenceService {
    static let shared = PersistenceService()
    
    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "UKCModel")
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Core Data failed: \(error)")
            }
        }
        return container
    }()
}
```

### 3. Voice-Guided Cooking
```swift
import AVFoundation
import Speech

class VoiceGuidedCookingViewModel: ObservableObject {
    @Published var currentStep: Int = 0
    @Published var isListening = false
    @Published var isSpeaking = false
    
    func startVoiceGuidance(recipe: Recipe) {
        speakCurrentStep()
        startListening()
    }
}
```

## Dependencies

- **Alamofire**: HTTP networking
- **SwiftKeychainWrapper**: Secure storage
- **SDWebImage**: Image loading and caching
- **Starscream**: WebSocket client
- **Combine**: Reactive programming

## Build Configuration

### Development
- Bundle ID: `com.yourcompany.ukc.dev`
- API Base URL: `http://localhost:8000`

### Production
- Bundle ID: `com.yourcompany.ukc`
- API Base URL: `https://your-domain.com`

## Testing

```bash
# Run unit tests
xcodebuild test -scheme UltimateKitchenCompendium -destination 'platform=iOS Simulator,name=iPhone 15'

# Run UI tests
xcodebuild test -scheme UltimateKitchenCompendiumUITests
```

## App Store Submission

1. Update version number in `Info.plist`
2. Configure app icons and launch screen
3. Update app store metadata
4. Archive and upload to App Store Connect
5. Submit for review

## Premium Features Unlock

The app uses StoreKit for in-app purchases:
- Product ID: `ukc.premium.unlock`
- Type: Non-consumable
- Price: $19.99 (configurable in App Store Connect)