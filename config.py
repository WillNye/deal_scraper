import json
import os

from elasticsearch import Elasticsearch

ES = Elasticsearch()
EP = 'https://brickseek.com/{}'


class Config:
    ES_INDEX = None
    PROXY = None
    ZIP_CODE = None

    @staticmethod
    def setup(brand=None, category=None):
        es_index = 'product'
        if category:
            es_index = es_index + '_{}'.format(category)
        if brand:
            es_index = es_index + '_{}'.format(brand)

        Config.ES_INDEX = es_index
        ES.indices.create(Config.ES_INDEX, ignore=400)

        config_path = os.path.expanduser('~/.deal_scraper/config.json')

        with open(config_path) as config:
            keys = json.loads(config.read())

        proxy = keys.get('proxy')
        Config.PROXY = {"http": proxy, "https": proxy}
        Config.ZIP_CODE = keys.get('zip_code')
