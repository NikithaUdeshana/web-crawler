import unittest

from unittest.mock import patch
from application import create_app
from werkzeug.exceptions import HTTPException


class TestCrawlerResource(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.test_client = self.app.test_client()

    def test_get_with_valid_url_and_depth(self):
        url = '/crawl?url=https://example.com&depth=2'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_with_missing_url_parameter(self):
        url = '/crawl?depth=2'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. URL field is required.'})

    def test_get_with_invalid_url_parameter(self):
        url = '/crawl?url=https://example.coms'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. URL parameter may not be valid.'})

    def test_get_with_negative_depth_parameter(self):
        url = '/crawl?url=https://example.com&depth=-2'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. '
                                                    'Depth must be a positive number.'})

    def test_get_with_invalid_depth_parameter(self):
        url = '/crawl?url=https://example.com&depth=abc'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. Depth or No_of_pages '
                                                    'parameter may not be valid.'})

    def test_get_with_negative_no_of_pages_parameter(self):
        url = '/crawl?url=https://example.com&no_of_pages=-2'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. '
                                                    'No_of_pages must be a positive number.'})

    def test_get_with_invalid_no_of_pages_parameter(self):
        url = '/crawl?url=https://example.com&no_of_pages=abc'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. Depth or '
                                                    'No_of_pages parameter may not be valid.'})

    @patch('resources.crawler_resource.Crawler')
    def test_get_with_http_exception(self, mock_crawler):
        mock_crawler_instance = mock_crawler.return_value
        mock_crawler_instance.crawl.side_effect = HTTPException('Bad Request')

        url = '/crawl?url=http://example.com'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {'message': 'Bad Request'})

    @patch('resources.crawler_resource.Crawler')
    def test_get_with_internal_server_error(self, mock_crawler):
        mock_crawler_instance = mock_crawler.return_value
        mock_crawler_instance.crawl.side_effect = Exception('Something went wrong')

        url = '/crawl?url=http://example.com'
        response = self.test_client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {'message': 'Internal Server error: Something went wrong'})

    # Need to add more test cases here


if __name__ == '__main__':
    unittest.main()
