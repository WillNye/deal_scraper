import asyncio
import concurrent.futures
import hashlib
from datetime import datetime as dt

import click
import requests
from bs4 import BeautifulSoup

from config import Config, ES, EP

INDEX = 'product'


def delete_document(doc_id, item_name, address):
    if ES.exists(index=Config.ES_INDEX, doc_type='default', id=doc_id):
        click.echo("Discount for {} at {} is on longer available.".format(item_name, address))
        ES.delete(index=Config.ES_INDEX, doc_type='default', id=doc_id)


def parse_item_data(item):
    """Parses the inventory and pricing data for a given item
    :param
        item:Subsection of the primary page's HTML containing product information
    :return:
    """
    minimum_percent_off = 20
    minimum_percent_off = (100-minimum_percent_off)/100

    links = item.find_all('a')
    item_summary = links[0]
    item_name = item_summary['title']
    if 'walmart' in links[2]['href']:
        sku = links[2]['href'].split('/')[-1]
        store_name = 'Walmart'
    elif 'target' in links[2]['href']:
        sku = links[2]['href'].split('=')[-1][:-1]
        store_name = 'Target'
    else:
        # ToDO Support more stores. Bestbuy would be top pick.
        return

    data = {
        'method': 'sku',
        'sku': sku,
        'upc': None,
        'zip': Config.ZIP_CODE,
        'sort': 'recommended'
    }

    # Load the product page's HTML in as text for parsing
    base_item_url = '{}-inventory-checker?sku={}'.format(store_name.lower(), sku)
    url = EP.format(base_item_url)
    response = requests.post(url, data=data, proxies=Config.PROXY)
    soup_data = response.text

    if 'No results found in the searched area.' in soup_data:
        return

    inventory_soup = BeautifulSoup(soup_data, 'html.parser')

    try:
        stores = inventory_soup.main.find("div", {"class": "table"})
        stores = stores.find_all("div", {"class": "table__row"})[1:]

        original_price = inventory_soup.main.find_all("div", {"class": "item-overview__meta-item"})[0]
        original_price = original_price.text.split(' ')[-2]

        if 'N/A' in original_price:
            return

        original_price = float(original_price[1:].replace(',', ''))

    except AttributeError:
        click.echo('Unable to parse {}'.format(url))
        return

    for store in stores:
        if store_name == 'Walmart':
            address = store.address.find_all("a", {"class": "address__link"})[0]['href'].split("?q=")[-1]
            address = address.replace("+", " ")
        elif store_name == 'Target':
            address = store.address.text.split('\n')[1][:-1]
        else:
            return

        doc_id = hashlib.sha256(str.encode('{} {} {}'.format(store_name, address.replace(" ", ""), sku))).hexdigest()
        quantity = store.find("div", {"class": "inventory-checker-table__availability"}).text
        quantity = quantity.replace("\n", "")

        if 'Out of Stock' in quantity or 'Limited Stock' in quantity:
            delete_document(doc_id, item_name, address)
            continue

        try:
            price = store.find("span", {"class": "price-formatted"}).text
            price = float(price[1:].replace(',', ''))
            if price > (original_price * minimum_percent_off):
                delete_document(doc_id, item_name, address)
                continue
        except AttributeError:
            delete_document(doc_id, item_name, address)
            continue

        if ES.exists(index=Config.ES_INDEX, doc_type='default', id=doc_id):
            product_doc = ES.get(index=Config.ES_INDEX, doc_type='default', id=doc_id)['_source']

            if product_doc['quantity'] != quantity or product_doc['sales_price'] != price:
                product_doc['last_updated'] = dt.utcnow()

            product_doc['quantity'] = quantity
            product_doc['last_seen'] = dt.utcnow()
            product_doc['sales_price'] = price
        else:
            click.echo("NEW! {} found at {} for ${}".format(item_name, address, str(price)))
            product_doc = {
                "created_at": dt.utcnow(),
                "last_seen": dt.utcnow(),
                "store": store_name,
                "address": address,
                "name": item_name,
                "sku": sku,
                "sales_price": price,
                "original_price": original_price,
                "quantity": quantity
            }

        try:
            ES.update(index=Config.ES_INDEX, doc_type='default', id=doc_id,
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


def get_deals(filter_mapping, page=1):
    category = ''
    Config.setup(filter_mapping['index_name'])
    base_url = 'deals/?sort=trending{}{}&pg={}'.format(filter_mapping['url'], category, page)
    url = EP.format(base_url)
    click.echo('Parsing page {}'.format(page))

    soup_data = requests.get(url, proxies=Config.PROXY).text

    try:
        soup = BeautifulSoup(soup_data, 'html.parser')
        items = soup.main.find_all("div", {"class": "item-list__item--deal"})
    except AttributeError:
        click.echo("Refresh your public IP")
        click.echo("Died while parsing page {}".format(page))
        return

    items = [item for item in items if item != '\n']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(iter_items(items))
