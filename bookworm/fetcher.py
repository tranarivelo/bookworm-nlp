import os
import re
import sys
import csv
import requests

BOOKS_DIR = "books"
os.makedirs(BOOKS_DIR, exist_ok=True)


def download_book(book_id: int) -> str:
    filepath = os.path.join(BOOKS_DIR, f"{book_id}.txt")
    if os.path.exists(filepath):
        return filepath

    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    print(f"Info: Downloading book {book_id}...")

    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"Error: Book {book_id} not found.", file=sys.stderr)
            sys.exit(1)
        response.raise_for_status()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"Error downloading book: {e}", file=sys.stderr)
        sys.exit(1)


def get_book_info(book_id: int, csv_filename="pg_catalog.csv") -> dict:
    if not os.path.exists(csv_filename):
        return {"id": str(book_id), "title": f"Book {book_id}", "authors": "Unknown", "bookshelves": "Unknown"}

    with open(csv_filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Text#'] == str(book_id):
                return {
                    'id': row['Text#'],
                    'title': row['Title'].replace('\r\n', ' ').replace('\n', ' '),
                    'authors': row['Authors'],
                    'bookshelves': row['Bookshelves']
                }
    return {"id": str(book_id), "title": f"Book {book_id}", "authors": "Unknown", "bookshelves": "Unknown"}


def get_clean_text(book_id: int) -> str:
    filepath = download_book(book_id)

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"

    if start_marker in text:
        text = text.split(start_marker, 1)[1].split("***", 1)[1]
    if end_marker in text:
        text = text.split(end_marker, 1)[0]

    text = re.sub(r'[ \t]+', ' ', text, flags=re.MULTILINE).strip()
    return text
