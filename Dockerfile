FROM python:3.11-slim

WORKDIR /app

# Copie et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Télécharge les ressources NLTK nécessaires
RUN python -c "\
import nltk; \
nltk.download('punkt'); \
nltk.download('punkt_tab'); \
nltk.download('stopwords'); \
nltk.download('averaged_perceptron_tagger'); \
nltk.download('averaged_perceptron_tagger_eng'); \
nltk.download('maxent_ne_chunker_tab'); \
nltk.download('wordnet'); \
nltk.download('words')"

# Copie le code
COPY . .

ENTRYPOINT ["python", "bookworm.py"]