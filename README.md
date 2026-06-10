# Bookworm — NLP Engine for Project Gutenberg

A lightweight CLI tool that creates "book cards" by performing NLP analysis on books from Project Gutenberg.

Built for the T-AIA-600 project.

---

## Getting Started

### Option 1 — Docker (recommended)

Build the image once:

```bash
docker build -t bookworm .
```

Create persistent volumes once:

```bash
docker volume create bookworm-cache
docker volume create bookworm-books
docker volume create bookworm-covers
```

Run a command:

```bash
docker run --rm -v bookworm-cache:/app/cache -v bookworm-books:/app/books bookworm --lexdiv 11
```

Books and cached results are stored in Docker volumes and persist between runs.

### Option 2 — Local (Python 3.11+)

```bash
git clone https://github.com/EpitechMscProPromo2028/T-AIA-600-PAR_28.git
cd T-AIA-600-PAR_28

python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# or
.venv\Scripts\Activate.ps1     # Windows PowerShell

pip install -r requirements.txt
python -m nltk.downloader punkt punkt_tab stopwords averaged_perceptron_tagger averaged_perceptron_tagger_eng maxent_ne_chunker_tab wordnet words
```

---

## Usage

```bash
python bookworm.py <command> <book_id>
```

| Command | Description |
|---|---|
| `--lexdiv <ID>` | Lexical diversity metrics |
| `--entities <ID>` | Extract characters and locations |
| `--topics <ID>` | Topic modeling (LDA) |
| `--summarize <ID>` | Book summarization |
| `--similar <ID>` | Find similar books |
| `--card <ID>` | Full book card |
| `--author <name>` | Download all books by an author |
| `--category <name>` | Download all books matching a category |

### Examples

```bash
# Lexical diversity of Alice in Wonderland (ID 11)
python bookworm.py --lexdiv 11

# Named entities of Dracula (ID 345)
python bookworm.py --entities 345

# Topic modeling of Peter Pan (ID 16)
python bookworm.py --topics 16

# Download all books by Lewis Carroll
python bookworm.py --author Carroll

# Download all books in the Horror category
python bookworm.py --category Horror
```

### Web interface

```bash
# Docker
docker run -p 8080:8080 -v bookworm-cache:/app/cache -v bookworm-books:/app/books bookworm --web

# Local
python bookworm.py --web
```

Then open [http://localhost:8080](http://localhost:8080).

---

## Project Structure

```
T-AIA-600-PAR_28/
├── bookworm.py          # Entry point (CLI + --web)
├── app.py               # Web server (local dev shortcut)
├── Dockerfile
├── requirements.txt
├── templates/
│   └── index.html       # Web interface
└── bookworm/
    ├── cache.py         # Cache read/write
    ├── fetcher.py       # Download & clean books
    ├── analysis.py      # lexdiv, topics, entities, summarize
    ├── similarity.py    # Similar books (TF-IDF cosine)
    ├── card.py          # Full book card
    ├── server.py        # Flask app
    └── cli.py           # Argparse CLI
```

---

## How it works

Results are cached as JSON files to avoid recomputing expensive operations.
Books are downloaded from [Project Gutenberg](https://www.gutenberg.org/) and stored locally.

When using Docker, both are persisted in named volumes (`bookworm-cache`, `bookworm-books`).

---

## Dependencies

- `nltk` — tokenization, POS tagging, NER
- `scikit-learn` — LDA topic modeling
- `requests` — book downloading
- `flask` — web interface