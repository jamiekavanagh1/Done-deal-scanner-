import time

from database import init_db, save_listing, get_average_price
from notifier import send_discord_alert
from scraper import search_item

# ── Configuration ──────────────────────────────────────────────────────────────

# Paste your Discord webhook URL here.
# Create one via: Discord Server Settings → Integrations → Webhooks → New Webhook
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# Items to scan.
# Each entry is a dict with:
#   "model"    – the search term sent to DoneDeal
#   "category" – "phones" or "gaming" (controls which section of the site is searched)
#
# To add more items, just copy an existing line and change the model name.
ITEMS = [
    # ── iPhone 12 family ──────────────────────────────────────────────────────
    {"model": "iPhone 12 Mini",     "category": "phones"},
    {"model": "iPhone 12",          "category": "phones"},
    {"model": "iPhone 12 Pro",      "category": "phones"},
    {"model": "iPhone 12 Pro Max",  "category": "phones"},

    # ── iPhone 13 family ──────────────────────────────────────────────────────
    {"model": "iPhone 13 Mini",     "category": "phones"},
    {"model": "iPhone 13",          "category": "phones"},
    {"model": "iPhone 13 Pro",      "category": "phones"},
    {"model": "iPhone 13 Pro Max",  "category": "phones"},

    # ── iPhone 14 family ──────────────────────────────────────────────────────
    {"model": "iPhone 14",          "category": "phones"},
    {"model": "iPhone 14 Plus",     "category": "phones"},
    {"model": "iPhone 14 Pro",      "category": "phones"},
    {"model": "iPhone 14 Pro Max",  "category": "phones"},

    # ── iPhone 15 family ──────────────────────────────────────────────────────
    {"model": "iPhone 15",          "category": "phones"},
    {"model": "iPhone 15 Plus",     "category": "phones"},
    {"model": "iPhone 15 Pro",      "category": "phones"},
    {"model": "iPhone 15 Pro Max",  "category": "phones"},

    # ── iPhone 16 family ──────────────────────────────────────────────────────
    {"model": "iPhone 16",          "category": "phones"},
    {"model": "iPhone 16 Plus",     "category": "phones"},
    {"model": "iPhone 16 Pro",      "category": "phones"},
    {"model": "iPhone 16 Pro Max",  "category": "phones"},

    # ── iPhone 17 family ──────────────────────────────────────────────────────
    {"model": "iPhone 17",          "category": "phones"},
    {"model": "iPhone 17 Air",      "category": "phones"},
    {"model": "iPhone 17 Pro",      "category": "phones"},
    {"model": "iPhone 17 Pro Max",  "category": "phones"},

    # ── Gaming ────────────────────────────────────────────────────────────────
    {"model": "PS5",                "category": "gaming"},
    {"model": "PS5 Pro",            "category": "gaming"},
    {"model": "PS5 Slim",           "category": "gaming"},
]

# How far below the average price a listing must be to trigger an alert.
# 0.25 means 25% cheaper than average.
DISCOUNT_THRESHOLD = 0.25

# How many seconds to wait between full scans (120 = 2 minutes).
SCAN_INTERVAL_SECONDS = 120

# ── Main loop ──────────────────────────────────────────────────────────────────

def scan_once():
    for item in ITEMS:
        model    = item["model"]
        category = item["category"]

        print(f"\nScanning: {model}")
        listings = search_item(model, category)
        print(f"  Found {len(listings)} listing(s) on DoneDeal.")

        new_count = 0
        for listing in listings:
            is_new = save_listing(
                listing_id=listing["id"],
                model=model,
                title=listing["title"],
                price=listing["price"],
                url=listing["url"],
            )

            if not is_new:
                continue  # Already seen — skip

            new_count += 1
            average = get_average_price(model)

            if average is None:
                # Not enough data yet to calculate a meaningful average
                print(
                    f"  [new] {listing['title']} @ €{listing['price']:.0f}"
                    " (building price history — no alert yet)"
                )
                continue

            discount = (average - listing["price"]) / average
            status = f"{discount * 100:.0f}% below avg €{average:.0f}"

            if discount >= DISCOUNT_THRESHOLD:
                print(f"  [DEAL] {listing['title']} @ €{listing['price']:.0f} — {status}")
                send_discord_alert(
                    webhook_url=DISCORD_WEBHOOK_URL,
                    model=model,
                    title=listing["title"],
                    price=listing["price"],
                    average_price=average,
                    url=listing["url"],
                )
            else:
                print(f"  [new]  {listing['title']} @ €{listing['price']:.0f} — {status}")

        if new_count == 0:
            print("  No new listings since last scan.")


def main():
    names = [i["model"] for i in ITEMS]
    print("=== DoneDeal Deal Scanner ===")
    print(f"Watching : {len(ITEMS)} items")
    print(f"Alert    : listings >{DISCOUNT_THRESHOLD * 100:.0f}% below average price")
    print(f"Interval : every {SCAN_INTERVAL_SECONDS // 60} minute(s)\n")

    init_db()

    while True:
        print("─" * 40)
        scan_once()
        print(f"\nSleeping {SCAN_INTERVAL_SECONDS}s until next scan…")
        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
