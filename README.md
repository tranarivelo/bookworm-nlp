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
| `--summarize <ID>` | Book summarization *(coming soon)* |
| `--similar <ID>` | Find similar books *(coming soon)* |
| `--card <ID>` | Full book card *(coming soon)* |

### Examples

```bash
# Lexical diversity of Alice in Wonderland (ID 11)
python bookworm.py --lexdiv 11

# Named entities of Dracula (ID 345)
python bookworm.py --entities 345

# Topic modeling of Peter Pan (ID 16)
python bookworm.py --topics 16
```

---

## Project Structure

```
bookworm/
├── bookworm.py          # Main script
├── Dockerfile           # Docker support
├── requirements.txt     # Python dependencies
├── books/               # Downloaded books (auto-generated)
└── cache/               # Cached results (auto-generated)
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