import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_alert(token, chat_id, model, title, price, stats, url):
    """
    Send a deal alert via Telegram.

    stats: dict returned by database.get_price_stats()
           keys: mean, median, count, low, high
    """
    saving = stats["median"] - price
    pct    = (saving / stats["median"]) * 100

    # Uses HTML parse_mode — <b> for bold, no special escaping needed
    message = (
        "<b>Cheap deal found!</b>\n"
        f"<b>{model}</b>\n\n"
        f"Title:   {title}\n"
        f"Price:   €{price:.0f}  (saving ~€{saving:.0f} / {pct:.0f}% off)\n"
        f"Median:  €{stats['median']:.0f}  |  Avg: €{stats['mean']:.0f}  ({stats['count']} listings)\n\n"
        f"<a href=\"{url}\">View listing</a>"
    )

    api_url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"  [notifier] Telegram alert sent: '{title}' @ €{price:.0f}")
    except requests.RequestException as e:
        print(f"  [notifier] Failed to send Telegram alert: {e}")
