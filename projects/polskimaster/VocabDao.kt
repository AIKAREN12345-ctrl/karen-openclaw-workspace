package com.ken.polskimaster.data.db

import androidx.room.*
import com.ken.polskimaster.data.model.VocabItem
import kotlinx.coroutines.flow.Flow

@Dao
interface VocabDao {
    @Query("SELECT * FROM vocab_items ORDER BY nextReviewDate ASC LIMIT 1")
    suspend fun getNextReviewItem(): VocabItem?

    @Query("SELECT * FROM vocab_items WHERE nextReviewDate <= :now ORDER BY nextReviewDate ASC LIMIT :limit")
    suspend fun getDueItems(now: Long, limit: Int): List<VocabItem>

    @Query("SELECT COUNT(*) FROM vocab_items WHERE isLearned = 1")
    fun getLearnedCount(): Flow<Int>

    @Query("SELECT COUNT(*) FROM vocab_items")
    fun getTotalCount(): Flow<Int>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<VocabItem>)

    @Update
    suspend fun update(item: VocabItem)
}
