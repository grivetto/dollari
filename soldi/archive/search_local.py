import gc
import requests
import json
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def search_places(query):
    if not API_KEY:
        return "Nessuna API Key Google Maps trovata in .env."
        
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query)}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    results = []
    if 'results' in data:
        for place in data['results']:
            # We look for businesses without a website or low rating count
            # TextSearch doesn't always return website directly, but we can see user_ratings_total
            ratings = place.get('user_ratings_total', 0)
            rating = place.get('rating', 0.0)
            name = place.get('name', 'N/A')
            address = place.get('formatted_address', 'N/A')
            
            # Filter criteria for "hidden gems" or low visibility:
            # Low number of reviews (< 50) but decent rating (>= 3.5), or no rating at all.
            if ratings < 50:
                results.append(f"- **{name}**\n  Indirizzo: {address}\n  Recensioni: {ratings} (Voto: {rating})")
                
    return "\n\n".join(results[:10])

if __name__ == "__main__":
    print(search_places("pet care dog sitter veterinario Torino"))
