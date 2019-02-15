import json
import os

import click

from config import FILTER_MAPPINGS
from deals import get_deals


@click.group()
def cli():
    pass


@cli.command()
@click.option('--proxy', help='IP and Port of the proxy to use')
@click.option('--zip_code', help='Zip code to reference when searching for deals')
def setup(proxy, zip_code):
    base_dir = os.path.expanduser('~/.deal_scraper')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    with open(os.path.join(base_dir, 'config.json'), 'w') as config:
        config.write(json.dumps({
            "proxy": proxy,
            'zipcode': zip_code
        }, indent=4))


@cli.command()
@click.option('--filter', 'filter_mapping', type=click.Choice(sorted(FILTER_MAPPINGS.keys())))
@click.option('--page', default=1, help='Page to start on')
def deals(filter_mapping, page):
    get_deals(FILTER_MAPPINGS[filter_mapping], page)


if __name__ == '__main__':
    cli()
