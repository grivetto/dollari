import gc
import requests
import json
import urllib.parse
from bs4 import BeautifulSoup

def search_duckduckgo(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for a in soup.find_all('a', class_='result__url', href=True):
        results.append(a['href'])
    return results

print(search_duckduckgo("site:paginegialle.it idraulico torino"))
