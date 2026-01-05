# Ultimate Kitchen Compendium - Android App

## Project Structure

```
UltimateKitchenCompendium/
├── app/src/main/java/com/ukc/
│   ├── MainActivity.kt             # Entry point
│   ├── UKCApplication.kt           # Application class
│   ├── di/                         # Dependency injection
│   │   ├── AppModule.kt
│   │   └── NetworkModule.kt
│   ├── data/                       # Data layer
│   │   ├── models/
│   │   ├── repository/
│   │   ├── local/
│   │   └── remote/
│   ├── domain/                     # Domain layer
│   │   ├── entities/
│   │   ├── usecases/
│   │   └── repository/
│   ├── presentation/               # UI layer
│   │   ├── navigation/
│   │   ├── theme/
│   │   ├── components/
│   │   └── features/
│   │       ├── auth/
│   │       ├── inventory/
│   │       ├── recipes/
│   │       ├── mealplanning/
│   │       ├── shopping/
│   │       └── settings/
│   └── utils/                      # Utilities
├── build.gradle.kts
└── settings.gradle.kts
```

## Setup Instructions

1. **Prerequisites**
   - Android Studio Hedgehog (2023.1.1) or later
   - JDK 17+
   - Android SDK 34+
   - Kotlin 1.9+

2. **Clone and Setup**
   ```bash
   cd mobile/android
   ./gradlew build
   ```

3. **Configuration**
   - Copy `local.properties.template` to `local.properties`
   - Update API endpoint URLs
   - Configure signing keys

4. **Build and Run**
   - Open project in Android Studio
   - Select target device/emulator
   - Build and run (Shift+F10)

## Key Features Implementation

### 1. CameraX Barcode Scanning
```kotlin
@Composable
fun BarcodeScannerScreen(
    onBarcodeScanned: (String) -> Unit,
    onError: (Throwable) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    
    AndroidView(
        factory = { ctx ->
            PreviewView(ctx).apply {
                implementationMode = PreviewView.ImplementationMode.COMPATIBLE
                scaleType = PreviewView.ScaleType.FILL_CENTER
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}
```

### 2. Offline-First Architecture with Room
```kotlin
@Entity(tableName = "inventory_items")
data class InventoryItemEntity(
    @PrimaryKey val id: String,
    val name: String,
    val barcode: String?,
    val quantity: Double,
    val unit: String,
    val expirationDate: LocalDate?,
    val location: String,
    val isSynced: Boolean = false
)
```

### 3. Voice-Guided Cooking
```kotlin
class VoiceGuidedCookingViewModel(
    private val textToSpeech: TextToSpeech,
    private val speechRecognizer: SpeechRecognizer
) : ViewModel() {
    
    var currentStep by mutableStateOf(0)
    var isListening by mutableStateOf(false)
    var isSpeaking by mutableStateOf(false)
    
    fun startVoiceGuidance(recipe: Recipe) {
        speakCurrentStep()
        startVoiceRecognition()
    }
}
```

## Dependencies

### Build.gradle.kts (Module: app)
```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.1")
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")
    
    // Dependency Injection
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Local Storage
    implementation("androidx.room:room-runtime:2.6.0")
    implementation("androidx.room:room-ktx:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")
    
    // Camera
    implementation("androidx.camera:camera-core:1.3.0")
    implementation("androidx.camera:camera-camera2:1.3.0")
    implementation("androidx.camera:camera-lifecycle:1.3.0")
    implementation("androidx.camera:camera-view:1.3.0")
    
    // ML Kit
    implementation("com.google.mlkit:barcode-scanning:17.2.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    
    // Security
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    
    // Billing (Premium unlock)
    implementation("com.android.billingclient:billing-ktx:6.1.0")
}
```

## Build Configuration

### Debug
- Application ID: `com.yourcompany.ukc.dev`
- API Base URL: `http://localhost:8000`
- Debuggable: true

### Release
- Application ID: `com.yourcompany.ukc`
- API Base URL: `https://your-domain.com`
- Debuggable: false
- ProGuard optimization enabled

## Testing

```bash
# Run unit tests
./gradlew test

# Run instrumentation tests
./gradlew connectedAndroidTest

# Run lint
./gradlew lint
```

## Google Play Store Submission

1. Update version code and name in `build.gradle.kts`
2. Configure app icons and feature graphic
3. Update store listing metadata
4. Build signed APK/AAB
5. Upload to Play Console
6. Submit for review

## Premium Features Unlock

The app uses Google Play Billing Library:
- Product ID: `ukc_premium_unlock`
- Type: Managed product (one-time purchase)
- Price: $19.99 (configurable in Play Console)

## ProGuard Rules

```proguard
# Keep model classes
-keep class com.ukc.data.models.** { *; }

# Keep API service interfaces
-keep interface com.ukc.data.remote.** { *; }

# Keep serialization
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes InnerClasses
-keepattributes EnclosingMethod
```

## Performance Optimization

- **R8/ProGuard**: Code shrinking and optimization
- **App Bundle**: Upload AAB for smaller downloads
- **Baseline Profiles**: Optimize startup performance
- **Lazy Loading**: Load features on demand