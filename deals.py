import asyncio
import concurrent.futures
import hashlib
from datetime import datetime as dt

import click
import requests
from bs4 import BeautifulSoup
from elasticsearch.exceptions import NotFoundError

from config import Config, ES, EP

INDEX = 'product'
proxy = '127.0.0.1:21218'

BRAND_MAPPINGS = {
    'Lego': {'url': '&brands%5B56%5D=56', 'index_name': 'lego'}
}


def parse_item_data(item):
    minimum_percent_off = 25
    minimum_percent_off = (100-minimum_percent_off)/100

    try:
        links = item.find_all('a')
        item_summary = links[0]
        item_name = item_summary['title']
        if 'walmart' in links[2]['href']:
            sku = links[2]['href'].split('/')[-1]
            store_name = 'Walmart'
        else:
            sku = links[2]['href'].split('=')[-1][:-1]
            store_name = 'Target'
    except:
        click.echo('Item Error. Unable to parse item data')
        return

    data = {
        'method': 'sku',
        'sku': sku,
        'upc': None,
        'zip': '78641',
        'sort': 'recommended'
    }

    base_item_url = '{}-inventory-checker?sku={}'.format(store_name.lower(), sku)
    url = EP.format(base_item_url)
    response = requests.post(url, data=data, proxies=Config.PROXY)
    soup_data = response.text

    if 'No results found in the searched area.' in soup_data:
        return

    inventory_soup = BeautifulSoup(soup_data, 'html.parser')

    try:
        stores = inventory_soup.main.find("div", {"class": "table"})
    except AttributeError:
        click.echo('Unable to parse {}'.format(url))
        return

    stores = stores.find_all("div", {"class": "table__row"})[1:]

    original_price = inventory_soup.main.find_all("div", {"class": "item-overview__meta-item"})[0]
    original_price = original_price.text.split(' ')[-2]
    original_price = float(original_price[1:])

    for store in stores:
        if store_name == 'Walmart':
            address = store.address.find_all("a", {"class": "address__link"})[0]['href'].split("?q=")[-1]
            address = address.replace("+", " ")
        elif store_name == 'Target':
            address = store.address.text.split('\n')[1][:-1]
        else:
            click.echo('Currently, only Walmart and Target are supported')
            return

        id = hashlib.sha256(str.encode('{} {} {}'.format(store_name, address.replace(" ", ""), sku))).hexdigest()

        quantity = store.find("div", {"class": "inventory-checker-table__availability"}).text
        quantity = quantity.replace("\n", "")
        if 'Out of Stock' in quantity:
            return

        try:
            price = store.find("span", {"class": "price-formatted"}).text
            price = float(price[1:])
            if price > (original_price * minimum_percent_off):
                continue
        except AttributeError:
            click.echo('Unable to find pricing data for {}'.format(url))
            return

        try:
            product_doc = ES.get(index=Config.ES_INDEX, doc_type='default', id=id)['_source']
            product_doc['last_seen'] = dt.now()

            if product_doc['sales_price'] > price:
                product_doc['sales_price'] = price
                product_doc['last_updated'] = dt.now()
        except NotFoundError:
            click.echo("NEW! {} found at {} for".format(item_name, address, str(price)))
            product_doc = {
                "created_at": dt.now(),
                "store": store_name,
                "address": address,
                "name": item_name,
                "sku": sku,
                "sales_price": price,
                "original_price": original_price,
                "quantity": quantity
            }

        try:
            ES.update(index=Config.ES_INDEX, doc_type='default', id=id,
                      body={
                          "doc": product_doc,
                          "doc_as_upsert": True
                      })
        except Exception as e:
            click.echo(str(e))


async def iter_items(items):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                parse_item_data,
                item
            ) for item in items]

        await asyncio.gather(*futures)


def get_deals(page=1):
    brand = BRAND_MAPPINGS.get('Lego', '')
    category = ''
    Config.setup(brand=brand['index_name'])
    base_url = 'deals/?sort=trending{}{}&pg={}'.format(brand['url'], category, page)
    url = EP.format(base_url)
    click.echo('Parsing page {}'.format(page))

    soup_data = requests.get(url, proxies=Config.PROXY).text

    try:
        soup = BeautifulSoup(soup_data, 'html.parser')
        items = soup.main.find_all("div", {"class": "item-list__item--deal"})
    except AttributeError:
        click.echo("Refresh your public IP")
        click.echo("Died while parsing page {}".format(current_page))
        return

    items = [item for item in items if item != '\n']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(iter_items(items))


if __name__ == '__main__':
    get_deals()
