from bs4 import BeautifulSoup
import logging
from . import config

logger = logging.getLogger(__name__)

def parse_search_page(html):
    """Parse the search results page to get listing URLs and basic info."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    listing_items = soup.select(config.SELECTORS["listing_item"])
    for item in listing_items:
        try:
            link_tag = item.select_one(config.SELECTORS["listing_link"])
            if not link_tag:
                continue

            url = link_tag.get("href")
            if url and not url.startswith("http"):
                url = f"{config.BASE_URL}{url}"

            # Extract basic info available on search page
            title_tag = item.select_one(config.SELECTORS["listing_title"])
            price_tag = item.select_one(config.SELECTORS["listing_price"])
            location_tag = item.select_one(config.SELECTORS["listing_location"])
            image_tag = item.select_one(config.SELECTORS["listing_image"])

            listing = {
                "source_url": url,
                "title": title_tag.get_text(strip=True) if title_tag else "",
                "price": price_tag.get_text(strip=True) if price_tag else "",
                "location": location_tag.get_text(strip=True) if location_tag else "",
                "image_url": image_tag.get("src") if image_tag else None,
                "listing_id": url.split("-")[-1] if url else None
            }

            # Clean up price (remove Rs)
            if listing["price"]:
                listing["price"] = listing["price"].replace("Rs", "").replace(",", "").strip()
                listing["currency"] = "LKR"

            listings.append(listing)

        except Exception as e:
            logger.error(f"Error parsing listing item: {e}")

    return listings

def parse_detail_page(html, url):
    """Parse the detail page to extract more info."""
    soup = BeautifulSoup(html, "html.parser")
    data = {"source_url": url}

    try:
        # Title
        title = soup.select_one("h1.title--3s1R8")
        if title:
            data["title"] = title.get_text(strip=True)

        # Price (if not already from search page, or to update it)
        price = soup.select_one("div.amount--3NTpl")
        if price:
             p_text = price.get_text(strip=True)
             data["price"] = p_text.replace("Rs", "").replace(",", "").strip()
             data["currency"] = "LKR"

        # Description
        desc = soup.select_one("div.description--1nxbC") or soup.find("div", class_=lambda x: x and "description" in x)
        if desc:
            # Check if there is a 'show more' button or similar, usually get full text
            # often description is in p tags
            ps = desc.find_all("p")
            if ps:
                data["description"] = "\n".join([p.get_text(strip=True) for p in ps])
            else:
                data["description"] = desc.get_text(strip=True)

        # Property details (Bedrooms, Bathrooms, Area)
        # These are often in a definition list dl or similar
        # selector: div.word-break--2nyVq (key-value pairs)
        # Or look for specific text

        attributes = {}
        # Try finding all divs with class 'word-break--2nyVq' inside a container
        # Or look for dt/dd pairs
        for dt in soup.find_all("dt"):
            dd = dt.find_next_sibling("dd")
            if dd:
                key = dt.get_text(strip=True).replace(":", "")
                value = dd.get_text(strip=True)
                attributes[key] = value

        # Also check for "Bedrooms: 3" text style

        if "Bedrooms" in attributes:
            data["bedrooms"] = attributes["Bedrooms"]
        if "Bathrooms" in attributes:
            data["bathrooms"] = attributes["Bathrooms"]
        if "House size" in attributes:
            data["area"] = attributes["House size"]
            data["area_sqft"] = attributes["House size"].replace("sqft", "").strip()
        if "Land size" in attributes:
             # if property type is land
             data["area"] = attributes["Land size"]

        # Images
        # Look for gallery images
        # standard is often in a json script or img tags with class gallery
        images = []
        gallery_imgs = soup.select("img.gallery-image--1nS9k") # hypothetical class
        if not gallery_imgs:
             # Try finding all images in the viewing container
             gallery_div = soup.select_one("div.gallery-container") # potential
             if gallery_div:
                 gallery_imgs = gallery_div.find_all("img")

        # Fallback: extract from meta tags or scripts if needed
        # For now, collect what we find
        for img in gallery_imgs:
            src = img.get("src") or img.get("data-src")
            if src:
                images.append(src)

        data["image_urls"] = images

        # Contact logic is tricky as it's often protected behind a button "Show Number"
        # We can trigger it? No, raw HTTP.
        # We might only get the name.
        contact_name = soup.select_one("div.contact-name--m97 Sb")
        if contact_name:
            data["contact_name"] = contact_name.get_text(strip=True)

    except Exception as e:
        logger.error(f"Error parsing detail page {url}: {e}")

    return data
