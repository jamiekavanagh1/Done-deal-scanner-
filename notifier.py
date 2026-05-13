import requests


def send_discord_alert(webhook_url, model, title, price, stats, url):
    """
    Post a deal alert to Discord.

    stats: dict returned by database.get_price_stats()
           keys: mean, median, count, low, high

    Does nothing if webhook_url has not been configured.
    """
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL":
        print("  [notifier] Discord webhook not configured — skipping alert.")
        return

    saving = stats["median"] - price
    pct    = (saving / stats["median"]) * 100

    message = (
        "**Cheap deal found!**\n"
        f"**{model}**\n"
        f"Title:   {title}\n"
        f"Price:   €{price:.0f}  (saving ~€{saving:.0f} / {pct:.0f}% off)\n"
        f"Median:  €{stats['median']:.0f}  |  Avg: €{stats['mean']:.0f}  ({stats['count']} listings)\n"
        f"Link:    {url}"
    )

    try:
        response = requests.post(webhook_url, json={"content": message}, timeout=10)
        response.raise_for_status()
        print(f"  [notifier] Alert sent: '{title}' @ €{price:.0f}")
    except requests.RequestException as e:
        print(f"  [notifier] Failed to send Discord alert: {e}")
