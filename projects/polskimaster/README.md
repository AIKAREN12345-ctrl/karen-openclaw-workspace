# PolskiMaster — Complete Core Architecture

## What I Built

### 1. Vocabulary & Data
- **`vocab_schema.json`** — JSON schema for vocabulary entries
- **`generate_vocab.py`** — generates `vocabulary.json` with 5,000 dummy Polish-English entries

### 2. Database (Room)
- **`VocabItem.kt`** — entity with SRS fields (interval, ease factor, next review date)
- **`VocabDao.kt`** — queries for due items, learned count, total count
- **`VocabDatabase.kt`** — singleton Room database

### 3. SRS Algorithm
- **`SrsScheduler.kt`** — simplified Anki-like SM-2 scheduling (Again/Hard/Good/Easy)

### 4. MVVM + UI
- **`FlashcardViewModel.kt`** — loads cards, reveals answers, updates SRS
- **`FlashcardScreen.kt`** — Material Design 3 flashcard UI with TTS, progress bar, difficulty buttons, streak counter display slot

### 5. Onboarding
- **`OnboardingScreen.kt`** — interactive Polish alphabet tutorial (ą, ę, ł, ń, ó, ś, ź, ż) with Next button and progress bar

### 6. Gamification
- **`GoalPreferences.kt`** — DataStore-backed streak counter, daily goals, and today's progress tracking
- **`StreakCounter.kt`** — reusable streak UI component with fire icon

### 7. Asset Import
- **`AssetImporter.kt`** — reads `vocabulary.json` from `assets/` and bulk-inserts into Room on first launch

### 8. Navigation
- **`MainActivity.kt`** — shows onboarding on first launch, then transitions to flashcard screen

## Project Structure
```
app/src/main/java/com/ken/polskimaster/
├── data/
│   ├── db/
│   │   ├── VocabDatabase.kt
│   │   ├── VocabDao.kt
│   │   └── Converters.kt (if needed)
│   ├── model/
│   │   └── VocabItem.kt
│   └── repository/
│       └── (optional)
├── srs/
│   └── SrsScheduler.kt
├── tts/
│   └── PolishTtsManager.kt (wrapped inside FlashcardScreen)
├── ui/
│   ├── components/
│   │   ├── StreakCounter.kt
│   │   └── ProgressBar.kt (LinearProgressIndicator inline)
│   ├── flashcard/
│   │   ├── FlashcardScreen.kt
│   │   └── FlashcardViewModel.kt
│   ├── onboarding/
│   │   └── OnboardingScreen.kt
│   └── theme/
│       └── PolskiMasterTheme (use Material3)
├── utils/
│   ├── AssetImporter.kt
│   └── GoalPreferences.kt
└── MainActivity.kt
```

## Gradle Dependencies You Need
```kotlin
// Room
implementation("androidx.room:room-runtime:2.6.1")
kapt("androidx.room:room-compiler:2.6.1")
implementation("androidx.room:room-ktx:2.6.1")

// DataStore
implementation("androidx.datastore:datastore-preferences:1.0.0")

// ViewModel Compose
implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
```

## How to Build and Run
1. Run `python generate_vocab.py` → creates `vocabulary.json`
2. Copy `vocabulary.json` to `app/src/main/assets/vocabulary.json`
3. Open project in Android Studio
4. Build and run

## What's Still for You to Do
- Polish the Material Design 3 theme colors
- Add haptic feedback on difficulty selection
- Consider adding a settings screen for daily goal adjustment
- Add Polish TTS voice selection if the default isn't great

---
*Built by Karen for Ken 🦞*
