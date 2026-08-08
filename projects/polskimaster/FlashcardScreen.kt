package com.ken.polskimaster.ui.flashcard

import android.speech.tts.TextToSpeech
import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import java.util.*

@Composable
fun FlashcardScreen(
    viewModel: FlashcardViewModel = viewModel()
) {
    val card by viewModel.currentCard.collectAsState()
    val revealed by viewModel.answerRevealed.collectAsState()
    val learned by viewModel.learnedCount.collectAsState()
    val total by viewModel.totalCount.collectAsState()

    val context = LocalContext.current
    var tts by remember { mutableStateOf<TextToSpeech?>(null) }

    LaunchedEffect(Unit) {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("pl", "PL")
            }
        }
    }

    DisposableEffect(Unit) {
        onDispose { tts?.shutdown() }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Progress header
        Text(
            text = "PolskiMaster",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(8.dp))
        LinearProgressIndicator(
            progress = { if (total > 0) learned / total.toFloat() else 0f },
            modifier = Modifier.fillMaxWidth()
        )
        Text(
            text = "$learned / $total words learned",
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(modifier = Modifier.height(32.dp))

        card?.let { vocab ->
            // Flashcard surface
            ElevatedCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                colors = CardDefaults.elevatedCardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = vocab.polish,
                            style = MaterialTheme.typography.displayLarge,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "[${vocab.ipa}]",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        AnimatedVisibility(visible = revealed) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Spacer(modifier = Modifier.height(24.dp))
                                Text(
                                    text = vocab.english,
                                    style = MaterialTheme.typography.headlineSmall,
                                    color = MaterialTheme.colorScheme.primary
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "\"${vocab.examplePl}\"",
                                    style = MaterialTheme.typography.bodyMedium,
                                    textAlign = TextAlign.Center
                                )
                                Text(
                                    text = "\"${vocab.exampleEn}\"",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    textAlign = TextAlign.Center
                                )
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // TTS button
            IconButton(
                onClick = { tts?.speak(vocab.polish, TextToSpeech.QUEUE_FLUSH, null, null) }
            ) {
                Icon(Icons.Default.VolumeUp, contentDescription = "Play pronunciation")
            }

            Spacer(modifier = Modifier.height(16.dp))

            if (!revealed) {
                Button(
                    onClick = { viewModel.revealAnswer() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Show Answer")
                }
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    DifficultyButton(
                        label = "Again",
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.weight(1f),
                        onClick = { viewModel.onDifficultySelected(0) }
                    )
                    DifficultyButton(
                        label = "Hard",
                        color = MaterialTheme.colorScheme.tertiary,
                        modifier = Modifier.weight(1f),
                        onClick = { viewModel.onDifficultySelected(3) }
                    )
                    DifficultyButton(
                        label = "Good",
                        color = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.weight(1f),
                        onClick = { viewModel.onDifficultySelected(4) }
                    )
                    DifficultyButton(
                        label = "Easy",
                        color = MaterialTheme.colorScheme.secondary,
                        modifier = Modifier.weight(1f),
                        onClick = { viewModel.onDifficultySelected(5) }
                    )
                }
            }
        } ?: run {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No cards due. You're all caught up! 🎉")
            }
        }
    }
}

@Composable
private fun DifficultyButton(
    label: String,
    color: androidx.compose.ui.graphics.Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = modifier,
        colors = ButtonDefaults.buttonColors(containerColor = color)
    ) {
        Text(label)
    }
}
