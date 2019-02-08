import sys

from lxml.html import fromstring
from selenium import webdriver


def get_proxies():
    url = 'https://www.us-proxy.org'
    driver = webdriver.Chrome()
    driver.get(url)
    driver.set_window_size(1920, 1080)  # Must be re-sized to display form

    filter_field = driver.find_element_by_xpath("//input[@type='search']")
    filter_field.send_keys('yes')

    proxies = []

    for page in range(5):
        parser = fromstring(driver.page_source)
        for i in parser.xpath('//tbody/tr')[:20]:
            try:
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.append(proxy)
            except IndexError:
                return list(set(proxies))

        driver.find_element_by_id('proxylisttable_paginate').click()

    return list(set(proxies))


PROXIES = get_proxies()


def get_next_proxy():
    if len(PROXIES) == 0:
        print('No proxies remaining')
        sys.exit(1)
    else:
        next_proxy = PROXIES[0]
        print('The following proxy was requested: {}'.format(next_proxy))
        del(PROXIES[0])
        return next_proxy

