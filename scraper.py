import json
import requests
from bs4 import BeautifulSoup

# Category → DoneDeal section URL mapping.
# Add new categories here if you want to search different sections of the site.
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


def search_item(model, category="phones"):
    """
    Search DoneDeal for the given model string in the given category.
    Returns a list of dicts: {id, title, price, url}.
    """
    search_url = CATEGORY_URLS.get(category, CATEGORY_URLS["phones"])
    params = {"query": model, "sort": "publishDate", "order": "desc"}

    try:
        response = requests.get(
            search_url, params=params, headers=HEADERS, timeout=15
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  [scraper] Network error for '{model}': {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    listings = _parse_nextjs(soup)
    if not listings:
        print(f"  [scraper] Could not parse listings for '{model}' — page structure may have changed.")
    return listings


# Keep old name as an alias so nothing breaks if called directly
def search_iphones(model):
    return search_item(model, category="phones")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_nextjs(soup):
    """
    DoneDeal is a Next.js app — listings are embedded as JSON in a
    <script id="__NEXT_DATA__"> tag on every search page.
    """
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag or not script_tag.string:
        return []

    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError:
        return []

    raw_listings = _dig_for_listings(data)
    return [_normalise(item) for item in raw_listings if _normalise(item)]


def _dig_for_listings(data):
    """Try several known paths where DoneDeal embeds listing arrays."""
    candidate_paths = [
        ["props", "pageProps", "listings"],
        ["props", "pageProps", "ads"],
        ["props", "pageProps", "searchResults", "listings"],
        ["props", "pageProps", "data", "listings"],
        ["props", "pageProps", "initialData", "listings"],
    ]
    for path in candidate_paths:
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
    """
    Convert a raw DoneDeal listing dict into our standard format.
    Returns None if any required field is missing or invalid.
    """
    try:
        listing_id = str(item.get("id", "")).strip()
        title = item.get("header", item.get("title", "")).strip()

        # Price can be a dict {"amount": 320, "currency": "EUR"} or a plain number
        raw_price = item.get("price", {})
        if isinstance(raw_price, dict):
            price = float(raw_price.get("amount", 0))
        else:
            price = float(raw_price)

        # URL can be relative ("/phones-for-sale/...") or absolute
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
