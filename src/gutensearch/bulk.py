"""
Process the entire library.
"""

from tqdm import tqdm

from gutensearch import database as db
from gutensearch import exceptions as exc
from gutensearch.search import get_book, filter_header_and_footer, count_frequencies


def run_bulk():
    catalog = db.get_catalog()
    failures = []
    for id in tqdm(catalog['id'].head(20).values(), total=20):
        try:
            process_and_store_counts(id)
        except Exception as e:
            failures.append((id, e))

    with open('/cache/failures.txt', 'w') as f:
        f.write('\n'.join([f'{a}\t{b}' for a, b in failures]))
    return


def process_and_store_counts(id: int):
    """Load book, count words, store in SQL."""
    fulltext = get_book(id, offline=True)
    try:
        text = filter_header_and_footer(fulltext)
    except exc.HeaderFooterNotFoundError as e:
        text = fulltext
    freqs = count_frequencies(text, include_stopwords=False)
    db.write_frequencies_to_sql(id, freqs)
    return
        


if __name__ == '__main__':
    run_bulk()

