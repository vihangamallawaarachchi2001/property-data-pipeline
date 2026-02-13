import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from . import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_session():
    """Create a requests session with retries."""
    session = requests.Session()
    retry = Retry(
        total=config.MAX_RETRIES,
        read=config.MAX_RETRIES,
        connect=config.MAX_RETRIES,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(config.HEADERS)
    return session

def fetch_url(session, url):
    """Fetch a URL with delay and error handling."""
    time.sleep(config.REQUEST_DELAY)
    try:
        response = session.get(url, timeout=config.TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

def clean_text(text):
    """Clean extracted text."""
    if not text:
        return ""
    return text.strip()
