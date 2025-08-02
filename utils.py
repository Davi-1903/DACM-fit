import sqlite3


FILE = 'database/banco.db'


def script_sql(script: str, values: tuple = ()):
    with sqlite3.connect(FILE) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        if 'select' in script.lower():
            return conn.execute(script, values).fetchone()
        conn.execute(script, values)
        conn.commit()

def script_sql_all(script: str, values: tuple = ()):
    with sqlite3.connect(FILE) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn.execute(script, values).fetchall()

