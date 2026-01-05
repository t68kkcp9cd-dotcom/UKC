package com.ukc.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.hilt.navigation.compose.hiltViewModel
import com.ukc.presentation.features.auth.LoginScreen
import com.ukc.presentation.features.auth.RegisterScreen
import com.ukc.presentation.features.inventory.InventoryScreen
import com.ukc.presentation.features.recipes.RecipesScreen
import com.ukc.presentation.features.mealplanning.MealPlanningScreen
import com.ukc.presentation.features.shopping.ShoppingListsScreen
import com.ukc.presentation.features.settings.SettingsScreen
import com.ukc.presentation.features.dashboard.DashboardScreen

@Composable
fun NavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Screen.Login.route
    ) {
        // Auth Screens
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                },
                onLoginSuccess = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Register.route) {
            RegisterScreen(
                onNavigateToLogin = {
                    navController.navigate(Screen.Login.route)
                },
                onRegisterSuccess = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Main App Screens
        composable(Screen.Dashboard.route) {
            DashboardScreen(
                onNavigateToInventory = {
                    navController.navigate(Screen.Inventory.route)
                },
                onNavigateToRecipes = {
                    navController.navigate(Screen.Recipes.route)
                },
                onNavigateToMealPlanning = {
                    navController.navigate(Screen.MealPlanning.route)
                },
                onNavigateToShopping = {
                    navController.navigate(Screen.Shopping.route)
                }
            )
        }
        
        composable(Screen.Inventory.route) {
            InventoryScreen(
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                }
            )
        }
        
        composable(Screen.Recipes.route) {
            RecipesScreen(
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                }
            )
        }
        
        composable(Screen.MealPlanning.route) {
            MealPlanningScreen(
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                }
            )
        }
        
        composable(Screen.Shopping.route) {
            ShoppingListsScreen(
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                }
            )
        }
        
        composable(Screen.Settings.route) {
            SettingsScreen(
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Dashboard.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Recipe Detail Screen
        composable(
            route = Screen.RecipeDetail.route,
            arguments = Screen.RecipeDetail.arguments
        ) { backStackEntry ->
            val recipeId = backStackEntry.arguments?.getString("recipeId") ?: ""
            com.ukc.presentation.features.recipes.RecipeDetailScreen(
                recipeId = recipeId,
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                }
            )
        }
        
        // Barcode Scanner Screen
        composable(Screen.BarcodeScanner.route) {
            com.ukc.presentation.features.inventory.BarcodeScannerScreen(
                onNavigateBack = {
                    navController.navigateUp()
                },
                onBarcodeScanned = { barcode ->
                    navController.previousBackStackEntry?.savedStateHandle?.set("scannedBarcode", barcode)
                    navController.navigateUp()
                }
            )
        }
        
        // Voice Guided Cooking Screen
        composable(
            route = Screen.VoiceGuidedCooking.route,
            arguments = Screen.VoiceGuidedCooking.arguments
        ) { backStackEntry ->
            val recipeId = backStackEntry.arguments?.getString("recipeId") ?: ""
            com.ukc.presentation.features.recipes.VoiceGuidedCookingScreen(
                recipeId = recipeId,
                viewModel = hiltViewModel(),
                onNavigateBack = {
                    navController.navigateUp()
                }
            )
        }
    }
}

// Screen definitions
sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Register : Screen("register")
    object Dashboard : Screen("dashboard")
    object Inventory : Screen("inventory")
    object Recipes : Screen("recipes")
    object MealPlanning : Screen("meal-planning")
    object Shopping : Screen("shopping")
    object Settings : Screen("settings")
    
    object RecipeDetail : Screen("recipe-detail/{recipeId}") {
        const val ARG_RECIPE_ID = "recipeId"
        val arguments = listOf(
            androidx.navigation.NavArgument.Builder()
                .setName(ARG_RECIPE_ID)
                .setType(androidx.navigation.NavType.StringType)
                .build()
        )
        
        fun createRoute(recipeId: String): String = "recipe-detail/$recipeId"
    }
    
    object BarcodeScanner : Screen("barcode-scanner")
    
    object VoiceGuidedCooking : Screen("voice-cooking/{recipeId}") {
        const val ARG_RECIPE_ID = "recipeId"
        val arguments = listOf(
            androidx.navigation.NavArgument.Builder()
                .setName(ARG_RECIPE_ID)
                .setType(androidx.navigation.NavType.StringType)
                .build()
        )
        
        fun createRoute(recipeId: String): String = "voice-cooking/$recipeId"
    }
}