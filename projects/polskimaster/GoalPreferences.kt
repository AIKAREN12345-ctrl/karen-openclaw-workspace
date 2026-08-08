package com.ken.polskimaster.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "goal_prefs")

class GoalPreferences(private val context: Context) {

    companion object {
        val STREAK_KEY = intPreferencesKey("streak_count")
        val LAST_STUDY_DATE_KEY = stringPreferencesKey("last_study_date")
        val DAILY_GOAL_KEY = intPreferencesKey("daily_goal")
        val TODAY_PROGRESS_KEY = intPreferencesKey("today_progress")
    }

    val streakFlow: Flow<Int> = context.dataStore.data.map { it[STREAK_KEY] ?: 0 }
    val dailyGoalFlow: Flow<Int> = context.dataStore.data.map { it[DAILY_GOAL_KEY] ?: 10 }
    val todayProgressFlow: Flow<Int> = context.dataStore.data.map { it[TODAY_PROGRESS_KEY] ?: 0 }

    suspend fun recordStudySession(wordsStudied: Int) {
        val today = java.time.LocalDate.now().toString()
        context.dataStore.edit { prefs ->
            val lastDate = prefs[LAST_STUDY_DATE_KEY]
            val currentStreak = prefs[STREAK_KEY] ?: 0
            val newStreak = when {
                lastDate == null -> 1
                lastDate == today -> currentStreak
                java.time.LocalDate.parse(lastDate).plusDays(1).toString() == today -> currentStreak + 1
                else -> 1
            }
            prefs[STREAK_KEY] = newStreak
            prefs[LAST_STUDY_DATE_KEY] = today
            prefs[TODAY_PROGRESS_KEY] = (prefs[TODAY_PROGRESS_KEY] ?: 0) + wordsStudied
        }
    }

    suspend fun resetDailyProgress() {
        context.dataStore.edit { prefs ->
            prefs[TODAY_PROGRESS_KEY] = 0
        }
    }

    suspend fun setDailyGoal(goal: Int) {
        context.dataStore.edit { prefs ->
            prefs[DAILY_GOAL_KEY] = goal
        }
    }
}
