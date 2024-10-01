"""
Get Project Gutenberg catalog and word frequencies from those books.
"""
import argparse
import logging
import re
from collections import Counter
import pandas as pd
import tqdm


logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    if args.query == 'init':
        init_catalog()
    else:
        logger.info(f'Args: {args}')
    return


def parse_args():
    parser = argparse.ArgumentParser(description='Get word frequencies from a Project Gutenberg book.')
    parser.add_argument('query', help='PG book id or a search term')
    parser.add_argument('--limit', type=int, help='Number of search results to return')

    # Subparser for management of database/cache
    # subparser not actually used; this code generates the help message but ``query`` is checked for "init"
    subparsers = parser.add_subparsers(title='subcommands', dest='subparser_name')
    parser_init = subparsers.add_parser('init', help='Download catalog from Project Gutenberg')
    return parser.parse_args()


def init_catalog():
    """Download or update the catalog."""
    logger.info('Initializing catalog')


if __name__ == '__main__':
    main()
