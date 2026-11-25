import sqlite3
import os
from datetime import datetime

# Store the database in a persistent location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.getenv(
    "ORDER_DB",
    os.path.join(BASE_DIR, "orders.db")
)


def get_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# Create the orders table if it does not exist
def initialize_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Save a successful purchase
def save_order(book_id, book_title, price):
    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO orders (book_id, book_title, price, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        book_id,
        book_title,
        price,
        datetime.now().isoformat(timespec="seconds")
    ))

    order_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return order_id
