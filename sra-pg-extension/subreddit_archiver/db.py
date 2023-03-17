import psycopg2
import os

here = os.path.abspath(os.path.dirname(__file__))
SCHEMA_FILE = here + "/" + "schema.sql"

def get_schema():
    with open(SCHEMA_FILE) as f:
        return f.read()

def get_connection(file_name, credentials):
    try:
        print('getting connection')
        with psycopg2.connect(
            host=credentials['host'],
            database=credentials['database'],
            user=credentials['username'],
            password=credentials['password'],
            port=credentials['port']
        ) as conn:
            cur = conn.cursor()
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {file_name};")
            conn.commit()
            cur.execute(f"SET search_path TO {file_name};")
            cur.execute(get_schema())
            conn.commit()
    finally:
        return psycopg2.connect(
            host=credentials['host'],
            database=credentials['database'],
            user=credentials['username'],
            password=credentials['password'],
            port=credentials['port'],
            options=f"-c search_path={file_name}"
        )

def insert_posts(db_connection, posts):
    cursor = db_connection.cursor()
    cursor.executemany(
            'INSERT INTO posts VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING',
            posts
            )
    db_connection.commit()

def insert_comments(db_connection, comments):
    cursor = db_connection.cursor()
    cursor.executemany(
            'INSERT INTO comments VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING',
            comments
            )
    db_connection.commit()

def set_kv(db_connection, key, value):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO archive_metadata VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s WHERE archive_metadata.key = %s", (key, value, value, key))
    #cursor.execute("UPDATE archive_metadata SET value = %s WHERE key = %s", (value, key))
    db_connection.commit()

def get_kv(db_connection, key):
    cursor = db_connection.cursor()
    cursor.execute(
        f"SELECT value FROM archive_metadata WHERE key = '{key}'"
        )
    value = cursor.fetchall()
    db_connection.commit()

    if value:
        return value[0][0]
    else:
        raise KeyError
