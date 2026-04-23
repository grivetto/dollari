import os
import json
import hmac
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

# Load API keys from .env
CRYPTOCOM_API_KEY = os.getenv('CRYPTOCOM_API_KEY')
CRYPTOCOM_API_SECRET = os.getenv('CRYPTOCOM_API_SECRET')

class CryptoComBot:
    def __init__(self):
        self.api_key = CRYPTOCOM_API_KEY
        self.api_secret = CRYPTOCOM_API_SECRET
        self.base_url = 'https://api.crypto.com/v2'

    def generate_signature(self, method,
