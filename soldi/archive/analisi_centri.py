import gc
#!/usr/bin/env python3
"""Estrai nomi centri estetici / cura persona dalle pagine Treatwell e dai siti singoli."""
import json, csv, re
from pathlib import Path
from bs4 import BeautifulSoup

OUT_DIR = Path("out_scrape")
REPORT = Path("scrape_report_ext.json")

def extract_treatwell_salons(html_path: Path) -> list:
    """Estrai saloni dalla pagina Treatwell."""
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    salons = []

    # Treatwell usa h2/h3 o div con nomi di saloni
    # pattern: card con nome salone, indirizzo, rating
    for card in soup.select("[class*='venue'], [class*='salon'], [class*='result']"):
        name_el = card.select_one("h2, h3, [class*='name'], [class*='title']")
        addr_el = card.select_one("[class*='address'], [class*='location']")
        rating_el = card.select_one("[class*='rating'], [class*='score']")
        link_el = card.select_one("a[href*='/luogo/']")

        name = name_el.get_text(strip=True) if name_el else None
        addr = addr_el.get_text(strip=True) if addr_el else None
        rating = rating_el.get_text(strip=True) if rating_el else None
        link = link_el["href"] if link_el else None

        if name and len(name) > 2:
            if link and link.startswith("/"):
                link = "https://www.treatwell.it" + link
            salons.append({
                "nome": name,
                "indirizzo": addr or "",
                "rating": rating or "",
                "url_treatwell": link or "",
                "fonte": "Treatwell",
            })

    # fallback: cerca pattern testo per nomi saloni
    if not salons:
        text = soup.get_text("\n", strip=True)
        # cerca linee che sembrano nomi di centri
        lines = text.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            # Treatwell spesso ha il nome seguito da rating tipo "4.8" o "Eccellente"
            if re.match(r'^[A-Z]', line) and 3 < len(line) < 80:
                # check se la linea successiva sembra un indirizzo
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                if any(kw in next_line.lower() for kw in ["torino", "via ", "corso ", "piazza "]):
                    salons.append({
                        "nome": line,
                        "indirizzo": next_line,
                        "rating": "",
                        "url_treatwell": "",
                        "fonte": "Treatwell (testo)",
                    })
    return salons

def extract_single_site_info(html_path: Path, url: str) -> dict:
    """Estrai info base da un sito singolo di centro estetico."""
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    text = soup.get_text(" ", strip=True)

    # cerca telefono
    phone_match = re.search(r'(\+39[\s\-]?\d{2,4}[\s\-]?\d{5,8}|\b0\d{1,3}[\s\-]?\d{5,8}\b|\b3\d{2}[\s\-]?\d{6,7}\b)', text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # cerca email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    email = email_match.group(0) if email_match else ""

    # cerca indirizzo (via/corso/piazza + torino)
    addr_match = re.search(r'((?:Via|Corso|Piazza|Strada|Viale|Largo|Vicolo)\s[^,\n]{3,50},?\s*(?:\d{5}\s*)?Torino)', text, re.I)
    addr = addr_match.group(0).strip() if addr_match else ""

    # cerca social links
    social = []
    for a in soup.find_all("a", href=True):
        h = a["href"].lower()
        if "facebook.com" in h or "instagram.com" in h or "tiktok.com" in h:
            social.append(a["href"])

    # segnali di visibilità
    has_social = len(social) > 0
    text_len = len(text)
    # siti con poco testo = potenzialmente scarsa presenza
    visibility = "alta" if text_len > 10000 and has_social else "media" if text_len > 3000 else "bassa"

    return {
        "nome": title,
        "indirizzo": addr,
        "telefono": phone,
        "email": email,
        "url_sito": url,
        "social": "; ".join(social[:5]),
        "testo_chars": text_len,
        "visibilita": visibility,
        "fonte": "sito diretto",
    }

def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    all_salons = []

    for entry in report:
        if not entry.get("ok"):
            continue
        url = entry["url"]
        host = __import__("urllib.parse", fromlist=["urlparse"]).urlparse(url).netloc
        slug = __import__("slugify").slugify(url)[:120]
        html_path = OUT_DIR / host / f"{slug}.html"

        if not html_path.exists():
            # prova con www
            for d in OUT_DIR.iterdir():
                candidate = d / f"{slug}.html"
                if candidate.exists():
                    html_path = candidate
                    break

        if not html_path.exists():
            continue

        if "treatwell.it" in url:
            salons = extract_treatwell_salons(html_path)
            all_salons.extend(salons)
        else:
            info = extract_single_site_info(html_path, url)
            all_salons.append(info)

    # dedup per nome
    seen = set()
    unique = []
    for s in all_salons:
        key = s["nome"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(s)

    # salva CSV
    csv_path = Path("centri_estetici_torino.csv")
    if unique:
        fieldnames = list(unique[0].keys())
        # unisci tutti i campi possibili
        all_fields = set()
        for s in unique:
            all_fields.update(s.keys())
        fieldnames = sorted(all_fields)

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for s in unique:
                writer.writerow(s)

    # salva JSON
    json_path = Path("centri_estetici_torino.json")
    json_path.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n📊 Totale centri trovati: {len(unique)}")
    print(f"📁 CSV: {csv_path}")
    print(f"📁 JSON: {json_path}")

    # stampa sommario
    for i, s in enumerate(unique, 1):
        vis = s.get("visibilita", "n/d")
        print(f"  {i}. {s['nome'][:60]} | {s.get('indirizzo','')[:40]} | vis: {vis} | fonte: {s['fonte']}")

if __name__ == "__main__":
    main()
