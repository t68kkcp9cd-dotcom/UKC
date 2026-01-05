package com.ukc.data.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.annotations.SerializedName
import kotlinx.serialization.Serializable
import java.util.*

@Serializable
@Entity(tableName = "users")
data class User(
    @PrimaryKey
    val id: String,
    val username: String,
    val email: String,
    @SerializedName("household_id")
    val householdId: String?,
    @SerializedName("is_active")
    val isActive: Boolean,
    @SerializedName("is_premium")
    val isPremium: Boolean,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String,
    val profile: UserProfile? = null
) {
    val displayName: String
        get() = profile?.displayName ?: username
    
    val hasPremiumFeatures: Boolean
        get() = isPremium
    
    val maxItems: Int
        get() = if (isPremium) Int.MAX_VALUE else 100
    
    val maxRecipes: Int
        get() = if (isPremium) Int.MAX_VALUE else 50
}

@Serializable
data class UserProfile(
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("display_name")
    val displayName: String?,
    @SerializedName("avatar_url")
    val avatarUrl: String?,
    @SerializedName("dietary_tags")
    val dietaryTags: List<String>,
    val allergens: List<String>,
    val preferences: Map<String, Any>,
    @SerializedName("feature_toggles")
    val featureToggles: Map<String, Boolean>,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String
) {
    fun hasDietaryTag(tag: DietaryTag): Boolean = dietaryTags.contains(tag.name)
    
    fun hasAllergen(allergen: Allergen): Boolean = allergens.contains(allergen.name)
    
    fun isFeatureEnabled(feature: String): Boolean = featureToggles[feature] ?: false
}

@Serializable
data class Household(
    val id: String,
    val name: String,
    @SerializedName("owner_id")
    val ownerId: String,
    @SerializedName("created_at")
    val createdAt: String
)

@Serializable
data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("refresh_token")
    val refreshToken: String?,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("expires_in")
    val expiresIn: Int,
    val user: User
)

@Serializable
data class LoginRequest(
    val username: String,
    val password: String
)

@Serializable
data class RegisterRequest(
    val username: String,
    val email: String,
    val password: String,
    @SerializedName("household_id")
    val householdId: String?
)

// Dietary preferences and restrictions
enum class DietaryTag(val name: String) {
    VEGETARIAN("vegetarian"),
    VEGAN("vegan"),
    GLUTEN_FREE("gluten-free"),
    DAIRY_FREE("dairy-free"),
    KETO("keto"),
    PALEO("paleo"),
    LOW_CARB("low-carb"),
    LOW_SODIUM("low-sodium"),
    HALAL("halal"),
    KOSHER("kosher")
}

enum class Allergen(val name: String) {
    NUTS("nuts"),
    PEANUTS("peanuts"),
    DAIRY("dairy"),
    EGGS("eggs"),
    SOY("soy"),
    WHEAT("wheat"),
    FISH("fish"),
    SHELLFISH("shellfish"),
    SESAME("sesame"),
    SULFITES("sulfites")
}

// Extension functions
fun User.hasDietaryTag(tag: DietaryTag): Boolean =
    profile?.dietaryTags?.contains(tag.name) ?: false

fun User.hasAllergen(allergen: Allergen): Boolean =
    profile?.allergens?.contains(allergen.name) ?: false

// Mock data for testing
fun User.Companion.mock(): User = User(
    id = UUID.randomUUID().toString(),
    username = "testuser",
    email = "test@example.com",
    householdId = UUID.randomUUID().toString(),
    isActive = true,
    isPremium = false,
    createdAt = "2024-01-01T00:00:00Z",
    updatedAt = "2024-01-01T00:00:00Z",
    profile = UserProfile.mock()
)

fun UserProfile.Companion.mock(): UserProfile = UserProfile(
    id = UUID.randomUUID().toString(),
    userId = UUID.randomUUID().toString(),
    displayName = "Test User",
    avatarUrl = null,
    dietaryTags = listOf(DietaryTag.VEGETARIAN.name),
    allergens = listOf(Allergen.NUTS.name),
    preferences = mapOf("theme" to "dark"),
    featureToggles = mapOf("ai_suggestions" to true),
    createdAt = "2024-01-01T00:00:00Z",
    updatedAt = "2024-01-01T00:00:00Z"
)