package com.ukc

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.rememberNavController
import com.ukc.presentation.navigation.NavGraph
import com.ukc.presentation.theme.UKCTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            UKCTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    NavGraph(navController = navController)
                }
            }
        }
    }
}

class UKCApplication : android.app.Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize app-wide services
        initializeServices()
    }
    
    private fun initializeServices() {
        // Initialize dependency injection
        // Hilt handles this automatically
        
        // Initialize notification channels
        NotificationService.createNotificationChannels(this)
        
        // Initialize work manager for background tasks
        BackgroundTaskManager.initialize(this)
    }
}