#!/usr/bin/env python3
import argparse
import os
import json
import requests
import re
import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tokenize import sent_tokenize
from nltk.tree import Tree

CACHE_DIR = "cache"
BOOKS_DIR = "books"

# creation automatique des dossiers 
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(BOOKS_DIR, exist_ok=True)

def save_to_cache(book_id: int, task_name: str, data):
    """Sauvegarde le résultat un fichier JSON."""
    filepath = os.path.join(CACHE_DIR, f"{book_id}_{task_name}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_from_cache(book_id: int, task_name: str):
    """Charge le résultat depuis le cache s'il existe"""
    filepath = os.path.join(CACHE_DIR, f"{book_id}_{task_name}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def download_book(book_id: int) -> str:
    
        """Télécharge un livre depuis Project Gutenberg et le sauvegarde localement. 
        Retourne le chemin vers le fichier. Ne re-télécharge pas si déjà présent."""
        
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

def get_clean_text(book_id: int) -> str:
    
    """Retourne le texte nettoyé d'un livre : suppression header/footer Gutenberg,
    normalisation des espaces multiples."""
 
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

def calculate_lexdiv(text: str) -> dict:
    """Calcule les métriques de diversité lexicale d'un texte.

    Approche : tokenisation → filtrage ponctuation → comptage fréquences

    Métriques retournées :
    - tok : nombre total de tokens (mots, répétitions incluses)
    - typ : nombre de types (mots uniques)
    - hap : hapax legomena (mots apparaissant exactement une fois)
    - ttr : Type-Token Ratio (typ/tok) — proche de 1 = vocabulaire varié
    - mwl : longueur moyenne des mots en caractères
    - mwf : fréquence moyenne des mots (tok/typ), inverse du TTR"""
    # Tokenisation : découpe le texte en mots
    tokens = word_tokenize(text)

    # Comptage que des mots sans ponctuaction
    words = [t.lower() for t in tokens if t.isalpha()]

    tok = len(words)
    typ = len(set(words))

    # Compte combien de fois chaque mot apparaît
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1

    # Hapax = mots qui n'apparaissent qu'une seule fois
    hap = sum(1 for count in freq.values() if count == 1)

    ttr = round(typ / tok, 4) if tok > 0 else 0.0
    mwl = round(sum(len(w) for w in words) / tok, 4) if tok > 0 else 0.0
    mwf = round(tok / typ, 4) if typ > 0 else 0.0

    return {
        "tok": tok,
        "typ": typ,
        "hap": hap,
        "ttr": ttr,
        "mwl": mwl,
        "mwf": mwf
    }


# STRUCTURE DU CLI
def main():
    parser = argparse.ArgumentParser(description="Through the Looking-Glass - NLP Engine")
    
    #les commandes prennent l'ID du livre en argument (type=int)
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
        #vérifie d'abord le cache 
        result = load_from_cache(book_id, "lexdiv")
        
        if result is None:
            # si pas en cache, on récupère le texte propre
            text = get_clean_text(book_id)
            print("Info: Calculating Lexical Diversity (not cached)...")
            
            result = calculate_lexdiv(text)
            save_to_cache(book_id, "lexdiv", result)
            
        print(result)

    # Ajouter les autres elif ici 
    elif args.topics is not None:
        print(f"Pret à coder --topics pour le livre {args.topics}")
        
    elif args.entities is not None:
        book_id = args.entities
        result = load_from_cache(book_id, "entities")

        if result is None:
            text = get_clean_text(book_id)
            print("Info: Extracting entities (not cached)...")
            result = extract_entities(text)
            save_to_cache(book_id, "entities", result)

        print(result)
        
def extract_entities(text: str) -> dict:
    """Extrait les personnages et lieux d'un texte via NLTK ne_chunk.

    Approche : tokenisation par phrase → POS tagging → NER (Maxent chunker)
    On filtre ensuite les entités de type PERSON, GPE, GSP et LOCATION.

    Limitations connues :
    - Génère des faux positifs sur les mots capitalisés en début de phrase
      (ex: "Found", "Always", "Grief" détectés comme personnages)
    - Le chunker NLTK est un modèle statistique léger entraîné sur des corpus
      généraux (ACE), moins précis que spaCy (en_core_web_sm) ou un LLM
    - Ne distingue pas les homonymes (ex: "Alice" peut être lieu et personnage)

    Choix justifié : NLTK respecte la contrainte "no heavy models" du sujet."""
    
    characters = set()
    locations = set()

    # Tokenization phrase par phrase
    sentences = sent_tokenize(text)

    for sentence in sentences:
        tokens = word_tokenize(sentence)
        tagged = pos_tag(tokens)
        chunks = ne_chunk(tagged)

        for chunk in chunks:
            # ne_chunk retourne soit une entité, soit mot normal
            if isinstance(chunk, Tree):
                name = " ".join(token for token, pos in chunk.leaves())
                label = chunk.label()

                if label == "PERSON":
                    characters.add(name)
                elif label in ("GPE", "GSP", "LOCATION"):
                    locations.add(name)

    return {
        "characters": sorted(list(characters)),
        "locations": sorted(list(locations))
    }

if __name__ == "__main__":
    main()