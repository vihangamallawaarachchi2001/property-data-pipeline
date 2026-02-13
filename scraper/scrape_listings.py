"""
ikman.lk Scraper - FIXED for window.initialData structure
Based on actual page structure from debug analysis
"""
import requests
import re
import json
import datetime
from bs4 import BeautifulSoup
import time
import sys


def fetch_page(url, max_retries=3):
    """Fetch page with proper headers"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(max_retries):
        try:
            print(f"  → Attempt {attempt + 1}/{max_retries}...")
            response = session.get(url, timeout=20)
            response.raise_for_status()

            if "<html" not in response.text.lower():
                raise Exception("Invalid response - possibly blocked")

            return response.text

        except Exception as e:
            print(f"  ❌ Attempt failed: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(3 * (attempt + 1))

    return None


def extract_initial_data(html):
    """
    Extract window.initialData from script tags
    Based on actual structure found in debug:
    Script 1: window.initialData = {"locale":"en","marketLocales":...
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find script containing window.initialData
    script = None
    for s in soup.find_all("script"):
        if s.string and "window.initialData" in s.string:
            script = s
            break

    if not script or not script.string:
        # Try regex search on entire HTML
        match = re.search(
            r'window\.initialData\s*=\s*({[\s\S]*?});?\s*(?:</script>|$)',
            html,
            re.IGNORECASE
        )
        if match:
            return json.loads(match.group(1))
        raise ValueError("Could not find window.initialData script")

    # Extract JSON from the script
    script_content = script.string.strip()

    # Pattern: window.initialData = { ... }
    match = re.search(
        r'window\.initialData\s*=\s*({[\s\S]*?});?\s*$',
        script_content,
        re.MULTILINE
    )

    if not match:
        # Alternative: might be in the middle of script
        match = re.search(
            r'window\.initialData\s*=\s*({.*})',
            script_content,
            re.DOTALL
        )

    if not match:
        raise ValueError("Found script but could not extract JSON data")

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        # Try to find the closing brace more carefully
        data_str = match.group(1)

        # Find the position of "adDetail" and extend to include full object
        if '"adDetail"' in data_str:
            ad_detail_pos = data_str.find('"adDetail"')
            # Try to parse from start to a reasonable end
            # Find the closing brace for the entire object
            brace_count = 0
            in_string = False
            escape_next = False
            end_pos = 0

            for i, char in enumerate(data_str):
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break

            if end_pos > 0:
                cleaned = data_str[:end_pos]
                return json.loads(cleaned)

        raise ValueError(f"JSON decode error: {str(e)}. Data preview: {data_str[:200]}")


def parse_ad_data(initial_data, url):
    """
    Parse ad data from window.initialData structure
    Structure from debug:
    {
      "locale": "en",
      "marketLocales": ["en", "si", "ta"],
      "locations": {...},
      "adDetail": {
        "data": {
          "ad": { ... }  // <-- THIS IS WHAT WE NEED
        }
      }
    }
    """
    # Navigate to ad data
    ad_detail = initial_data.get("adDetail", {})
    ad_data = ad_detail.get("data", {}).get("ad", {})

    if not ad_data or not ad_data.get("id"):
        # Try alternative paths
        if "ad" in initial_data:
            ad_data = initial_data["ad"]
        elif "props" in initial_data:
            ad_data = initial_data["props"].get("pageProps", {}).get("ad", {})

        if not ad_data or not ad_data.get("id"):
            raise ValueError("Ad data not found in initialData structure")

    def get_property(properties, key_name):
        """Extract property value from properties array"""
        if not properties:
            return None
        if isinstance(properties, dict):
            return properties.get(key_name)
        if isinstance(properties, list):
            for prop in properties:
                if isinstance(prop, dict) and prop.get("key") == key_name:
                    return prop.get("value")
        return None

    # 1. listing_id
    listing_id = str(ad_data.get("id", "")).strip()

    # 2. source_url
    source_url = url

    # 3. title
    title = ad_data.get("title", "").strip()

    # 4. property_type
    category = ad_data.get("category", {})
    property_type = category.get("name", "Unknown")

    # 5-6. price & currency
    price_obj = ad_data.get("price", {})
    price = price_obj.get("value")
    currency = price_obj.get("currency", "LKR")

    # 7. location (hierarchical)
    location_parts = []
    for level in ["l3_location", "l2_location", "l1_location", "location"]:
        loc = ad_data.get(level)
        if loc and isinstance(loc, str) and loc.strip():
            location_parts.append(loc.strip())
    location = ", ".join(location_parts) if location_parts else "Unknown"

    # 8. area (raw string)
    area = get_property(ad_data.get("properties", []), "size") or ""

    # 9. nearest_university (requires geocoding API - not on page)
    nearest_university = None

    # 10-11. bedrooms & bathrooms
    bedrooms = get_property(ad_data.get("properties", []), "bedrooms")
    bathrooms = get_property(ad_data.get("properties", []), "bathrooms")

    # 12. area_sqft (parse from area string)
    area_sqft = None
    if area:
        # Look for sqft pattern
        match = re.search(r"([\d,]+)\s*(?:sq\.?ft|square feet|ft²)", area, re.IGNORECASE)
        if match:
            area_sqft = float(match.group(1).replace(",", ""))
        else:
            # Try to extract any number if unit is ambiguous
            num_match = re.search(r"([\d,]+)", area)
            if num_match:
                # Only use if context suggests sqft
                if "sq" in area.lower() or "ft" in area.lower():
                    area_sqft = float(num_match.group(1).replace(",", ""))

    # 13. amenities
    amenities = []
    amenities_raw = ad_data.get("amenities", [])
    if isinstance(amenities_raw, list):
        amenities = [a.get("name") for a in amenities_raw if isinstance(a, dict) and a.get("name")]
    elif isinstance(amenities_raw, dict) and "data" in amenities_raw:
        amenities = [a.get("name") for a in amenities_raw["data"] if isinstance(a, dict) and a.get("name")]

    # 14. description
    description = ad_data.get("description", "").strip()

    # 15-16. contact info (ETHICALLY OMITTED - requires user interaction)
    contact_name = "MANUAL_INTERACTION_REQUIRED"
    contact_phone = "MANUAL_INTERACTION_REQUIRED"

    # 17. image_folder
    image_folder = f"images/{listing_id}/"

    # 18. scraped_date
    scraped_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "listing_id": listing_id,
        "source_url": source_url,
        "title": title,
        "property_type": property_type,
        "price": price,
        "currency": currency,
        "location": location,
        "area": area,
        "nearest_university": nearest_university,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "area_sqft": area_sqft,
        "amenities": amenities,
        "description": description,
        "contact_name": contact_name,
        "contact_phone": contact_phone,
        "image_folder": image_folder,
        "scraped_date": scraped_date
    }


def scrape_listing(url, debug=False):
    """Main scraping function"""
    print(f"\n🔍 Scraping: {url}")

    # Fix URL if it has trailing spaces
    url = url.strip()

    html = fetch_page(url)
    if not html:
        return None

    if debug:
        print("\n🔍 DEBUG: Inspecting structure...")
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script")
        print(f"   Found {len(scripts)} script tags")
        for i, s in enumerate(scripts[:3]):
            if s.string and "initialData" in s.string:
                preview = s.string[:300].replace('\n', ' ')
                print(f"   Script {i} (has initialData): {preview}...")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📄 Saved full HTML to debug_page.html")

    try:
        initial_data = extract_initial_data(html)
        print(f"✅ Extracted initialData - Keys: {list(initial_data.keys())[:5]}")

        ad_data = parse_ad_data(initial_data, url)

        # Display results
        print(f"\n✅ SUCCESS! Listing ID: {ad_data['listing_id']}")
        print(f"   Title: {ad_data['title']}")
        print(f"   Type: {ad_data['property_type']}")
        if ad_data['price']:
            print(f"   Price: {ad_data['currency']} {ad_data['price']:,}")
        print(f"   Location: {ad_data['location']}")
        print(f"   Beds: {ad_data['bedrooms']} | Baths: {ad_data['bathrooms']}", end="")
        if ad_data['area_sqft']:
            print(f" | Area: {ad_data['area_sqft']} sqft")
        else:
            print(f" | Area: {ad_data['area']}")
        if ad_data['amenities']:
            print(f"   Amenities: {', '.join(ad_data['amenities'][:5])}{'...' if len(ad_data['amenities']) > 5 else ''}")

        return ad_data

    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        return None


if __name__ == "__main__":
    debug_mode = "--debug" in sys.argv

    urls = [
        "https://ikman.lk/en/ad/2-storey-5beds-house-rent-in-kelaniya-for-rent-gampaha-7",
        "https://ikman.lk/en/ad/annex-for-rent-in-meegoda-for-rent-colombo-1",
        "https://ikman.lk/en/ad/rooms-for-rent-colombo-1022",
        "https://ikman.lk/en/ad/unfurnished-3br-apartment-in-jaya-road-bambalapitiya-for-rent-for-rent-colombo"
    ]

    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*70}")
        print(f"Processing listing {i}/{len(urls)}")
        print('='*70)

        data = scrape_listing(url, debug=debug_mode)
        if data:
            results.append(data)

        # Rate limiting
        if i < len(urls):
            delay = 8 + (i % 3)
            print(f"\n⏳ Waiting {delay}s before next request...")
            time.sleep(delay)

    # Summary
    print("\n" + "="*70)
    print(f"✅ COMPLETED: {len(results)}/{len(urls)} listings successfully scraped")
    print("="*70)

    if results:
        print("\n📊 RESULTS SUMMARY:")
        for idx, ad in enumerate(results, 1):
            print(f"\n{idx}. {ad['title'][:60]}...")
            print(f"   ID: {ad['listing_id']} | Price: {ad['currency']} {ad['price']:, if ad['price'] else 'N/A'}")
            print(f"   Location: {ad['location']}")

        print("\n💡 IMPORTANT NOTES:")
        print("   • Contact info requires manual interaction (ethically omitted)")
        print("   • nearest_university requires geocoding API (not on page)")
        print("   • For production: Add 10-15s delays and proxy rotation")

        # Optional: Save to JSON
        import json
        with open("scraped_listings.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved results to scraped_listings.json")