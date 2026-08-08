package com.ken.polskimaster

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.*
import androidx.lifecycle.lifecycleScope
import com.ken.polskimaster.data.db.VocabDatabase
import com.ken.polskimaster.ui.flashcard.FlashcardScreen
import com.ken.polskimaster.ui.onboarding.OnboardingScreen
import com.ken.polskimaster.ui.theme.PolskiMasterTheme
import com.ken.polskimaster.utils.AssetImporter
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val dao = VocabDatabase.getDatabase(this).vocabDao()
        lifecycleScope.launch {
            AssetImporter.importIfNeeded(applicationContext, dao)
        }

        val prefs = getSharedPreferences("app_prefs", MODE_PRIVATE)
        val onboardingShown = prefs.getBoolean("onboarding_shown", false)

        setContent {
            PolskiMasterTheme {
                var showOnboarding by remember { mutableStateOf(!onboardingShown) }

                if (showOnboarding) {
                    OnboardingScreen(
                        onFinish = {
                            prefs.edit().putBoolean("onboarding_shown", true).apply()
                            showOnboarding = false
                        }
                    )
                } else {
                    FlashcardScreen()
                }
            }
        }
    }
}
