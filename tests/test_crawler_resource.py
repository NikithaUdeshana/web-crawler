import unittest
from unittest import TestCase
from unittest.mock import patch
from application import create_app
from werkzeug.exceptions import HTTPException, InternalServerError


class TestCrawlerResource(TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_get_with_valid_url_and_depth(self):
        url = '/crawl?url=https://example.com&depth=2'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_with_missing_url_parameter(self):
        url = '/crawl?depth=2'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. URL field is required.'})

    def test_get_with_invalid_url_parameter(self):
        url = '/crawl?url=https://example.coms'
        response = self.client.get(url)
        print(response)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. URL parameter may not be valid.'})

    def test_get_with_negative_depth_parameter(self):
        url = '/crawl?url=https://example.com&depth=-2'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. '
                                                    'Depth must be a positive integer between 1 and 10.'})

    def test_get_with_invalid_depth_parameter(self):
        url = '/crawl?url=https://example.com&depth=abc'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'message': 'Invalid request. Depth parameter may not be valid.'})

    @patch('resources.crawler_resource.Crawler')
    def test_get_with_http_exception(self, mock_crawler):
        mock_crawler_instance = mock_crawler.return_value
        mock_crawler_instance.crawl.side_effect = HTTPException('Bad Request')

        url = '/crawl?url=http://example.com'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {'message': 'Bad Request'})

    @patch('resources.crawler_resource.Crawler')
    def test_get_with_internal_server_error(self, mock_crawler):
        mock_crawler_instance = mock_crawler.return_value
        mock_crawler_instance.crawl.side_effect = Exception('Something went wrong')

        url = '/crawl?url=http://example.com'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {'message': 'Internal Server error: Something went wrong'})

    # Need to add more test cases here


if __name__ == '__main__':
    unittest.main()
