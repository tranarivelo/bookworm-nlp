#!/usr/bin/env python3
import argparse
import os
import json
import requests
import re
import sys
import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tokenize import sent_tokenize
from nltk.tree import Tree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv 

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

def summarize_book(text: str, num_sentences: int = 4) -> str:
    # Decouper le texte en phrases
    sentences = sent_tokenize(text)
    
    # si le texte est minuscule
    if len(sentences) <= num_sentences:
        return text
        
    # filtrer les phrases selon la longeure
    valid_sentences = []
    original_indices = []
    
    for i, sentence in enumerate(sentences):
        word_count = len(word_tokenize(sentence))
        if 10 <= word_count <= 40:  # On garde les phrases de taille moyenne
            valid_sentences.append(sentence)
            original_indices.append(i)
            
    if not valid_sentences:
        valid_sentences = sentences
        original_indices = list(range(len(sentences)))

    # Vectorisation TF-IDF
    # On enlève les stopwords pour que les scores se concentrent sur les mots porteurs de sens
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform(valid_sentences)
    except ValueError:
        # En cas d'erreur (ex: vocabulaire vide), on renvoie les premières phrases
        return " ".join(sentences[:num_sentences])

    # score TF-IDF de chaque phrase
    sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    top_score_indices = sentence_scores.argsort()[-num_sentences:]# argsort() pour trier

    top_score_indices.sort() # trier dans l'ordre d'apparition dans le texte original 
    
    #assembler le résumé
    summary = " ".join([valid_sentences[i] for i in top_score_indices])
    
    return summary

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
    
def split_into_sections(text: str, n_sections: int = 4) -> list:
    
    """Découpe le texte en sections de taille ~ égale.
    division par nombre de caractères."""
    
    # Découpe d'abord en paragraphes (séparés par lignes vides)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Regroupe les paragraphes en sections égales
    section_size = max(1, len(paragraphs) // n_sections)
    sections = []
    
    for i in range(n_sections):
        start = i * section_size

        end = start + section_size if i < n_sections - 1 else len(paragraphs)
        section_text = " ".join(paragraphs[start:end])
        if section_text:
            sections.append(section_text)
    
    return sections

def extract_topics(text: str, n_topics: int = 4, n_words: int = 10) -> dict:
    """Extrait les topics principaux d'un livre via LDA.

    Pipeline : découpage en sections -> vectorisation
    LDA -> extraction des top mots par topic.

    Approche choisie : LDA (Latent Dirichlet Allocation)
    - Chaque section est un regroupement de topics
    - Chaque topic est une distribution sur le vocabulaire (plus large donc...)

    Limitations :
    - LDA est sensible au nombre de topics choisi (ici fixé à 4)
    - Les stopwords doivent être filtrés en amont pour de bons résultats"""

    sections = split_into_sections(text, n_sections=n_topics)

    # Vectorisation : transforme chaque section en vecteur de fréquences de mots
    # max_df=0.9 : ignore les mots présents dans plus de 90% des sections (trop communs)
    # min_df=2   : ignore les mots présents dans moins de 2 sections (trop rares)
    vectorizer = CountVectorizer(
        stop_words='english',
        max_df=0.9,
        min_df=2,
        max_features=1000
    )

    try:
        dtm = vectorizer.fit_transform(sections)
    except ValueError:
        # Pas assez de sections ou vocabulaire trop pauvre
        return {i + 1: [] for i in range(n_topics)}

    # LDA : trouve n_topics groupes de mots cohérents
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=10
    )
    lda.fit(dtm)

    # Récupère le vocabulaire
    feature_names = vectorizer.get_feature_names_out()

    # Pour chaque topic, récupère les n_words mots les plus représentatifs
    topics = {}
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        topics[topic_idx + 1] = top_words

    return topics
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
        
if __name__ == "__main__":
    main()