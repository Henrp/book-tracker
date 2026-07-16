import time
import random
from curl_cffi import requests

BOOK_URL = "https://www.webnovel.com/book/x_{book_id}"
IMPERSONATE = "chrome124"   # pin explicitly; don't use bare "chrome"

class FetchError(Exception):
    pass

class Fetcher:
    def __init__(self, delay=2.0, max_retries=3):
        self.session = requests.Session(impersonate=IMPERSONATE)
        self.delay = delay
        self.max_retries = max_retries
        self._last_request = 0.0

    def _throttle(self):
        elapsed = time.time() - self._last_request
        wait = self.delay - elapsed
        if wait > 0:
            time.sleep(wait + random.uniform(0, 0.5))
        self._last_request = time.time()

    def fetch_book_page(self, book_id: str) -> str:
        url = BOOK_URL.format(book_id=book_id)

        for attempt in range(self.max_retries):
            self._throttle()
            try:
                r = self.session.get(url, timeout=20)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise FetchError(f"{book_id}: {e}") from e
                time.sleep(2 ** attempt)
                continue

            if r.status_code == 200:
                return r.text
            if r.status_code == 404:
                raise FetchError(f"{book_id}: not found")   # permanent, don't retry
            if r.status_code in (403, 429, 500, 502, 503):
                time.sleep(2 ** attempt * 5)                # transient, back off
                continue
            raise FetchError(f"{book_id}: HTTP {r.status_code}")

        raise FetchError(f"{book_id}: exhausted retries")