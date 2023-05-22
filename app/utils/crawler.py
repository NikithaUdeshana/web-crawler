import gevent
import logging
import requests
from gevent.pool import Pool
from gevent.lock import Semaphore
from exception.crawl_exception import CrawlError
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for error messages
crawl_page_error = 'Error crawling website: {}'
fetch_url_error = 'Error fetching URL: {}'
parse_html_error = 'Error parsing HTML: {}'


class Crawler:
    """Crawler class consists the logic of crawling page links within the given domain of the input URL.

    :param max_depth: This parameter defines the maximum number of levels that can be crawled in the page
     hierarchy of a given website.
    :type max_depth: int
    :param max_pages: This parameter defines the maximum allowed number of pages that can be crawled in
     a given instance of a Crawler method.
    :type max_pages: int
    :param pool_size: This parameter defines the limit of python coroutines(greenlets) pool. These greenlets
     will be utilised to handle the crawling tasks of the Crawler instance concurrently.
    """
    def __init__(self, max_depth=3, max_pages=100, pool_size=100):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_pages = set()
        self.link_relationships = {}
        self.lock = Semaphore()
        self.pool = Pool(size=pool_size)

    def crawl(self, url):
        """Crawl method crawls web links within the given domain of the input URL. This method returns
        a dictionary which consists of page links and their associate page links.

        :param url: Web URL that needs to be crawled
        :type url: str
        :return: A dictionary of page links with their relationships to associate page links
        :rtype: dict
        """
        self._crawl(url)
        return self.link_relationships
        
    def _crawl(self, url, depth=0):
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
    #                    self._crawl(page_url, depth + 1)
    #                    greenlets.append(gevent.spawn(self._crawl, page_url, depth + 1))
                        greenlets.append(self.pool.spawn(self._crawl, page_url, depth + 1))
            gevent.joinall(greenlets)

        except Exception as e:
            logger.error(crawl_page_error.format(str(e)))
            raise CrawlError(crawl_page_error.format(str(e)))

    def _mark_visited(self, url):
        with self.lock:
            self.visited_pages.add(url)

    def _should_stop_crawling(self, url, depth):
        with self.lock:
            return depth >= self.max_depth or len(self.visited_pages) >= self.max_pages or url in self.visited_pages
    
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
            logger.error(fetch_url_error.format(str(e)))
            raise CrawlError(fetch_url_error.format(str(e)))
        except Exception as e:
            logger.error(parse_html_error.format(str(e)))
            raise CrawlError(parse_html_error.format(str(e)))
                    
    def print_link_relationships(self):
        with self.lock:
            for origin, destinations in self.link_relationships.items():
                for destination in destinations:
                    print(f"{origin} -> {destination}")
