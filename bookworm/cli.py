import argparse
import json

from .cache import save_to_cache, load_from_cache
from .fetcher import get_clean_text
from .analysis import calculate_lexdiv, extract_topics, extract_entities, summarize_book
from .similarity import get_similar_books
from .card import generate_book_card


def main():
    parser = argparse.ArgumentParser(description="Through the Looking-Glass - NLP Engine")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--lexdiv', type=int, help="Calculate lexical diversity for a book ID")
    group.add_argument('--topics', type=int, help="Extract main topics for a book ID")
    group.add_argument('--entities', type=int, help="Extract named entities for a book ID")
    group.add_argument('--summarize', type=int, help="Summarize a book ID")
    group.add_argument('--similar', type=int, help="Find similar books for a book ID")
    group.add_argument('--card', type=int, help="Generate the full book card for a book ID")

    args = parser.parse_args()

    if args.lexdiv is not None:
        book_id = args.lexdiv
        result = load_from_cache(book_id, "lexdiv")
        if result is None:
            text = get_clean_text(book_id)
            print("Info: Calculating Lexical Diversity (not cached)...")
            result = calculate_lexdiv(text)
            save_to_cache(book_id, "lexdiv", result)
        print(result)

    elif args.topics is not None:
        book_id = args.topics
        result = load_from_cache(book_id, "topics")
        if result is None:
            text = get_clean_text(book_id)
            print("Info: Extracting topics (not cached)...")
            result = extract_topics(text)
            save_to_cache(book_id, "topics", result)
        print(result)

    elif args.entities is not None:
        book_id = args.entities
        result = load_from_cache(book_id, "entities")
        if result is None:
            text = get_clean_text(book_id)
            print("Info: Extracting entities (not cached)...")
            result = extract_entities(text)
            save_to_cache(book_id, "entities", result)
        print(result)

    elif args.summarize is not None:
        book_id = args.summarize
        result = load_from_cache(book_id, "summarize")
        if result is None:
            text = get_clean_text(book_id)
            print("Info: Summarizing book (not cached)...")
            result = summarize_book(text)
            save_to_cache(book_id, "summarize", result)
        print(result)

    elif args.similar is not None:
        book_id = args.similar
        result = load_from_cache(book_id, "similar")
        if result is None:
            print("Info: Calculating book similarity (not cached)...")
            result = get_similar_books(book_id)
            save_to_cache(book_id, "similar", result)
        print(result)

    elif args.card is not None:
        book_id = args.card
        print(f"Info: Generating full book card for ID {book_id}...")
        book_card = generate_book_card(book_id)
        print(json.dumps(book_card, indent=4, ensure_ascii=False))
