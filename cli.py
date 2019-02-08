import json
import os

import click

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
@click.option('--starting_page', default=1, help='Page to start on')
def deals(starting_page):
    get_deals(starting_page)


if __name__ == '__main__':
    cli()
