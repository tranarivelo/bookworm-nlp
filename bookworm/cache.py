import os
import json

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def save_to_cache(book_id: int, task_name: str, data):
    filepath = os.path.join(CACHE_DIR, f"{book_id}_{task_name}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_from_cache(book_id: int, task_name: str):
    filepath = os.path.join(CACHE_DIR, f"{book_id}_{task_name}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None
