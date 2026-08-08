package com.ken.polskimaster.ui.flashcard

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ken.polskimaster.data.db.VocabDatabase
import com.ken.polskimaster.data.model.VocabItem
import com.ken.polskimaster.srs.SrsScheduler
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class FlashcardViewModel(application: Application) : AndroidViewModel(application) {

    private val dao = VocabDatabase.getDatabase(application).vocabDao()

    private val _currentCard = MutableStateFlow<VocabItem?>(null)
    val currentCard: StateFlow<VocabItem?> = _currentCard.asStateFlow()

    private val _answerRevealed = MutableStateFlow(false)
    val answerRevealed: StateFlow<Boolean> = _answerRevealed.asStateFlow()

    val learnedCount = dao.getLearnedCount().stateIn(viewModelScope, SharingStarted.Lazily, 0)
    val totalCount = dao.getTotalCount().stateIn(viewModelScope, SharingStarted.Lazily, 0)

    init {
        loadNextCard()
    }

    fun revealAnswer() {
        _answerRevealed.value = true
    }

    fun onDifficultySelected(quality: Int) {
        val card = _currentCard.value ?: return
        viewModelScope.launch {
            val updated = SrsScheduler.schedule(card, quality)
            dao.update(updated)
            _answerRevealed.value = false
            loadNextCard()
        }
    }

    private fun loadNextCard() {
        viewModelScope.launch {
            _currentCard.value = dao.getDueItems(System.currentTimeMillis(), limit = 1).firstOrNull()
                ?: dao.getNextReviewItem()
        }
    }
}
