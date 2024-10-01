"""
Interact with the local gutensearch database.
"""
import logging
from io import StringIO
import pandas as pd
import mysql.connector
import requests


logger = logging.getLogger(__name__)


def init_catalog():
    """Download or update the catalog."""
    logger.info('Initializing catalog')
    catalog_compressed_url = 'https://gutenberg.org/cache/epub/feeds/pg_catalog.csv.gz'
    r = requests.get(catalog_compressed_url)
    if r.status_code == 200:
        catalog = pd.read_csv(StringIO(r.text))
    logger.info('Catalog downloaded')
    print(catalog.info())
    return
