from flask import abort, request
from flask_restful import Resource
from utils.crawler import Crawler
from werkzeug.exceptions import HTTPException
from exception.client_exception import ClientError
import requests


class CrawlerResource(Resource):
    def get(self):
        try:
            url = request.args.get('url')
            depth = int(request.args.get('depth', 1))

            if not url:
                raise ClientError('Invalid request. URL field is required.')

            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-200 status codes

#           TO_DO:max_depth parameter needs to be configured
            if depth <= 0 or depth > 10:
                raise ClientError('Invalid request. Depth must be a positive integer between 1 and 10.')

            crawler = Crawler(depth, 100)
            return crawler.crawl(url)

        except ValueError:
            raise ClientError('Invalid request. Depth parameter may not be valid.')

        except requests.exceptions.RequestException:
            raise ClientError('Invalid request. URL parameter may not be valid.')

        except ClientError as e:
            return {'message': str(e.description)}, e.code

        except HTTPException as e:
            return {'message': str(e.description)}, 400

        except Exception as e:
            abort(500, f'Internal Server error: {str(e)}')
