package com.ken.polskimaster.data.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.ken.polskimaster.data.model.VocabItem

@Database(entities = [VocabItem::class], version = 1, exportSchema = false)
abstract class VocabDatabase : RoomDatabase() {
    abstract fun vocabDao(): VocabDao

    companion object {
        @Volatile
        private var INSTANCE: VocabDatabase? = null

        fun getDatabase(context: Context): VocabDatabase {
            return INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(
                    context.applicationContext,
                    VocabDatabase::class.java,
                    "vocab_database"
                )
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
