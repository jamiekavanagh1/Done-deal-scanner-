import json
import requests
from bs4 import BeautifulSoup

# Category → DoneDeal section URL.
# Add new categories here if you need to search other parts of the site.
CATEGORY_URLS = {
    "phones": "https://www.donedeal.ie/phones-for-sale",
    "gaming": "https://www.donedeal.ie/gaming-for-sale",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IE,en;q=0.9",
}

# Listings outside this price range are almost certainly errors or unrelated items.
MIN_PRICE = 50
MAX_PRICE = 5_000


def search_item(model, category="phones", all_models=None):
    """
    Search DoneDeal for `model` within the given category.

    all_models: full list of tracked model names — used to filter out
                more-specific variants sneaking into results.
                e.g. searching "iPhone 14 Pro" should not return "iPhone 14 Pro Max".

    Returns a list of dicts: {id, title, price, url}
    """
    search_url = CATEGORY_URLS.get(category, CATEGORY_URLS["phones"])
    params = {"query": model, "sort": "publishDate", "order": "desc"}

    try:
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  [scraper] Network error for '{model}': {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    raw = _parse_nextjs(soup)

    if not raw:
        print(f"  [scraper] Could not parse listings for '{model}' — page structure may have changed.")
        return []

    # Work out which words after this model name indicate a different variant
    exclusions = _build_exclusions(model, all_models or [model])
    filtered = [l for l in raw if _is_match(l, model, exclusions)]

    removed = len(raw) - len(filtered)
    if removed:
        print(f"  [scraper] Removed {removed} non-matching / out-of-range listing(s).")

    return filtered


# ---------------------------------------------------------------------------
# Exact-model matching
# ---------------------------------------------------------------------------

def _build_exclusions(model, all_models):
    """
    Auto-detect which extra words mark a more-specific variant of this model.

    Example:
      model      = "iPhone 14 Pro"
      all_models = [..., "iPhone 14 Pro Max", ...]
      result     = {"max"}   ← titles containing "Pro Max" will be excluded

    Example:
      model      = "PS5"
      all_models = [..., "PS5 Digital Edition", ...]
      result     = {"digital"}
    """
    model_lower = model.lower()
    extra_words = set()
    for other in all_models:
        other_lower = other.lower()
        if other_lower != model_lower and other_lower.startswith(model_lower + " "):
            remainder = other_lower[len(model_lower):].strip()
            if remainder:
                extra_words.add(remainder.split()[0])
    return extra_words


def _is_match(listing, model, exclusions):
    """
    Return True only when the listing is genuinely for this specific model.

    Rules:
      1. The model name must appear somewhere in the title.
      2. The word immediately after the model name in the title must not be
         one of the exclusion words (which would make it a different variant).
      3. The price must fall within MIN_PRICE … MAX_PRICE.
    """
    title_lower = listing["title"].lower()
    model_lower = model.lower()

    if model_lower not in title_lower:
        return False

    if exclusions:
        pos = title_lower.find(model_lower)
        remainder = title_lower[pos + len(model_lower):].strip()
        for word in exclusions:
            if remainder.startswith(word):
                return False

    if not (MIN_PRICE <= listing["price"] <= MAX_PRICE):
        return False

    return True


# ---------------------------------------------------------------------------
# DoneDeal Next.js page parser
# ---------------------------------------------------------------------------

def _parse_nextjs(soup):
    """
    DoneDeal is a Next.js app — listing data is embedded as JSON inside a
    <script id="__NEXT_DATA__"> tag on every search-results page.
    """
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag or not script_tag.string:
        return []

    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError:
        return []

    raw_listings = _dig_for_listings(data)
    return [item for item in (_normalise(r) for r in raw_listings) if item]


def _dig_for_listings(data):
    """Try several known paths where DoneDeal stores listing arrays."""
    paths = [
        ["props", "pageProps", "listings"],
        ["props", "pageProps", "ads"],
        ["props", "pageProps", "searchResults", "listings"],
        ["props", "pageProps", "data", "listings"],
        ["props", "pageProps", "initialData", "listings"],
    ]
    for path in paths:
        obj = data
        try:
            for key in path:
                obj = obj[key]
            if isinstance(obj, list) and obj:
                return obj
        except (KeyError, TypeError):
            continue
    return []


def _normalise(item):
    """Convert a raw DoneDeal listing dict to our standard {id, title, price, url} format."""
    try:
        listing_id = str(item.get("id", "")).strip()
        title      = item.get("header", item.get("title", "")).strip()

        raw_price = item.get("price", {})
        price = float(raw_price.get("amount", 0)) if isinstance(raw_price, dict) else float(raw_price)

        friendly = item.get("friendlyUrl", item.get("url", "")).strip()
        if friendly.startswith("http"):
            url = friendly
        elif friendly:
            url = "https://www.donedeal.ie/" + friendly.lstrip("/")
        else:
            url = ""

        if listing_id and title and price > 0 and url:
            return {"id": listing_id, "title": title, "price": price, "url": url}
    except (ValueError, TypeError, AttributeError):
        pass
    return None
