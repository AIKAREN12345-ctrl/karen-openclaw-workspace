package com.ken.polskimaster.srs

import com.ken.polskimaster.data.model.VocabItem
import kotlin.math.max
import kotlin.math.roundToInt

object SrsScheduler {

    fun schedule(item: VocabItem, quality: Int): VocabItem {
        // quality: 0=Again, 3=Hard, 4=Good, 5=Easy
        var repetitions = item.repetitions
        var interval = item.intervalDays
        var ease = item.easeFactor

        if (quality < 3) {
            repetitions = 0
            interval = 1
        } else {
            repetitions += 1
            interval = when (repetitions) {
                1 -> 1
                2 -> 6
                else -> (interval * ease).roundToInt()
            }
        }

        ease = max(1.3f, ease + (0.1f - (5 - quality) * (0.08f + (5 - quality) * 0.02f)))
        val nextReview = System.currentTimeMillis() + interval * 24L * 60L * 60L * 1000L

        return item.copy(
            repetitions = repetitions,
            intervalDays = interval,
            easeFactor = ease,
            nextReviewDate = nextReview,
            isLearned = repetitions >= 1
        )
    }
}
