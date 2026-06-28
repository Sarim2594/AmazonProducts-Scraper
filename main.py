import sys
import io
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Ensure Windows consoles don't crash on special characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUTPUT_FILE = "results.xlsx"
DELAY_MIN = 3.0
DELAY_MAX = 7.0
REQUEST_TIMEOUT = 20

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

def _text(card, selector):
    el = card.select_one(selector)
    return el.get_text(strip=True) if el else None

def main():
    if len(sys.argv) > 1:
        start_url = sys.argv[1]
    else:
        start_url = input("Enter Amazon Search URL: ").strip()

    if not start_url:
        print("No URL provided. Exiting.")
        return

    session = requests.Session()
    session.headers.update({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    })

    # Basic Amazon session cookies
    session.cookies.set("session-id", "000-0000000-0000000", domain=".amazon.com")
    session.cookies.set("i18n-prefs", "USD", domain=".amazon.com")

    print(f"\nTarget URL: {start_url}")
    print("Warming up session...")
    try:
        session.headers["User-Agent"] = random.choice(USER_AGENTS)
        session.get("https://www.amazon.com/", timeout=REQUEST_TIMEOUT)
        time.sleep(random.uniform(1.5, 3.0))
    except requests.RequestException:
        pass

    all_products = []
    current_url = start_url
    page = 1

    while True:
        print(f"Scraping page {page}...")
        session.headers["User-Agent"] = random.choice(USER_AGENTS)
        time.sleep(random.uniform(0.5, 1.5))

        try:
            resp = session.get(current_url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch page {page}: {e}")
            break

        html_lower = resp.text.lower()
        if 'action="/errors/validatecaptcha"' in resp.text or ('<title>' in resp.text and 'robot check' in html_lower):
            print(f"CAPTCHA detected on page {page}. Stopping.")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select('[data-component-type="s-search-result"]')
        
        if not cards:
            print("No products found on page.")
            break

        print(f"  Found {len(cards)} products.")

        for card in cards:
            asin = card.get("data-asin", "").strip()
            if not asin:
                continue

            title = _text(card, "h2 span") or _text(card, "h2 a span") or "N/A"
            price = _text(card, ".a-price .a-offscreen")
            orig_price_el = card.select(".a-price.a-text-price .a-offscreen")
            original_price = orig_price_el[0].get_text(strip=True) if orig_price_el else None
            discount = _text(card, ".s-coupon-unclipped .a-color-base") or _text(card, "[class*='savingsPercentage']")
            rating = _text(card, ".a-icon-star-small .a-icon-alt") or _text(card, "[class*='a-star'] .a-icon-alt")
            
            review_count = None
            for sel in (".s-underline-text", "a[href*='customerReviews'] .a-size-base", "[aria-label*='stars'] + span .a-size-base"):
                el = card.select_one(sel)
                if el:
                    review_count = el.get_text(strip=True)
                    break

            sponsored = bool(card.select_one("[class*='s-sponsored-label']") or card.select_one(".puis-sponsored-label-text"))
            
            link_el = card.select_one("h2 a[href]") or card.select_one("a.a-link-normal[href]")
            href = link_el["href"] if link_el else ""
            url = f"https://www.amazon.com{href.split('?')[0]}" if href.startswith("/") else (href if href.startswith("http") else f"https://www.amazon.com/dp/{asin}")

            all_products.append({
                "Page": page,
                "Title": title,
                "ASIN": asin,
                "Price": price,
                "Original Price": original_price,
                "Discount": discount,
                "Rating": rating,
                "Reviews": review_count,
                "Sponsored": "Yes" if sponsored else "No",
                "Product URL": url
            })

        print(f"  Running total: {len(all_products)} products")

        next_btn = soup.select_one(".s-pagination-next")
        if next_btn and next_btn.name == "a" and "href" in next_btn.attrs:
            next_href = next_btn["href"]
            current_url = f"https://www.amazon.com{next_href}" if next_href.startswith("/") else next_href
        else:
            print("No 'Next' button found. End of results.")
            break

        page += 1
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        print(f"  Waiting {delay:.1f}s before next request...")
        time.sleep(delay)

    if all_products:
        df = pd.DataFrame(all_products)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\nDone! {len(all_products)} products saved to '{OUTPUT_FILE}'.")
    else:
        print("\nNo products scraped.")

if __name__ == "__main__":
    main()
