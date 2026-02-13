
BASE_URL = "https://ikman.lk"
SEARCH_URL = f"{BASE_URL}/en/ads/sri-lanka/property"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Scraper settings
REQUEST_DELAY = 1.5  # Seconds between requests
MAX_RETRIES = 3
TIMEOUT = 10  # Seconds

# Selectors (Based on analysis)
SELECTORS = {
    "listing_item": "li.normal--2QYVk",
    "listing_link": "a.card-link--3ssYv",
    "listing_title": "h2.heading--2eONR", # Found in h2 tag inside the link
    "listing_price": "div.price--3SnqI",
    "listing_location": "div.description--2-ez3", # Contains "Location, Category"
    "listing_image": "img.normal-ad--1TyjD",

    # Detail page selectors (To be verified)
    "detail_title": "h1.title--3s1R8",
    "detail_price": "div.amount--3NTpl",
    "detail_location": "a.subtitle--BuHVd", # or similar
    "detail_description": "div.description--1nxbC",
    "detail_attributes": "div.word-break--2nyVq", # Key-value pairs often here
    "detail_contact": "div.contact-section--2swy-", # Contact section
}

# Storage settings
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
IMAGES_DIR = os.path.join(STORAGE_DIR, "images")
JSON_DIR = os.path.join(STORAGE_DIR, "json")
EXCEL_FILE = os.path.join(STORAGE_DIR, "listings.xlsx") # Keep for reference or removal
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "scraper.log")
