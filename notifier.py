import requests


def send_discord_alert(webhook_url, model, title, price, average_price, url):
    """
    Post a deal alert to a Discord channel via a webhook URL.
    Does nothing (prints a warning) if webhook_url is not set.
    """
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL":
        print("  [notifier] Discord webhook not configured — skipping alert.")
        return

    message = (
        "**Cheap iPhone found!**\n"
        f"**{model}**\n"
        f"Title: {title}\n"
        f"Price: €{price:.0f}\n"
        f"Average: €{average_price:.0f}\n"
        f"Link: {url}"
    )

    try:
        response = requests.post(
            webhook_url,
            json={"content": message},
            timeout=10,
        )
        response.raise_for_status()
        print(f"  [notifier] Alert sent for '{title}' @ €{price:.0f}")
    except requests.RequestException as e:
        print(f"  [notifier] Failed to send Discord alert: {e}")
