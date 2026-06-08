from .cache import save_to_cache, load_from_cache
from .fetcher import get_clean_text, get_book_info
from .analysis import calculate_lexdiv, extract_topics, extract_entities, summarize_book
from .similarity import get_similar_books


def generate_book_card(book_id: int) -> dict:
    text = get_clean_text(book_id)
    info = get_book_info(book_id)

    lexdiv = load_from_cache(book_id, "lexdiv")
    if lexdiv is None:
        lexdiv = calculate_lexdiv(text)
        save_to_cache(book_id, "lexdiv", lexdiv)

    topics = load_from_cache(book_id, "topics")
    if topics is None:
        raw_topics = extract_topics(text)
        topics = {str(k): v for k, v in raw_topics.items()}
        save_to_cache(book_id, "topics", topics)

    entities = load_from_cache(book_id, "entities")
    if entities is None:
        entities = extract_entities(text)
        save_to_cache(book_id, "entities", entities)

    summary = load_from_cache(book_id, "summarize")
    if summary is None:
        summary = summarize_book(text, num_sentences=4)
        save_to_cache(book_id, "summarize", summary)

    similar = load_from_cache(book_id, "similar")
    if similar is None:
        similar = get_similar_books(book_id)
        save_to_cache(book_id, "similar", similar)

    return {
        "info": info,
        "lexdiv": lexdiv,
        "topics": topics,
        "entities": entities,
        "summary": summary,
        "similar": similar
    }
