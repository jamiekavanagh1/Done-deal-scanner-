import time

from database import init_db, save_listing, get_average_price
from notifier import send_discord_alert
from scraper import search_iphones

# ── Configuration ──────────────────────────────────────────────────────────────

# Paste your Discord webhook URL here.
# Create one via: Discord Server Settings → Integrations → Webhooks → New Webhook
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# iPhone models to scan.
# To add more models later, just append to this list, e.g. "iPhone 15 Pro".
MODELS = [
    "iPhone 12",
    "iPhone 13",
    "iPhone 14",
]

# How far below the average price a listing must be to trigger an alert.
# 0.25 means 25% cheaper than average.
DISCOUNT_THRESHOLD = 0.25

# How many seconds to wait between full scans (120 = 2 minutes).
SCAN_INTERVAL_SECONDS = 120

# ── Main loop ──────────────────────────────────────────────────────────────────

def scan_once():
    for model in MODELS:
        print(f"\nScanning: {model}")
        listings = search_iphones(model)
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
    print("=== DoneDeal iPhone Scanner ===")
    print(f"Models : {', '.join(MODELS)}")
    print(f"Alert  : listings >{DISCOUNT_THRESHOLD * 100:.0f}% below average price")
    print(f"Interval: every {SCAN_INTERVAL_SECONDS // 60} minute(s)\n")

    init_db()

    while True:
        print("─" * 40)
        scan_once()
        print(f"\nSleeping {SCAN_INTERVAL_SECONDS}s until next scan…")
        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
