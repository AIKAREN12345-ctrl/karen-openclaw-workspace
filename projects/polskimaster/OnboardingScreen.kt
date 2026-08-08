package com.ken.polskimaster.ui.onboarding

import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

private val POLISH_LETTERS = listOf(
    "ą" to "a~ (nasal a, like 'own')",
    "ę" to "e~ (nasal e, like 'eng')",
    "ł" to "w (like 'w')",
    "ń" to "n' (like 'ny')",
    "ó" to "oo (like 'oo' in 'boot')",
    "ś" to "sh (like 'she')",
    "ź" to "zh (like 'vision')",
    "ż" to "zh (like 'vision', harder)"
)

@Composable
fun OnboardingScreen(
    onFinish: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scope = rememberCoroutineScope()
    var step by remember { mutableIntStateOf(0) }
    val current = POLISH_LETTERS.getOrNull(step)

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Polish Alphabet in 30s",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(32.dp))

        if (current != null) {
            AnimatedContent(
                targetState = step,
                label = "letter"
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = current.first,
                        style = MaterialTheme.typography.displayLarge
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = current.second,
                        style = MaterialTheme.typography.titleMedium,
                        textAlign = TextAlign.Center
                    )
                }
            }
        } else {
            Text(
                text = "Gotowe! 🇵🇱",
                style = MaterialTheme.typography.headlineLarge,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "You're ready to master Polish!",
                style = MaterialTheme.typography.bodyLarge
            )
        }

        Spacer(modifier = Modifier.height(48.dp))

        if (current != null) {
            Button(
                onClick = { step++ },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Next")
            }
        } else {
            Button(
                onClick = onFinish,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Start Learning")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        LinearProgressIndicator(
            progress = { (step + 1).toFloat() / (POLISH_LETTERS.size + 1) },
            modifier = Modifier.fillMaxWidth()
        )
    }
}
