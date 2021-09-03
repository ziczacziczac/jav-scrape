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

def get_all_from_clublucifer():
    logging.info('Get all video title from http://1st.clublucifer.net/')
    data = requests.get("http://1st.clublucifer.net/")
    parser = BeautifulSoup(data.text, 'html.parser')

    page_a_tags = parser.find('div', {'class': 'pagenavi'}).find_all('a')
    # last_page = int(page_a_tags[-2].text.replace(',', ''))
    last_page = 3
    logging.info('Total page from http://1st.clublucifer.net/ is %s' % str(last_page))
    page_ids = [i + 1 for i in range(last_page)]
    dfs = []
    for page_id in page_ids:
        logging.info('Get page %(page_id)s from http://1st.clublucifer.net/ ' % {"page_id": page_id})
        page_data = get_clublucifer_page(page_id)
        dfs.append(page_data)
        logging.info('Get page %(page_id)s from http://1st.clublucifer.net/ completed' % {"page_id": page_id})
        # if page_data is not None:
    return pd.concat(dfs, ignore_index=True)

def get_clublucifer_page(page_id):
    logging.info("Get data from http://1st.clublucifer.net/ at page " + str(page_id))
    url = "http://1st.clublucifer.net/?word=&page=" + str(page_id)
    data = None
    response = None
    while response is None:
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except Exception as e:
            print(str(e))
    parser = BeautifulSoup(response.text, 'html.parser')
    page_df = pd.DataFrame(columns=['source', 'title', 'date'])

    h3s = parser.find('div', {'class': 'mainContent'}).find_all('h3')
    for h3 in h3s:

        title_link = h3.find('a').get('href')
        title = get_title_from_link(title_link)
        page_df = page_df.append({
            'source': 'http://1st.clublucifer.net/',
            'title': title,
            'date': None
        }, ignore_index=True)
    logging.info("Get data from http://1st.clublucifer.net/ at page " + str(page_id) + " completed")
    return page_df

def get_title_from_link(link):
    logging.info("Get title from link %s" % link)
    response = requests.get(link, headers=headers)
    parser = BeautifulSoup(response.content, 'html.parser')
    div_item = parser.find('div', {'class': 'entryText'})
    if div_item is not None:
        logging.info("Get title from link %s completed" % link)
        return div_item.text
    return ''

atashi_data = get_all_from_clublucifer()
atashi_data.to_csv('data/target/clublucifer.csv')