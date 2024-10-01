"""
Get Project Gutenberg catalog and word frequencies from those books.
"""
import argparse
import logging
import re
from collections import Counter
import pandas as pd
import tqdm


logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    logger.debug(f'Args: {args}')
    try:
        book_id = int(args.query)
    except ValueError:
        logger.info(f"Query '{args.query}' cannot be coerced to an integer ID; treating as word query")
        query_word(args.query)
    else:
        query_book(book_id)
    return


def parse_args():
    parser = argparse.ArgumentParser(description='Get word frequencies from a Project Gutenberg book.')
    parser.add_argument('query', help='PG book id or a search term')
    parser.add_argument('--limit', type=int, help='Number of search results to return')
    return parser.parse_args()


def init_catalog():
    """Download or update the catalog."""
    logger.info('Initializing catalog')
    return


def query_book(id: int):
    logger.info(f'Querying for book id {id}')
    return


def query_word(word: str):
    logger.info(f'Querying for word "{word}"')
    return


if __name__ == '__main__':
    main()
