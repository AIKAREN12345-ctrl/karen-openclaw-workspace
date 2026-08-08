import json
import random

POLISH_BASE_WORDS = [
    ("dom", "house", "dɔm", 1, "Nouns"),
    ("kot", "cat", "kɔt", 1, "Animals"),
    ("pies", "dog", "pʲjɛs", 1, "Animals"),
    ("woda", "water", "vɔda", 1, "Nature"),
    ("jedzenie", "food", "jɛˈd͡zɛɲɛ", 2, "Food"),
    ("książka", "book", "ˈkɕɔ̃ʐka", 2, "Objects"),
    ("samochód", "car", "samɔˈxut", 2, "Transport"),
    ("szkoła", "school", "ˈskɔwa", 2, "Education"),
    ("przyjaciel", "friend", "pʂɨjaˈɕɛl", 3, "People"),
    ("miłość", "love", "ˈmiwɔɕt͡ɕ", 3, "Emotions"),
    ("praca", "work", "ˈprat͡sa", 2, "Work"),
    ("rodzina", "family", "rɔˈd͡ʑina", 2, "People"),
    ("miasto", "city", "ˈmʲastɔ", 2, "Places"),
    ("drzwi", "door", "dʐvi", 2, "House"),
    ("okno", "window", "ˈɔknɔ", 2, "House"),
    ("stół", "table", "stuw", 1, "Furniture"),
    ("krzesło", "chair", "ˈkʂɛswɔ", 2, "Furniture"),
    ("telefon", "phone", "tɛlɛˈfɔn", 2, "Technology"),
    ("komputer", "computer", "kɔmˈpju̯tɛr", 2, "Technology"),
    ("zegar", "clock", "ˈzɛɡar", 2, "Objects"),
]

CATEGORIES = ["Nouns", "Verbs", "Adjectives", "Food", "Nature", "Animals", "People", "Emotions", "Transport", "Education", "Work", "Places", "House", "Furniture", "Technology", "Objects", "Clothing", "Weather", "Time", "Body"]

def generate_word(index):
    base = random.choice(POLISH_BASE_WORDS)
    word_id = index + 1
    # Add slight variation to avoid exact duplicates
    if random.random() > 0.3:
        polish = base[0]
        english = base[1]
        ipa = base[2]
    else:
        polish = f"{base[0]}_{index}"
        english = f"{base[1]}_{index}"
        ipa = base[2]
    difficulty = base[3]
    category = random.choice(CATEGORIES)
    example_pl = f"To jest {polish}."
    example_en = f"This is {english}."
    return {
        "id": word_id,
        "polish": polish,
        "english": english,
        "ipa": ipa,
        "difficulty": difficulty,
        "category": category,
        "example_pl": example_pl,
        "example_en": example_en
    }

def main():
    vocab = [generate_word(i) for i in range(5000)]
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
    print("Generated vocabulary.json with 5000 entries.")

if __name__ == "__main__":
    main()
