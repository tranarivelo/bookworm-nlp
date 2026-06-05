import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def summarize_book(text: str, num_sentences: int = 4) -> str:
    sentences = sent_tokenize(text)

    if len(sentences) <= num_sentences:
        return text

    valid_sentences = []
    original_indices = []

    for i, sentence in enumerate(sentences):
        word_count = len(word_tokenize(sentence))
        if 10 <= word_count <= 40:
            valid_sentences.append(sentence)
            original_indices.append(i)

    if not valid_sentences:
        valid_sentences = sentences
        original_indices = list(range(len(sentences)))

    vectorizer = TfidfVectorizer(stop_words='english')

    try:
        tfidf_matrix = vectorizer.fit_transform(valid_sentences)
    except ValueError:
        return " ".join(sentences[:num_sentences])

    sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    top_score_indices = sentence_scores.argsort()[-num_sentences:]
    top_score_indices.sort()

    return " ".join([valid_sentences[i] for i in top_score_indices])


def calculate_lexdiv(text: str) -> dict:
    tokens = word_tokenize(text)
    words = [t.lower() for t in tokens if t.isalpha()]

    tok = len(words)
    typ = len(set(words))

    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1

    hap = sum(1 for count in freq.values() if count == 1)

    ttr = round(typ / tok, 4) if tok > 0 else 0.0
    mwl = round(sum(len(w) for w in words) / tok, 4) if tok > 0 else 0.0
    mwf = round(tok / typ, 4) if typ > 0 else 0.0

    return {"tok": tok, "typ": typ, "hap": hap, "ttr": ttr, "mwl": mwl, "mwf": mwf}


def split_into_sections(text: str, n_sections: int = 4) -> list:
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
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
    sections = split_into_sections(text, n_sections=n_topics)

    vectorizer = CountVectorizer(
        stop_words='english',
        max_df=0.9,
        min_df=2,
        max_features=1000
    )

    try:
        dtm = vectorizer.fit_transform(sections)
    except ValueError:
        return {i + 1: [] for i in range(n_topics)}

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=10)
    lda.fit(dtm)

    feature_names = vectorizer.get_feature_names_out()

    topics = {}
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_words:][::-1]
        topics[topic_idx + 1] = [feature_names[i] for i in top_indices]

    return topics


def extract_entities(text: str) -> dict:
    characters = set()
    locations = set()

    for sentence in sent_tokenize(text):
        tokens = word_tokenize(sentence)
        tagged = pos_tag(tokens)
        chunks = ne_chunk(tagged)

        for chunk in chunks:
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
