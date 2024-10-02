"""
Interact with the local gutensearch database.
"""
import logging
import os
from io import StringIO
import pandas as pd
import mysql.connector
import requests

from gutensearch import exceptions as exc

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
        catalog = pd.read_sql(sql, con=cnx)
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


def get_frequencies(id: int) -> pd.DataFrame:
    """Retrieve word frequencies for a given book from cached results."""
    logger.debug('Checking frequencies table')
    id_col = f'id_{id}'
    sql = f'SELECT word, `{id_col}` FROM freqs;'
    try:
        freqs = pd.read_sql(sql, con=cnx)
    except pd.errors.DatabaseError as e:
        logger.info('Failed to find id already in frequencies table')
        raise exc.FrequenciesNotCachedError
    sorted_freqs = freqs.sort_values(by=id_col, ascending=False)
    return sorted_freqs


def write_frequencies_to_sql(id: int, freqs: dict):
    """Writes word frequencies for a single book to the frequencies table.

    Each book will be stored by id as a column in the table, preceeded by "id_"
    to avoid using pure numbers as SQL column names.
    """
    id_col = f'id_{id}'
    cursor = cnx.cursor()
    logger.debug('Writing frequencies to temp table')
    sql_temp_table = f"""
        CREATE TEMPORARY TABLE temp_freqs (
            word VARCHAR(50) PRIMARY KEY,
            frequency INT
        );"""
    cursor.execute(sql_temp_table)
    sql_temp_insert = """
        INSERT INTO temp_freqs (word, frequency) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE frequency = frequency + VALUES(frequency)
        ;"""
    cursor.executemany(sql_temp_insert, freqs.most_common())
    cnx.commit()

    # Merge with main table via upsert
    sql_alter = f"""ALTER TABLE freqs ADD COLUMN `{id_col}` INT DEFAULT 0"""
    try:
        cursor.execute(sql_alter)
    except mysql.connector.errors.ProgrammingError:
        logger.warning('Potentially trying to add an id column that already exists')
        return
    # Update freqs of new book for words already in table
    sql_update = f"""
        UPDATE freqs f JOIN temp_freqs tf ON tf.word = f.word
        SET f.{id_col} = tf.frequency
        ;"""
    cursor.execute(sql_update)
    # Insert new words along with frequency
    sql_insert = f"""
        INSERT INTO freqs (word, {id_col})
        SELECT tf.word, tf.frequency
        FROM temp_freqs tf
        LEFT JOIN freqs f ON f.word = tf.word
        WHERE f.word IS NULL
        ;"""
    cursor.execute(sql_insert)
    cnx.commit()
    cursor.close()
    return


def get_word_from_sql(word: str, limit: int) -> pd.DataFrame:
    """Fetch top n books and frequencies for a given word."""
    cursor = cnx.cursor()
    # get row for word, transpose, sort descending
    sql_search = f"""SELECT * FROM freqs WHERE word = '{word}';"""
    results = pd.read_sql(sql_search, con=cnx)
    # drop the word column as it's not needed
    results = results.drop(columns=['word'])
    transposed = results.T.reset_index()
    transposed.columns = ['id', 'frequency']
    transposed = transposed.astype(dtype={'frequency': int})
    transposed = transposed.sort_values(by='frequency', ascending=False)

    # apply limit
    limit = transposed.head(limit)
    # remove the stub "id_" from book ids in search results in order to join with catalog
    limit['id'] = limit['id'].str.replace('id_', '').astype(int)

    # left join with catalog for titles
    ids_as_array = ",".join([str(x) for x in limit['id'].values])
    sql_catalog = f"""
        SELECT id, title FROM catalog
        WHERE id IN ({ids_as_array})
        ;"""
    logger.debug(f'SQL catalog search for ids:\n{sql_catalog}')
    catalog = pd.read_sql(sql_catalog, con=cnx)
    merged = pd.merge(limit, catalog, how='left', on='id')
    return merged
