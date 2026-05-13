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
    """Insert a listing. Returns True if new, False if already seen (duplicate)."""
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
        return False  # listing_id already exists
    finally:
        conn.close()


def get_price_stats(model):
    """
    Return price statistics for a model using all stored listings.

    Returns a dict with keys: mean, median, count, low, high
    Returns None if fewer than MIN_SAMPLES listings exist.

    Why both mean and median?
      - Median is not affected by a single unusually high or low listing.
        We use it as the reference price when checking for deals.
      - Mean gives a broader sense of the typical market price.
    """
    from config import MIN_SAMPLES  # imported here to avoid circular imports at module load

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT price FROM listings WHERE model = ? AND price > 0 ORDER BY price",
        (model,),
    )
    prices = [row[0] for row in cursor.fetchall()]
    conn.close()

    if len(prices) < MIN_SAMPLES:
        return None

    return {
        "mean":   round(statistics.mean(prices), 2),
        "median": round(statistics.median(prices), 2),
        "count":  len(prices),
        "low":    min(prices),
        "high":   max(prices),
    }
