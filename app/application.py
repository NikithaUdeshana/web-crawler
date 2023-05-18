from flask import Flask
from flask_restful import Api
from resources.crawler_resource import CrawlerResource


def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(CrawlerResource, "/crawl")
    return app