import logging
import logging.handlers

import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            "debug.log", maxBytes=10000 * 1024, backupCount=5),
        logging.StreamHandler()
    ]
)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def get_page_titles(page_url):
    logging.info("Get titles from page %s" % page_url)
    page_df = pd.DataFrame(columns=['title', 'date', 'view', 'link'])
    response = None
    while response is None:
        try:
            response = requests.get(page_url, headers=headers)
        except Exception as e:
            logging.error("Get titles from page %(page_url)s failed because of %(error)s"
                          % {'page_url': page_url, 'error': str(e)})

    parser = BeautifulSoup(response.text, 'html.parser')
    items = parser.find_all('div', {'class': 'item'})
    for item in items:
        title = item.find('h3').text
        date = item.find('span', {'class': 'date'}).text
        link = item.find('a').get('href')
        view = item.find('span', {'class': 'views'})
        if view is not None:
            view = view.text
        else:
            view = 0
        item_details = {
            'title': title,
            'date': date,
            'view': view,
            'link': link
        }
        page_df = page_df.append(item_details, ignore_index=True)
    logging.info("Get titles from page %s completed" % page_url)
    return page_df


def get_category_titles(category_url):
    logging.info("Get title from category %s" % category_url)
    response = None
    while response is None:
        try:
            response = requests.get(category_url, headers=headers)
        except Exception as e:
            logging.error("Get data from category url %(url)s failed "
                          "because of %(error)s" % {'url': category_url, 'error': str(e)})

    parser = BeautifulSoup(response.text, 'html.parser')
    page_elems = parser.find('ul', {'class': 'pagination'}).find_all('li')
    total_page = int(page_elems[-2].text.replace(',', ''))
    # total_page = 3
    logging.info("Category %(url)s has %(page)s pages",
                 {'url': category_url, 'page': str(total_page)})

    total_df = []
    for i in range(total_page):
        page_idx = i + 1
        if 'popular' in category_url:
            page_url = category_url + "?page=" + str(page_idx)
        else:
            page_url = category_url + "page/" + str(page_idx)
        page_titles = get_page_titles(page_url)
        total_df.append(page_titles)

    return pd.concat(total_df, ignore_index=True)

freejav_popular = get_category_titles('http://freejav.video/categories/popular/')
freejav_popular.to_csv('freejav_popular.csv')

freejav_censored = get_category_titles('http://freejav.video/categories/censored/')
freejav_censored.to_csv('freejav_censored.csv')

freejav_uncensored= get_category_titles('http://freejav.video/categories/uncensored/')
freejav_uncensored.to_csv('freejav_uncensored.csv')

freejav_amateur = get_category_titles('http://freejav.video/categories/amateur/')
freejav_amateur.to_csv('freejav_amateur.csv')

freejav_reducing_mosaic = get_category_titles('http://freejav.video/categories/reducing-mosaic/')
freejav_reducing_mosaic.to_csv('freejav_reducing_mosaic.csv')
