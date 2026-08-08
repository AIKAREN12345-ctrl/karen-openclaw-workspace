package com.ken.polskimaster.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "vocab_items")
data class VocabItem(
    @PrimaryKey val id: Int,
    val polish: String,
    val english: String,
    val ipa: String,
    val difficulty: Int,
    val category: String,
    val examplePl: String,
    val exampleEn: String,
    val intervalDays: Int = 1,
    val repetitions: Int = 0,
    val easeFactor: Float = 2.5f,
    val nextReviewDate: Long = System.currentTimeMillis(),
    val isLearned: Boolean = false
)
