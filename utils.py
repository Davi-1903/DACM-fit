import sqlite3


FILE = 'database/banco.db'


def script_sql(script: str, values: tuple = ()):
    with sqlite3.connect(FILE) as conn:
        conn.row_factory = sqlite3.Row
        if 'select' in script.lower():
            return conn.execute(script, values).fetchone()
        conn.execute(script, values)
        conn.commit()
