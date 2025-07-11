from utils import script_sql


def init_database():
    with open('database/schema.sql') as f:
        script_sql(f.read())
