import gc
import gc
#!/usr/bin/env python3
"""Scraper resiliente per centri estetici / cura persona a Torino."""
import re, json, time, random, sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from slugify import slugify

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

OUT_DIR = Path("out_scrape")
OUT_DIR.mkdir(exist_ok=True)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "close",
}

JS_REQUIRED_PATTERNS = [
    r"enable javascript",
    r"requires javascript",
    r"Please enable JS",
    r"Se non vieni reindirizzato automaticamente",
]

class FetchError(Exception):
    pass

def looks_like_js_required(html: str) -> bool:
    h = html.lower()
    return any(re.search(p, h, re.I) for p in JS_REQUIRED_PATTERNS)

def save_artifacts(url: str, html: str, text: str, meta: dict):
    host = urlparse(url).netloc or "nohost"
    name = slugify(url)[:120]
    (OUT_DIR / host).mkdir(parents=True, exist_ok=True)
    (OUT_DIR / host / f"{name}.html").write_text(html, encoding="utf-8", errors="ignore")
    (OUT_DIR / host / f"{name}.txt").write_text(text, encoding="utf-8", errors="ignore")
    (OUT_DIR / host / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) >= 2]
    return "\n".join(lines)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    retry=retry_if_exception_type(FetchError),
)
def fetch_with_requests(url: str, timeout=20) -> tuple:
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
    meta = {"method": "requests", "status_code": r.status_code, "final_url": r.url}
    if r.status_code in (403, 429):
        raise FetchError(f"HTTP {r.status_code}")
    html = r.text or ""
    if looks_like_js_required(html):
        raise FetchError("JS_REQUIRED")
    return html, meta

def fetch_with_playwright(url: str, timeout_ms=30000) -> tuple:
    if not HAS_PLAYWRIGHT:
        raise FetchError("PLAYWRIGHT_NOT_AVAILABLE")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(
            locale="it-IT",
            user_agent=DEFAULT_HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": DEFAULT_HEADERS["Accept-Language"]},
            viewport={"width": 1366, "height": 768},
        )
        def route_filter(route):
            if route.request.resource_type in ("image", "font", "media"):
                route.abort()
            else:
                route.continue_()
        context.route("**/*", route_filter)
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            html = page.content()
            meta = {"method": "playwright", "final_url": page.url, "title": page.title()}
            return html, meta
        except PlaywrightTimeoutError as e:
            raise FetchError(f"PLAYWRIGHT_TIMEOUT: {e}")
        finally:
            context.close()
            browser.close()

def polite_sleep():
    gc.collect()
            time.sleep(random.uniform(0.8, 2.0))

def fetch_url(url: str) -> dict:
    polite_sleep()
    # 1) HTTP semplice
    try:
        html, meta = fetch_with_requests(url)
        text = extract_text(html)
        save_artifacts(url, html, text, meta)
        print(f"  ✅ {url} via requests ({len(text)} chars)")
        return {"url": url, "ok": True, "meta": meta, "text_len": len(text)}
    except FetchError as e:
        reason = str(e)
        print(f"  ⚠️  requests failed ({reason}), trying Playwright...")
    except Exception as e:
        reason = str(e)
        print(f"  ⚠️  requests exception ({reason}), trying Playwright...")

    # 2) fallback Playwright
    polite_sleep()
    try:
        html, meta = fetch_with_playwright(url)
        text = extract_text(html)
        save_artifacts(url, html, text, meta | {"fallback_reason": reason})
        print(f"  ✅ {url} via Playwright ({len(text)} chars)")
        return {"url": url, "ok": True, "meta": meta, "text_len": len(text), "fallback_reason": reason}
    except Exception as e:
        print(f"  ❌ {url} FAILED ({e})")
        return {"url": url, "ok": False, "error": str(e), "initial_error": reason}

# ─── Discovery: raccolta URL da DuckDuckGo HTML ───
def discover_urls_ddg(query: str, max_results=30) -> list:
    """Cerca su DuckDuckGo HTML e restituisce URL trovate."""
    found = []
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=DEFAULT_HEADERS,
            timeout=20,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.result__a"):
            href = a.get("href", "")
            if "duckduckgo.com/l/" in href:
                # estrai URL reale dal redirect
                from urllib.parse import parse_qs, urlparse as up
                qs = parse_qs(up(href).query)
                real = qs.get("uddg", [None])[0]
                if real:
                    found.append(real)
            elif href.startswith("http"):
                found.append(href)
        # fallback: cerca tutti i link con dominio .it o .com che non siano DDG
        if not found:
            for a in soup.find_all("a", href=True):
                h = a["href"]
                if "duckduckgo.com" not in h and h.startswith("http"):
                    found.append(h)
    except Exception as e:
        print(f"  ⚠️  DDG discovery failed for '{query}': {e}")
    # dedup preservando ordine
    seen = set()
    deduped = []
    for u in found[:max_results]:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return deduped

# ─── Discovery: Treatwell ───
def discover_treatwell_torino() -> list:
    """Scarica la pagina Treatwell estetiste Torino ed estrae link ai saloni."""
    found = []
    try:
        r = requests.get(
            "https://www.treatwell.it/saloni/da-estetista/in-torino-it/",
            headers=DEFAULT_HEADERS,
            timeout=20,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/luogo/" in href or "/saloni/" in href:
                if href.startswith("/"):
                    href = "https://www.treatwell.it" + href
                found.append(href)
    except Exception as e:
        print(f"  ⚠️  Treatwell discovery failed: {e}")
    seen = set()
    return [u for u in found if not (u in seen or seen.add(u))]

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", help="File con URL seed (opzionale)")
    ap.add_argument("--discover", action="store_true", help="Esegui discovery automatica")
    ap.add_argument("--output", default="scrape_report.json")
    args = ap.parse_args()

    all_urls = []

    # Seed file
    if args.urls:
        all_urls += [ln.strip() for ln in Path(args.urls).read_text(encoding="utf-8").splitlines() if ln.strip()]

    # Discovery automatica
    if args.discover:
        queries = [
            "centro estetico torino",
            "salone bellezza donna torino",
            "centro benessere torino",
            "estetica avanzata torino",
            "trattamenti viso corpo torino",
            "epilazione laser torino",
            "manicure pedicure torino",
            "massaggi estetici torino",
            "spa torino",
            "centro estetico san salvario torino",
            "centro estetico crocetta torino",
            "centro estetico mirafiori torino",
            "centro estetico lingotto torino",
            "centro estetico barriera di milano torino",
            "centro estetico santa rita torino",
            "centro estetico borgo vittoria torino",
            "centro estetico cenisia torino",
            "centro estetico vanchiglia torino",
            "centro estetico aurora torino",
            "centro estetico pozzo strada torino",
        ]
        for q in queries:
            print(f"🔍 Discovery: {q}")
            urls = discover_urls_ddg(q)
            print(f"   → {len(urls)} URL trovate")
            all_urls += urls
            polite_sleep()

        print(f"🔍 Discovery: Treatwell Torino")
        tw = discover_treatwell_torino()
        print(f"   → {len(tw)} link Treatwell")
        all_urls += tw

    # Dedup
    seen = set()
    unique = []
    for u in all_urls:
        norm = u.rstrip("/").lower()
        if norm not in seen:
            seen.add(norm)
            unique.append(u)

    # Filtra solo domini plausibili (escludi google, bing, duckduckgo, wikipedia, youtube)
    skip_domains = {"google.", "bing.", "duckduckgo.", "wikipedia.", "youtube.", "amazon.", "ebay."}
    filtered = [u for u in unique if not any(sd in urlparse(u).netloc.lower() for sd in skip_domains)]

    print(f"\n🔎 Scraping {len(filtered)} URL uniche...\n")
    results = []
    for i, u in enumerate(filtered, 1):
        print(f"[{i}/{len(filtered)}] {u}")
        res = fetch_url(u)
        results.append(res)

    Path(args.output).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for r in results if r["ok"])
    fail = len(results) - ok
    print(f"\n📊 Risultati: {ok} OK, {fail} falliti su {len(filtered)} URL")
    print(f"📁 Report: {args.output} | Artefatti: out_scrape/")

if __name__ == "__main__":
    main()
