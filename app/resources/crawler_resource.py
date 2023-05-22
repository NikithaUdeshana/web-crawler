from flask import abort, request
from flask_restful import Resource
from utils.crawler import Crawler
from werkzeug.exceptions import HTTPException
from exception.client_exception import ClientError
import requests
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrawlerResource(Resource):
    """CrawlerResource class exposes the crawling functionality via an endpoint
    """

    def get(self):
        """CrawlerResource get method is used to define the `/crawl` endpoint

        :return: JSON dictionary of page links.
        """
        try:
            url = request.args.get('url')
            depth = int(request.args.get('depth', 1))
            no_of_pages = int(request.args.get('no_of_pages', 50))

            if not url:
                raise ClientError('Invalid request. URL field is required.')

            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-200 status codes

#           TO_DO:max_depth parameter needs to be configured
            if depth <= 0:
                raise ClientError('Invalid request. Depth must be a positive number.')

#           TO_DO:max_pages parameter needs to be configured
            if no_of_pages <= 0:
                raise ClientError('Invalid request. No_of_pages must be a positive number.')

            crawler = Crawler(depth, no_of_pages)
            link_relationships = crawler.crawl(url)
            logger.info(f'Number of pages crawled: {len(crawler.visited_pages)}')
            return link_relationships

        except ValueError:
            raise ClientError('Invalid request. Depth or No_of_pages parameter may not be valid.')

        except requests.exceptions.RequestException:
            raise ClientError('Invalid request. URL parameter may not be valid.')

        except ClientError as e:
            return {'message': str(e.description)}, e.code

        except HTTPException as e:
            return {'message': str(e.description)}, 400

        except Exception as e:
            abort(500, f'Internal Server error: {str(e)}')
