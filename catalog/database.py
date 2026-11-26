

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.getenv("CATALOG_DB", os.path.join(BASE_DIR, "catalog.db"))

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM books")

    if cursor.fetchone()[0] == 0:
        books = [
            (1, "How to get a good grade in DOS in 40 minutes a day",
             "Distributed Systems", 10, 40),

            (2, "RPCs for Noobs",
             "Distributed Systems", 5, 50),

            (3, "Xen and the Art of Surviving Undergraduate School",
             "Undergraduate School", 8, 60),

            (4, "Cooking for the Impatient Undergrad",
             "Undergraduate School", 12, 35)
        ]

        cursor.executemany("""
            INSERT INTO books (id, title, topic, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        """, books)

    conn.commit()
    conn.close()

