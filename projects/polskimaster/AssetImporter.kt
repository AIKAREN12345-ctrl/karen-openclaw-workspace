package com.ken.polskimaster.utils

import android.content.Context
import com.ken.polskimaster.data.db.VocabDao
import com.ken.polskimaster.data.model.VocabItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

object AssetImporter {

    suspend fun importIfNeeded(context: Context, dao: VocabDao) {
        withContext(Dispatchers.IO) {
            val total = dao.getTotalCount()
            // Flow collects asynchronously; simplistic check:
            // In production, use a shared preference flag for import completion
            val prefs = context.getSharedPreferences("importer", Context.MODE_PRIVATE)
            if (prefs.getBoolean("imported", false)) return@withContext

            val json = context.assets.open("vocabulary.json").bufferedReader().use { it.readText() }
            val array = JSONArray(json)
            val items = mutableListOf<VocabItem>()

            for (i in 0 until array.length()) {
                val obj = array.getJSONObject(i)
                items.add(
                    VocabItem(
                        id = obj.getInt("id"),
                        polish = obj.getString("polish"),
                        english = obj.getString("english"),
                        ipa = obj.getString("ipa"),
                        difficulty = obj.getInt("difficulty"),
                        category = obj.getString("category"),
                        examplePl = obj.optString("example_pl"),
                        exampleEn = obj.optString("example_en")
                    )
                )
            }

            if (items.isNotEmpty()) {
                dao.insertAll(items)
                prefs.edit().putBoolean("imported", true).apply()
            }
        }
    }
}
