import unittest
from unittest.mock import patch
from utils.crawler import Crawler
from exception.crawl_exception import CrawlError


class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler(max_depth=2, max_pages=2)

    @patch('utils.crawler.requests.get')
    def test_crawl(self, mock_get):
        # Mock response from requests.get()
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = """
                                <html>
                                    <body>
                                        <a href="/page1.html">Page 1</a>
                                        <a href="/page2.html">Page 2</a>
                                    </body>
                                </html>
                             """

        url = "http://example.com"
        result = self.crawler.crawl(url)

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    # Need to add more test cases here

    def test_mark_visited(self):
        url = 'https://example.com/'
        self.crawler._mark_visited(url)
        self.assertIn(url, self.crawler.visited_pages)

    def test_should_stop_crawling(self):
        # Test when depth exceeds max_depth
        result = self.crawler._should_stop_crawling("http://example.com", 3)
        self.assertTrue(result)

        # Test when visited pages exceed max_pages
        self.crawler.visited_pages = {"http://example.com", "http://example.com/page1"}
        result = self.crawler._should_stop_crawling("http://example.com/page2", 1)
        self.assertTrue(result)

        # Test when URL is already visited
        self.crawler.visited_pages = {"http://example.com"}
        result = self.crawler._should_stop_crawling("http://example.com", 1)
        self.assertTrue(result)

        # Test when conditions are not met
        self.crawler.visited_pages = {"http://example.com"}
        result = self.crawler._should_stop_crawling("http://example.com/page1", 1)
        self.assertFalse(result)

    def test_add_link_relationships(self):
        # Test adding a new origin and destination
        self.crawler._add_link_relationships("http://example.com", "http://example.com/page1")
        self.assertIn("http://example.com", self.crawler.link_relationships)
        self.assertEqual(self.crawler.link_relationships["http://example.com"], ["http://example.com/page1"])

        # Test adding to an existing origin
        self.crawler._add_link_relationships("http://example.com", "http://example.com/page2")
        self.assertIn("http://example.com", self.crawler.link_relationships)
        self.assertEqual(self.crawler.link_relationships["http://example.com"],
                         ["http://example.com/page1", "http://example.com/page2"])

    @patch('utils.crawler.requests.get')
    def test_fetch_page_links(self, mock_get):
        # Mock response from requests.get()
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = """
                                <html>
                                    <body>
                                        <a href="/page1.html">Page 1</a>
                                        <a href="/page2.html">Page 2</a>
                                    </body>
                                </html>
                             """
        # Test fetching links from a valid URL
        url = "http://example.com"
        links = self.crawler._fetch_page_links(url)

        self.assertTrue(isinstance(links, list))
        self.assertEqual(len(links), 2)

    def test_fetch_page_links_with_invalid_URL(self):
        # Test fetching links from a non-existing URL
        url = "bttp://example.com"
        with self.assertRaises(CrawlError):
            self.crawler._fetch_page_links(url)

        # Test fetching links from a URL with invalid HTML
        url = "http://example.com/invalid"
        with self.assertRaises(CrawlError):
            self.crawler._fetch_page_links(url)

    def test_print_link_relationships(self):
        crawler = Crawler(max_depth=2, max_pages=10)
        crawler.crawl('https://example.com/')
        crawler.print_link_relationships()
