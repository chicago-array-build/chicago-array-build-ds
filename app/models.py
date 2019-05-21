"""Connect to AWS RDS instance"""
from os import getenv

import psycopg2

if getenv('FLASK_ENV') == 'production':
    DB = psycopg2.connect(
        dbname=environ["DB_NAME"],
        user=environ["DB_USER"],
        password=environ["DB_PWD"],
        host=environ["DB_HOST"],
    )
else:
    DB = None
