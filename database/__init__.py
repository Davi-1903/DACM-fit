import sqlite3


def init_database():
    with sqlite3.connect('database/banco.db') as conn:
        with open('database/schema.sql') as f:
            conn.execute(f.read())
