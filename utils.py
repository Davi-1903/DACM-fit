import sqlite3


FILE = 'database/banco.db'


def script_sql(script: str):
    with sqlite3.connect(FILE) as conn:
        if 'select' in script.lower():
            return conn.execute(script).fetchone()
        conn.execute(script)
        conn.commit()
