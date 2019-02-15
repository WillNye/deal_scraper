import json
import os

from elasticsearch import Elasticsearch

ES = Elasticsearch()
EP = 'https://brickseek.com/{}'

FILTER_MAPPINGS = {
    'All': {'url': '', 'index_name': 'all'},
    'Apparel': {'url': '&categories[1]=1', 'index_name': 'apparel'},
    'Appliances': {'url': '&categories[2]=2', 'index_name': 'appliances'},
    'Automotive': {'url': '&categories[3]=3', 'index_name': 'automotive'},
    'Baby': {'url': '&categories[4]=4', 'index_name': 'baby'},
    'Electronics': {'url': '&categories[7]=7', 'index_name': 'electronics'},
    'Outdoors': {'url': '&categories[15]=15', 'index_name': 'outdoors'},
    'Grocery': {'url': '&categories[12]=12', 'index_name': 'grocery'},
    'Health': {'url': '&categories[5]=5', 'index_name': 'health'},
    'Home': {'url': '&categories[9]=9', 'index_name': 'home'},
    'Renovation': {'url': '&categories[10]=10', 'index_name': 'renovation'},
    'Household': {'url': '&categories[8]=8', 'index_name': 'household'},
    'Pet': {'url': '&categories[16]=16', 'index_name': 'pet'},
    'Sporting': {'url': '&categories[17]=17', 'index_name': 'sporting'},
    'Tools': {'url': '&categories[18]=18', 'index_name': 'tools'},
    'Toys': {'url': '&categories[19]=19', 'index_name': 'toys'},
    'Apple': {'url': '&brands[7]=7', 'index_name': 'apple'},
    'Barbie': {'url': '&brands[265]=265', 'index_name': 'barbie'},
    'Disney': {'url': '&brands[13]=13', 'index_name': 'disney'},
    'GE': {'url': '&brands[54]=54', 'index_name': 'ge'},
    'Kobalt': {'url': '&brands[6572]=6572', 'index_name': 'kobalt'},
    'Lego': {'url': '&brands[56]=56', 'index_name': 'lego'},
    'Nintendo': {'url': '&brands[11]=11', 'index_name': 'nintendo'},
    'Pillowfort': {'url': '&brands[3831]=3831', 'index_name': 'pillowfort'},
    'OzarkTrail': {'url': '&brands[50]=50', 'index_name': 'ozark_trail'},
    'Samsung': {'url': '&brands[42]=42', 'index_name': 'samsung'},
    'PioneerWoman': {'url': '&brands[137]=137', 'index_name': 'pioneer_woman'}
}


class Config:
    ES_INDEX = None
    PROXY = None
    ZIP_CODE = None

    @staticmethod
    def setup(filter_index=None):
        es_index = 'product_{}'.format(filter_index)

        Config.ES_INDEX = es_index
        ES.indices.create(Config.ES_INDEX, ignore=400)

        config_path = os.path.expanduser('~/.deal_scraper/config.json')

        with open(config_path) as config:
            keys = json.loads(config.read())

        proxy = keys.get('proxy')
        Config.PROXY = {"http": proxy, "https": proxy}
        Config.ZIP_CODE = keys.get('zip_code')
