"""
Interact with the local gutensearch database.
"""
import logging
import os
from io import StringIO
import pandas as pd
import mysql.connector
import requests


logger = logging.getLogger(__name__)
cnx = mysql.connector.connect(
    user='root', 
    password=os.getenv('MYSQL_ROOT_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database='gutensearch'
    )


def get_catalog() -> pd.DataFrame:
    """Download or update the catalog."""
    logger.debug('Checking catalog')
    # Check for existence
    sql = 'SELECT id, title FROM catalog'
    catalog = pd.read_sql(sql, con=cnx)
    if catalog.empty:  # TODO or if catalog is "stale"
        logger.warning('Local catalog is empty, updating from gutenberg.org')
        new_catalog = get_catalog_from_web()
        write_catalog_to_sql(new_catalog)
        catalog = new_catalog
    else:
        logger.debug('Catalog is available offline')
    return catalog


def get_catalog_from_web() -> pd.DataFrame:
    """Fetch the whole catalog from PG website."""
    catalog_compressed_url = 'https://gutenberg.org/cache/epub/feeds/pg_catalog.csv.gz'
    r = requests.get(catalog_compressed_url)
    if r.status_code == 200:
        logger.debug('Catalog downloaded')
        raw_catalog = pd.read_csv(StringIO(r.text))

    # Only keep text documents (excludes images, databases, etc.)
    text_catalog = raw_catalog.loc[raw_catalog['Type'] == 'Text']
    # Fill nulls with empty strings so Mysql can handle
    text_catalog = text_catalog.fillna('')
    columns = ['Text#', 'Issued', 'Title', 'Language', 'Authors', 'Subjects', 'LoCC', 'Bookshelves']
    catalog = text_catalog[columns]
    logger.debug(f'Preview of downloaded catalog:\n{catalog.head()}')
    return catalog


def write_catalog_to_sql(catalog: pd.DataFrame):
    """Writes catalog to SQL in an upsert / merge."""
    logger.debug('Writing catalog to SQL')
    sql = """
        INSERT IGNORE INTO catalog
        (id, issued, title, language, authors, subjects, locc, bookshelves)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
    """
    cursor = cnx.cursor()
    logger.debug(f'Preview of values to insert: {catalog.head(5).values.tolist()}')
    cursor.executemany(sql, catalog.values.tolist())
    cnx.commit()
    cursor.close()
    logger.debug('Catalog updated')
    return
