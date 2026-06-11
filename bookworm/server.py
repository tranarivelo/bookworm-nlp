import io
import os
from flask import Flask, render_template, request, jsonify, send_file, abort

from .cache import save_to_cache, load_from_cache
from .fetcher import get_clean_text, get_books_by_author, get_books_by_category
from .analysis import calculate_lexdiv, extract_topics, extract_entities, summarize_book
from .similarity import get_similar_books
from .card import generate_book_card

app = Flask(__name__, template_folder='../templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run():
    data = request.json
    command = data.get('command')
    value = data.get('value', '').strip()

    if not value:
        return jsonify({'error': 'Aucune valeur fournie.'}), 400

    try:
        if command == 'lexdiv':
            book_id = int(value)
            result = load_from_cache(book_id, 'lexdiv')
            if result is None:
                result = calculate_lexdiv(get_clean_text(book_id))
                save_to_cache(book_id, 'lexdiv', result)

        elif command == 'topics':
            book_id = int(value)
            result = load_from_cache(book_id, 'topics')
            if result is None:
                result = extract_topics(get_clean_text(book_id))
                save_to_cache(book_id, 'topics', result)

        elif command == 'entities':
            book_id = int(value)
            result = load_from_cache(book_id, 'entities')
            if result is None:
                result = extract_entities(get_clean_text(book_id))
                save_to_cache(book_id, 'entities', result)

        elif command == 'summarize':
            book_id = int(value)
            result = load_from_cache(book_id, 'summarize')
            if result is None:
                result = summarize_book(get_clean_text(book_id))
                save_to_cache(book_id, 'summarize', result)

        elif command == 'similar':
            book_id = int(value)
            result = load_from_cache(book_id, 'similar')
            if result is None:
                result = get_similar_books(book_id)
                save_to_cache(book_id, 'similar', result)

        elif command == 'card':
            result = generate_book_card(int(value))

        elif command == 'author':
            result = get_books_by_author(value)

        elif command == 'category':
            result = get_books_by_category(value)

        else:
            return jsonify({'error': f"Commande inconnue : {command}"}), 400

        return jsonify({'result': result})

    except ValueError:
        return jsonify({'error': 'ID de livre invalide (entier attendu).'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export/pdf/<int:book_id>')
def export_pdf(book_id):
    from weasyprint import HTML
    card = generate_book_card(book_id)
    html = render_template('card_pdf.html', card=card, book_id=book_id)
    pdf_bytes = HTML(string=html, base_url=request.host_url).write_pdf()
    title = (card.get('info', {}).get('title') or f'book-{book_id}')
    title = ''.join(c if c.isalnum() or c in ' -' else '' for c in title).strip().replace(' ', '-')[:60]
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{title}.pdf'
    )


@app.route('/cover/<int:book_id>')
def cover(book_id):
    filepath = os.path.join('covers', f'{book_id}.jpg')
    if os.path.exists(filepath):
        return send_file(os.path.abspath(filepath), mimetype='image/jpeg')
    abort(404)


def run_server(host='0.0.0.0', port=8080):
    app.run(host=host, port=port)
