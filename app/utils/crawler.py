import gevent
import requests
from exception.crawl_exception import CrawlError
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self, max_depth=3, max_pages=1000):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_pages = set()
        self.link_relationships = {}
        self.lock = gevent.lock.BoundedSemaphore()
        
    def crawl(self, url, depth=0):
        if self._should_stop_crawling(url, depth):
            return
        
        self._mark_visited(url)

        base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
        page_links = self._fetch_page_links(url)
        greenlets = []

        try:
            for link in page_links:
                if link and not link.startswith('#'):
                    page_url = urljoin(base_url, link)
                    if page_url.startswith(base_url):
                        self._add_link_relationships(url, page_url)
    #                    self.crawl(page_url, depth + 1)
                        greenlets.append(gevent.spawn(self.crawl, page_url, depth + 1))
            gevent.joinall(greenlets)
            return self.link_relationships
        except Exception as e:
            logger.error(f'Error crawling website: {str(e)}')
            raise CrawlError(f'Error crawling website: {str(e)}')

    def _mark_visited(self, url):
        with self.lock:
            self.visited_pages.add(url)

    def _should_stop_crawling(self, url, depth):
        return depth > self.max_depth or len(self.visited_pages) >= self.max_pages or url in self.visited_pages
    
    def _add_link_relationships(self, origin, destination):
        with self.lock:
            if origin in self.link_relationships:
                self.link_relationships[origin].append(destination)
            else:
                self.link_relationships[origin] = [destination]
    
    def _fetch_page_links(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()    # Raise an exception for non-200 status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            return [link.get('href') for link in links]
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching URL: {str(e)}')
            raise CrawlError(f'Error fetching URL: {str(e)}')
        except Exception as e:
            logger.error(f'Error parsing HTML: {str(e)}')
            raise CrawlError(f'Error parsing HTML: {str(e)}')
                    
    def print_link_relationships(self):
        for origin, destinations in self.link_relationships.items():
            for destination in destinations:
                print(f"{origin} -> {destination}")
