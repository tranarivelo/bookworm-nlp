# Bookworm — NLP Engine for Project Gutenberg

Bookworm analyses books from [Project Gutenberg](https://www.gutenberg.org/) and produces structured **book cards** containing a summary, topic modeling, named entities, lexical statistics, similar books, and a cover image.

It can be used as a **CLI tool** or through a **web interface**, and runs entirely locally via Docker.

---

## Table of contents

1. [Requirements](#requirements)
2. [Quick start with Docker](#quick-start-with-docker)
3. [Quick start (local Python)](#quick-start-local-python)
4. [Web interface](#web-interface)
5. [CLI reference](#cli-reference)
6. [How to find a book ID](#how-to-find-a-book-id)
7. [Caching](#caching)
8. [Project structure](#project-structure)

---

## Requirements

| Method | Requirements |
|--------|-------------|
| Docker | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| Local  | Python 3.11+ |

Docker is the recommended method — no Python setup needed.

---

## Quick start with Docker

**1. Clone the repository**

```bash
git clone https://github.com/EpitechMscProPromo2028/T-AIA-600-PAR_28.git
cd T-AIA-600-PAR_28
```

**2. Build the image** (once)

```bash
docker build -t bookworm .
```

> This step takes a few minutes the first time (downloads Python dependencies and NLP models).

**3. Create persistent volumes** (once)

Volumes store downloaded books, covers and cached results so they survive container restarts.

```bash
docker volume create bookworm-books
docker volume create bookworm-cache
docker volume create bookworm-covers
```

**4. Run a command**

```bash
docker run --rm \
  -v bookworm-books:/app/books \
  -v bookworm-cache:/app/cache \
  -v bookworm-covers:/app/covers \
  bookworm --card 11
```

> Replace `--card 11` with any command from the [CLI reference](#cli-reference).

---

## Quick start (local Python)

**1. Clone and enter the repository**

```bash
git clone https://github.com/EpitechMscProPromo2028/T-AIA-600-PAR_28.git
cd T-AIA-600-PAR_28
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

Activate it:

| Platform | Command |
|----------|---------|
| macOS / Linux | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (Git Bash) | `source .venv/Scripts/activate` |

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Download NLP models**

```bash
python -m nltk.downloader punkt punkt_tab stopwords averaged_perceptron_tagger averaged_perceptron_tagger_eng maxent_ne_chunker_tab wordnet words
```

**5. Run a command**

```bash
python bookworm.py --card 11
```

---

## Web interface

The web interface lets you run any analysis interactively in your browser and export full book cards as PDF.

**Docker:**

```bash
docker run --rm -p 8080:8080 \
  -v bookworm-books:/app/books \
  -v bookworm-cache:/app/cache \
  -v bookworm-covers:/app/covers \
  bookworm --web
```

**Local:**

```bash
python bookworm.py --web
```

Then open **[http://localhost:8080](http://localhost:8080)** in your browser.

### Features

- Select any analysis command from the dropdown
- Enter a book ID, author name, or category
- Results are displayed in a formatted catalogue view
- **PDF export** — generates a full book card as a real text-based PDF (text is selectable)
- **JSON toggle** — view the raw JSON output for any result

---

## CLI reference

```bash
python bookworm.py <command> <value>
```

| Command | Value | Description |
|---------|-------|-------------|
| `--card <ID>` | Book ID | Full book card (summary, topics, entities, stats, similar books, cover) |
| `--summarize <ID>` | Book ID | Automatic extractive summary |
| `--lexdiv <ID>` | Book ID | Lexical diversity metrics (TTR, hapax, token count…) |
| `--topics <ID>` | Book ID | Topic modeling via LDA — returns the main thematic clusters |
| `--entities <ID>` | Book ID | Named entity recognition - extracts characters and locations |
| `--similar <ID>` | Book ID | Finds the 5 most similar books from a built-in reference collection |
| `--author <name>` | Author name | Downloads all books by a given author |
| `--category <name>` | Category name | Downloads all books matching a category or bookshelf |
| `--web` | — | Starts the web interface on port 8080 |

### Examples

```bash
# Full book card for Alice in Wonderland
python bookworm.py --card 11

# Summary of Dracula
python bookworm.py --summarize 345

# Named entities in Moby Dick
python bookworm.py --entities 2701

# Topics in Peter Pan
python bookworm.py --topics 16

# Books similar to Frankenstein
python bookworm.py --similar 84

# Download all books by Arthur Conan Doyle
python bookworm.py --author "Doyle"

# Download all books in the Science Fiction category
python bookworm.py --category "Science Fiction"
```

---

## How to find a book ID

Every book on Project Gutenberg has a numeric ID visible in its URL.

For example, *Alice in Wonderland* is at:
```
https://www.gutenberg.org/ebooks/11
                                 ^^
                              book ID = 11
```

A few popular IDs to get started:

| ID | Title | Author |
|----|-------|--------|
| 11 | Alice's Adventures in Wonderland | Lewis Carroll |
| 84 | Frankenstein | Mary Shelley |
| 345 | Dracula | Bram Stoker |
| 1661 | The Adventures of Sherlock Holmes | Arthur Conan Doyle |
| 2701 | Moby Dick | Herman Melville |
| 16 | Peter Pan | J. M. Barrie |
| 55 | The Wonderful Wizard of Oz | L. Frank Baum |

---

## Caching

All computed results (summaries, entities, topics…) are saved as JSON files in the `cache/` folder. Downloaded books are stored in `books/`, covers in `covers/`.

If a result is already cached, it is loaded instantly without recomputing.

When using Docker with named volumes, the cache persists across container restarts. Without volumes, the cache is lost when the container stops.

---

## Project structure

```
T-AIA-600-PAR_28/
├── bookworm.py          # Entry point — CLI and --web
├── app.py               # Shortcut to start the web server locally
├── Dockerfile
├── requirements.txt
├── pg_catalog.csv       # Project Gutenberg catalogue (for author/category search)
├── templates/
│   ├── index.html       # Web interface
│   └── card_pdf.html    # PDF export template
└── bookworm/
    ├── cache.py         # Cache read/write
    ├── fetcher.py       # Book download, cover download, author/category search
    ├── analysis.py      # Summarization, lexdiv, topic modeling, NER
    ├── similarity.py    # Similar books via TF-IDF cosine similarity
    ├── card.py          # Assembles the full book card
    ├── server.py        # Flask web server and PDF export route
    └── cli.py           # Argparse CLI
```
