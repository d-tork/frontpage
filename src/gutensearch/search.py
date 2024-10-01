"""
Get Project Gutenberg catalog and word frequencies from those books.
"""
import argparse
import logging
import re
from collections import Counter
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
    logger.info(f'Querying for book id {id}')
    # Look for book in local cache dir
    # If not found, fetch from gutenberg.org and save to cache dir
    # run counter and write to SQL
    # print title, then words and their frequencies
    db.init_catalog()
    with open('/home/dtork/repos/frontpage/test.txt', 'r') as f:
        freqs = get_frequencies(f.read())
    df = pd.DataFrame.from_records(freqs.most_common(), columns=['word', 'frequency'])
    print('Around the World in 80 Days')
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


def get_frequencies(text: str) -> Counter:
    """Get the word frequencies from a text."""
    words = re.findall(r'\w+', text.lower())
    return Counter(words)


if __name__ == '__main__':
    main()
