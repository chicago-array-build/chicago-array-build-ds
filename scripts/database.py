import datetime
import os
import urllib.parse as up
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ["DATABASE_URL_DEV"]
DATA_DIR = Path(__file__).parents[1] / 'data'


def get_db_conn():
    up.uses_netloc.append("postgres")
    url = up.urlparse(DB_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )

    return conn


def initial_schema_creation():
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute(open(str(DATA_DIR / 'public' / 'schema.sql'), 'r').read())
        conn.commit()
    except Exception:
        raise
    finally:
        cur.close()
        conn.close()

    return None


def populate_user():
    user = {
        'id': 1,
        'bg_high': 200,
        'bg_low': 55,
        'bg_target_top': 140,
        'bg_target_bottom': 70,
        'height': 540,
        'weight': 165,
        'birthdate': datetime.date(1992, 1, 1),
        'gender': 'Female',
        'diagnosis_date': datetime.date(2007, 1, 1),
        'diabetes_type': 'Type 1',
        'username': 'userone',
        'password': 'pass_1',
    }

    conn = get_db_conn()
    cur = conn.cursor()

    SQL = f"""INSERT INTO "public"."user" ({', '.join(user.keys())}) VALUES ({', '.join(['%s'] * len(user))})"""
    cur.execute(SQL, tuple(user.values()))
    conn.commit()
