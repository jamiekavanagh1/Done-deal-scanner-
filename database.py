import sqlite3
import statistics

DB_FILE = "deals.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id  TEXT    UNIQUE,
            model       TEXT    NOT NULL,
            title       TEXT    NOT NULL,
            price       REAL    NOT NULL,
            url         TEXT    NOT NULL,
            seen_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_listing(listing_id, model, title, price, url):
    """Insert a listing. Returns True if new, False if already seen."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO listings (listing_id, model, title, price, url) VALUES (?, ?, ?, ?, ?)",
            (listing_id, model, title, price, url),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_average_price(model):
    """Return the mean price for a model, or None if fewer than 5 samples."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT price FROM listings WHERE model = ? AND price > 0",
        (model,),
    )
    prices = [row[0] for row in cursor.fetchall()]
    conn.close()

    if len(prices) < 5:
        return None
    return statistics.mean(prices)
