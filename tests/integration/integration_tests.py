import gevent.monkey
gevent.monkey.patch_all()

import unittest
from unittest.mock import patch
from application import create_app
from utils.crawler import Crawler
from tests.integration.fixtures import html_pages


class CrawlerIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.test_client = self.app.test_client()

    @patch('utils.crawler.requests.get')
    def test_crawl_integration(self, mock_get):
        # Mock response from requests.get()
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = html_pages.home_page

        url = "http://example.com"
        expected_link_relationships = {
            "http://example.com": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ],
            "http://example.com/page1.html": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ],
            "http://example.com/page2.html": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ]
        }

        crawler = Crawler(max_depth=2, max_pages=10, pool_size=10)
        link_relationships = crawler.crawl(url)

        # Assert the expected link relationships
        self.assertEqual(link_relationships, expected_link_relationships)

    @patch('utils.crawler.requests.get')
    def test_crawler_resource_integration(self, mock_get):
        # Mock response from requests.get()
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = html_pages.home_page

        url = "/crawl?url=http://example.com&depth=2"
        expected_link_relationships = {
            "http://example.com": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ],
            "http://example.com/page1.html": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ],
            "http://example.com/page2.html": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ]
        }

        response = self.test_client.get(url)

        # Assert the response status code
        self.assertEqual(response.status_code, 200)
        # Assert the expected link relationships
        self.assertEqual(response.get_json(), expected_link_relationships)

    @patch('utils.crawler.requests.get')
    def test_crawler_resource_with_depth_integration(self, mock_get):
        # Mock response from requests.get()
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = html_pages.home_page

        url = "/crawl?url=http://example.com&depth=1"
        expected_link_relationships = {
            "http://example.com": [
                "http://example.com/page1.html",
                "http://example.com/page2.html"
            ]
        }

        # Perform a GET request to the CrawlerResource endpoint with depth=1
        response = self.test_client.get(url)
        # Assert the response status code
        self.assertEqual(response.status_code, 200)
        # Assert the expected link relationships
        self.assertEqual(response.get_json(), expected_link_relationships)


if __name__ == '__main__':
    unittest.main()
