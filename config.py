# ── Discord ────────────────────────────────────────────────────────────────────
# Create a webhook: Discord Server Settings → Integrations → Webhooks → New Webhook
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# ── Scanner behaviour ──────────────────────────────────────────────────────────
SCAN_INTERVAL_SECONDS = 120   # How often to scan (2 minutes)
DISCOUNT_THRESHOLD    = 0.25  # Alert when price is this far below median (25%)
MIN_SAMPLES           = 5     # Minimum listings needed before alerts fire

# ── Products to track ──────────────────────────────────────────────────────────
# Each entry needs:
#   "model"    – the search term sent to DoneDeal (be specific)
#   "category" – "phones" or "gaming" (controls which section of DoneDeal is searched)
#
# To add a new product: copy any line below and change the model name.
# To remove a product: delete or comment out its line.

ITEMS = [
    # ── iPhones ───────────────────────────────────────────────────────────────
    {"model": "iPhone 13",           "category": "phones"},
    {"model": "iPhone 13 Pro",       "category": "phones"},
    {"model": "iPhone 13 Pro Max",   "category": "phones"},
    {"model": "iPhone 14",           "category": "phones"},
    {"model": "iPhone 14 Pro",       "category": "phones"},
    {"model": "iPhone 14 Pro Max",   "category": "phones"},
    {"model": "iPhone 15",           "category": "phones"},
    {"model": "iPhone 15 Pro",       "category": "phones"},
    {"model": "iPhone 15 Pro Max",   "category": "phones"},
    {"model": "iPhone 16",           "category": "phones"},
    {"model": "iPhone 16 Pro",       "category": "phones"},
    {"model": "iPhone 16 Pro Max",   "category": "phones"},
    {"model": "iPhone 17",           "category": "phones"},
    {"model": "iPhone 17 Pro",       "category": "phones"},
    {"model": "iPhone 17 Pro Max",   "category": "phones"},

    # ── Gaming ────────────────────────────────────────────────────────────────
    {"model": "PS5",                 "category": "gaming"},
    {"model": "PS5 Digital Edition", "category": "gaming"},
]
