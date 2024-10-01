"""
Get Project Gutenberg catalog and word frequencies from those books.
"""
import argparse
import logging
import re
from collections import Counter
import os
import urllib
import pandas as pd
import tqdm

from gutensearch import database as db


logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    logger.debug(f'Args: {args}')
    try:
        book_id = int(args.query)
    except ValueError:
        logger.info(f"Query '{args.query}' cannot be coerced to an integer ID; treating as word query")
        query_word(args.query, args)
    else:
        query_book(book_id, args)
    return


def parse_args():
    parser = argparse.ArgumentParser(description='Get word frequencies from a Project Gutenberg book.')
    parser.add_argument('query', help='PG book id or a search term')
    parser.add_argument('--limit', type=int, help='Number of search results to return')
    parser.add_argument('--offline', action='store_true', help='Whether to only use locally cached library')
    return parser.parse_args()


def query_book(id: int, args):
    """Get the top N words by frequency for a given book.

    1) Look for book in local cache dir
    2) If not found, fetch from gutenberg.org and save to cache dir
    3) run counter and write to SQL
    4) print title, then words and their frequencies

    """
    logger.info(f'Querying for book id {id}')
    catalog = db.get_catalog()
    book = catalog.loc[catalog['id'] == id].squeeze()
    print(book['title'])

    # Check for book in local cache

    fulltext = get_book(id, offline=args.offline)
    freqs = get_frequencies(fulltext)
    df = pd.DataFrame.from_records(freqs.most_common(), columns=['word', 'frequency'])
    print(df.head(args.limit))
    return


def query_word(word: str, args):
    # if not offline, prompt user for permission to download whole corpus
    # if offline, search for exact term in SQL where freq > 0 and return resulting columns names
    # lookup those names against catalog to get titles
    # print titles in descending order of word frequency
    # TODO: (future) if no exact match, perform fuzzy match and return the top nearest results or prompt user for choice
    logger.info(f'Querying for word "{word}"')
    return


def get_book(id: int, offline: bool = False) -> str:
    """Get text of book by id.

    First look in cache directory. If the book does not exist in the local cache, download it.

    """
    local_path = os.path.join('/cache', 'epub', str(id), f'pg{id}.txt')
    logger.debug(f'Searching locally for {local_path}')
    if (not os.path.exists(local_path)) & (not offline):
        logger.info(f'{id} not in cache, getting from the web')
        get_book_from_web(id, target_path=local_path)
    else:
        logger.debug('Book is available offline')
    try:
        with open(local_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error('Book failed to store locally.')
        raise
    return


def get_book_from_web(id: int, target_path: str):
    """Download specific book from PG and store locally."""
    # Create destination directories in cache
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    # Create and fetch by URL
    filename = os.path.basename(target_path)
    base_url = 'https://gutenberg.org/cache/epub/'
    book_url = urllib.parse.urljoin(base_url, f'{id}/{filename}')
    logger.debug(f'Fetching {book_url}')
    book_file = urllib.request.urlretrieve(book_url, filename=target_path)
    logger.debug(f'{id} saved to file')
    return


def get_frequencies(text: str) -> Counter:
    """Get the word frequencies from a text."""
    words = re.findall(r'\w+', text.lower())
    return Counter(words)


if __name__ == '__main__':
    main()
