from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .fetcher import get_clean_text, get_book_info

COLLECTION_IDS = [
    11, 12, 16, 55, 113, 120, 236, 108, 834, 863, 1661,
    61262, 69087, 70114, 35, 36, 84, 159, 164, 345, 68283
]


def get_similar_books(target_id: int) -> list:
    collection_ids = list(COLLECTION_IDS)
    if target_id not in collection_ids:
        collection_ids.append(target_id)

    print(f"Info: Processing {len(collection_ids)} books for similarity mapping. This might take a minute...")

    texts = []
    valid_ids = []

    for b_id in collection_ids:
        try:
            text = get_clean_text(b_id)
            texts.append(text)
            valid_ids.append(b_id)
        except SystemExit:
            pass

    vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(texts)

    target_index = valid_ids.index(target_id)
    target_vector = tfidf_matrix[target_index]

    similarities = cosine_similarity(target_vector, tfidf_matrix).flatten()

    scores = [(sim, valid_ids[i]) for i, sim in enumerate(similarities)]
    scores.sort(reverse=True, key=lambda x: x[0])
    top_5_ids = [b_id for sim, b_id in scores if b_id != target_id][:5]

    return [get_book_info(b_id)['title'] for b_id in top_5_ids]
