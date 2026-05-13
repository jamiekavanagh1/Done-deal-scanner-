import time

import config
from database import init_db, save_listing, get_price_stats
from notifier import send_discord_alert
from scraper import search_item

# Pre-build the full list of model names once — passed to the scraper so it
# can filter out more-specific variants from search results automatically.
ALL_MODELS = [item["model"] for item in config.ITEMS]


def scan_once():
    for item in config.ITEMS:
        model    = item["model"]
        category = item["category"]

        print(f"\n[{category}] {model}")
        listings = search_item(model, category, ALL_MODELS)
        print(f"  {len(listings)} matching listing(s) found.")

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
                continue  # Already in database — skip

            new_count += 1
            stats = get_price_stats(model)

            if stats is None:
                # Not enough data yet — just log and move on
                print(f"  [new]  {listing['title']} @ €{listing['price']:.0f}"
                      f"  (need {config.MIN_SAMPLES} samples for alerts — collecting...)")
                continue

            # Use median as the reference price — it ignores outliers better than mean
            discount = (stats["median"] - listing["price"]) / stats["median"]
            pct_str  = f"{discount * 100:.0f}%"

            if discount >= config.DISCOUNT_THRESHOLD:
                print(f"  [DEAL] {listing['title']}")
                print(f"         €{listing['price']:.0f} — {pct_str} below median €{stats['median']:.0f}")
                send_discord_alert(
                    webhook_url=config.DISCORD_WEBHOOK_URL,
                    model=model,
                    title=listing["title"],
                    price=listing["price"],
                    stats=stats,
                    url=listing["url"],
                )
            else:
                sign = "below" if discount > 0 else "above"
                print(f"  [new]  {listing['title']} @ €{listing['price']:.0f}"
                      f"  ({pct_str} {sign} median €{stats['median']:.0f})")

        if new_count == 0:
            print("  No new listings since last scan.")


def main():
    print("=" * 50)
    print("       DoneDeal Deal Scanner")
    print("=" * 50)
    print(f"Products : {len(config.ITEMS)}")
    print(f"Alert    : >{config.DISCOUNT_THRESHOLD * 100:.0f}% below median price")
    print(f"Interval : every {config.SCAN_INTERVAL_SECONDS // 60} minute(s)")
    print(f"Samples  : alerts need ≥{config.MIN_SAMPLES} listings per product")
    print("=" * 50)

    init_db()

    while True:
        scan_once()
        print(f"\n{'─' * 50}")
        print(f"Next scan in {config.SCAN_INTERVAL_SECONDS}s  "
              f"(Ctrl+C to stop)")
        print(f"{'─' * 50}")
        time.sleep(config.SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
