"""
Get Project Gutenberg catalog and word frequencies from those books.
"""
import argparse
import logging
import re
from collections import Counter
import os
import sys
import urllib
from urllib.error import HTTPError
import pandas as pd
import tqdm

from gutensearch import database as db
from gutensearch import exceptions as exc


logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    logger.debug(f'Args: {args}')
    try:
        book_id = int(args.query)
    except ValueError:
        logger.info(f"Query '{args.query}' cannot be coerced to an integer ID; treating as word query")
        try:
            query_word(args.query, args)
        except exc.HandledFatalException as e:
            logger.info(e)
            sys.exit(0)
    else:
        query_book(book_id, args)
    return


def parse_args():
    parser = argparse.ArgumentParser(description='Get word frequencies from a Project Gutenberg book.')
    parser.add_argument('query', help='PG book id or a search term')
    parser.add_argument('--limit', type=int, help='Number of search results to return')
    parser.add_argument('-o', '--offline', action='store_true', help='Whether to only use locally cached library for word search')
    parser.add_argument('--csv', action='store_true', help='Output in CSV for use in pipes (does not print book title)')
    return parser.parse_args()


def query_book(id: int, args):
    """Get the top N words by frequency for a given book.

    1) Look for id in frequencies table (has already been calculated and stored)
    2) If not found, fetch book from gutenberg.org
    3) run counter and write to SQL
    4) print title, then words and their frequencies
    5) clean up by removing cached book

    """
    logger.info(f'Querying for book id {id}')
    # Check catalog for title
    catalog = db.get_catalog()
    book = catalog.loc[catalog['id'] == id].squeeze()

    # Check frequencies table for existing counts
    try:
        df_freq = db.get_frequencies(id)
        if df_freq.empty:
            raise exc.FrequenciesNotCachedError('Empty set')
    except exc.FrequenciesNotCachedError:
        fulltext = get_book(id, offline=args.offline)
        freqs = count_frequencies(fulltext)
        db.write_frequencies_to_sql(id, freqs)
        df_freq = pd.DataFrame.from_records(freqs.most_common(), columns=['word', 'frequency'])
    else:
        logger.debug('Book frequencies are cached')
    truncated = df_freq.head(args.limit)
    if args.csv:
        print(truncated.to_csv(index=False))
    else:
        print(book['title'])
        print(truncated.to_string(index=False))
    return


def query_word(word: str, args):
    # if not offline, prompt user for permission to download whole corpus
    # if offline, search for exact term in SQL where freq > 0 and return resulting columns names
    # lookup those names against catalog to get titles
    # print titles in descending order of word frequency
    # TODO: (future) if no exact match, perform fuzzy match and return the top nearest results or prompt user for choice
    logger.info(f'Querying for word "{word}"')
    if args.offline:
        logger.info('"offline" requested; searching only locally cached books')
        df = db.get_word_from_sql(word, limit=args.limit)
    else:
        prompt = ('You have not asked to stay "offline"; downloading the entire Project ' +
            'Gutenberg collection is about 10Gb compressed and may take a while. Do you ' +
            'want to proceed? [y|N] ')
        user_ok = input(prompt)
        if 'y' in user_ok.lower():
            logger.warning('STAND-IN FOR DOWNLOADING ENTIRE LIBRARY')
            # download and unzip to cache dir
            pass
        else:
            logger.info('User chose not to download library, proceeding offline')
            df = db.get_word_from_sql(word, limit=args.limit)
    if args.csv:
        print(df.to_csv(index=False))
    else:
        print(word)
        print('='*25)
        print(df.to_string(index=False))
    return


def get_book(id: int, offline: bool = False) -> str:
    """Get text of book by id.

    First look in cache directory. If the book does not exist in the local cache, download it.

    """
    local_path = os.path.join('/cache', 'epub', str(id), f'pg{id}.txt')
    logger.debug(f'Searching locally for {local_path}')
    if (not os.path.exists(local_path)) & (not offline):
        logger.info(f'{id} not in cache, getting from the web')
        try:
            get_book_from_web(id, target_path=local_path)
        except exc.TxtNotExistError as e:
            logger.error(e)
            sys.exit(1)
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
    try:
        book_file = urllib.request.urlretrieve(book_url, filename=target_path)
    except HTTPError as err:
        if err.code == 404:
            raise exc.TxtNotExistError('Book not in PG as txt file')
        else:
            raise
    logger.debug(f'{id} saved to file')
    return


def count_frequencies(text: str) -> Counter:
    """Get the word frequencies from a text.

    Requires a negative lookahead for words made entirely of digits, otherwise
    is just non-whitespace surrounded by word boundaries.
    """
    words = re.findall(r'\b(?!\d+\b)\w+', text.lower())
    return Counter(words)


if __name__ == '__main__':
    main()
