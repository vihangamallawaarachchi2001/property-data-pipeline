
import os
import json
import logging
import requests
from . import config

logger = logging.getLogger(__name__)

def init_storage():
    """Initialize storage directories."""
    if not os.path.exists(config.STORAGE_DIR):
        os.makedirs(config.STORAGE_DIR)
    if not os.path.exists(config.IMAGES_DIR):
        os.makedirs(config.IMAGES_DIR)
    if not os.path.exists(config.JSON_DIR):
        os.makedirs(config.JSON_DIR)
    logger.info(f"Initialized storage directories at {config.STORAGE_DIR}")

def get_existing_ids():
    """Get list of existing listing IDs to avoid duplicates."""
    if not os.path.exists(config.JSON_DIR):
        return set()

    try:
        # Listing IDs are filenames without extension
        ids = {f.replace(".json", "") for f in os.listdir(config.JSON_DIR) if f.endswith(".json")}
        return ids
    except Exception as e:
        logger.error(f"Error reading existing IDs: {e}")
        return set()

def save_listing(listing_data):
    """Save a listing to a JSON file."""
    try:
        listing_id = listing_data.get("listing_id")
        if not listing_id:
            logger.error("Listing data missing ID. Cannot save.")
            return False

        file_path = os.path.join(config.JSON_DIR, f"{listing_id}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(listing_data, f, indent=4, ensure_ascii=False)

        logger.info(f"Saved listing {listing_id} to JSON.")
        return True
    except Exception as e:
        logger.error(f"Error saving listing {listing_data.get('listing_id')}: {e}")
        return False

def get_all_listings():
    """Retrieve all listings from JSON files."""
    listings = []
    if not os.path.exists(config.JSON_DIR):
        return listings

    for filename in os.listdir(config.JSON_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(config.JSON_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    listings.append(data)
            except Exception as e:
                logger.error(f"Error reading listing file {filename}: {e}")
    return listings

def download_images(listing_id, image_urls):
    """Download images for a listing."""
    listing_img_dir = os.path.join(config.IMAGES_DIR, str(listing_id))
    if not os.path.exists(listing_img_dir):
        os.makedirs(listing_img_dir)

    saved_count = 0
    # Limit to 10 images
    for i, url in enumerate(image_urls[:10]):
        try:
            if not url:
                continue

            response = requests.get(url, headers=config.HEADERS, timeout=10)
            if response.status_code == 200:
                # determine extension
                ext = url.split('.')[-1].split('?')[0]
                if len(ext) > 4 or not ext:
                    ext = "jpg"

                filename = f"image_{i+1}.{ext}"
                filepath = os.path.join(listing_img_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(response.content)
                saved_count += 1
        except Exception as e:
            logger.error(f"Failed to download image {url}: {e}")

    return listing_img_dir
