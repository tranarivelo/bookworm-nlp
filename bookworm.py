#!/usr/bin/env python3
import argparse
import os
import json
import requests
import re
import sys


# téléchargement (si pas deja dans le projet)
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

#nettoyage du texte
def get_clean_text(book_id: int) -> str:
    """Récupère le texte du livre et le nettoie (Header/Footer, espaces)."""
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


#STRUCTURE DU CLI
def main():
    parser = argparse.ArgumentParser(description="Through the Looking-Glass - NLP Engine")
    
    #les commandes prennent l'ID du livre en argument
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument('--lexdiv', type=int, help="Calculate lexical diversity for a book ID")
    group.add_argument('--topics', type=int, help="Extract main topics for a book ID")
    group.add_argument('--entities', type=int, help="Extract named entities for a book ID")
    group.add_argument('--summarize', type=int, help="Summarize a book ID")
    group.add_argument('--similar', type=int, help="Find similar books for a book ID")
    group.add_argument('--card', type=int, help="Generate the full book card for a book ID")
    
    args = parser.parse_args()
    
    # --- ROUTAGE DES COMMANDES ---
    
    if args.lexdiv is not None:
        book_id = args.lexdiv
        
        
        
            
       

    # Les autres elif viendront se placer ici sur le même modèle...
    elif args.topics is not None:
        print(f"Pret à coder --topics pour le livre {args.topics}")
        
    elif args.entities is not None:
        print(f"Pret à coder --entities pour le livre {args.entities}")

if __name__ == "__main__":
    main()