
import time
import logging
from urllib.parse import urljoin
from . import config, utils, parsers, storage

logger = logging.getLogger(__name__)

def run_scraper():
    """Main execution loop."""
    logger.info("Starting scraper...")

    # Initialize storage
    storage.init_storage()
    existing_ids = storage.get_existing_ids()
    logger.info(f"Types of existing IDs: {type(existing_ids)}. First few: {list(existing_ids)[:5]}")
    logger.info(f"Found {len(existing_ids)} existing listings.")

    session = utils.get_session()

    page = 1
    total_scraped = 0
    target_count = 2000 # Target from plan

    while total_scraped < target_count:
        logger.info(f"Scraping search page {page}...")

        # Construct URL with pagination
        # ikman.lk pagination: ?page=1
        search_url = f"{config.SEARCH_URL}?page={page}"

        response = utils.fetch_url(session, search_url)
        if not response:
            logger.error("Failed to fetch search page. Stopping.")
            break

        listings = parsers.parse_search_page(response.text)
        if not listings:
            logger.info("No more listings found or parsing failed. Stopping.")
            break

        new_listings_count = 0
        for listing in listings:
            listing_id = listing.get("listing_id")

            if not listing_id:
                logger.warning("Found listing without ID. Skipping.")
                continue

            if listing_id in existing_ids:
                if total_scraped % 10 == 0:
                   logger.info(f"Skipping existing listing {listing_id}")
                continue

            # Fetch detail page
            logger.info(f"Processing new listing {listing_id}...")
            detail_response = utils.fetch_url(session, listing.get("source_url"))

            if detail_response:
                # Parse detail info
                detail_data = parsers.parse_detail_page(detail_response.text, listing.get("source_url"))

                # Merge data (detail data overrides search data if present)
                full_data = {**listing, **detail_data}

                # Download images
                image_urls = full_data.get("image_urls", [])
                # If only one image from search page and none from detail, use search image
                if not image_urls and listing.get("image_url"):
                    image_urls = [listing.get("image_url")]

                if image_urls:
                    image_folder = storage.download_images(listing_id, image_urls)
                    full_data["image_folder"] = image_folder
                else:
                    full_data["image_folder"] = ""

                # Add scraped date
                full_data["scraped_date"] = time.strftime("%Y-%m-%d %H:%M:%S")

                # Save to JSON
                if storage.save_listing(full_data):
                    existing_ids.add(listing_id)
                    total_scraped += 1
                    new_listings_count += 1
                    logger.info(f"Scraped count: {total_scraped}/{target_count}")

            # Rate limiting is handled in fetch_url

        if new_listings_count == 0 and len(listings) > 0:
             # If we went through a whole page of duplicates, we might want to stop?
             # But valid to continue as older ads might be mixed or we want to catch up.
             # Yet, if we have 2000 gathered and we see duplicates, maybe we are done.
             # For now, let's continue.
             pass

        page += 1

    logger.info("Scraping completed.")

if __name__ == "__main__":
    run_scraper()
