import logging
import logging.handlers
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Hides the browser window

browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
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

def get_all_from_blogterest(from_page, to_page):
    logging.info('Get all video title from http://big-boobs.blogterest.net/ from page %(from_page)s to page %(to_page)s',
                 {'from_page': from_page, 'to_page': to_page})
    data = requests.get("http://big-boobs.blogterest.net/")
    parser = BeautifulSoup(data.text, 'html.parser')

    page_a_tags = parser.find('div', {'class': 'pagenavi'}).find_all('a')
    last_page = int(page_a_tags[-2].text.replace(',', ''))
    # last_page = 3
    if to_page > last_page: to_page = last_page
    logging.info('Total page from http://big-boobs.blogterest.net/ is %s' % str(to_page - from_page + 1))
    page_ids = [i for i in range(from_page, to_page)]
    dfs = []
    for page_id in page_ids:
        logging.info('Get page %(page_id)s from http://big-boobs.blogterest.net/ ' % {"page_id": page_id})
        page_data = get_blogterest_page(page_id)
        dfs.append(page_data)
        logging.info('Get page %(page_id)s from http://big-boobs.blogterest.net/ completed' % {"page_id": page_id})
        # if page_data is not None:
    return pd.concat(dfs, ignore_index=True)

def get_blogterest_page(page_id):
    logging.info("Get data from http://big-boobs.blogterest.net/ at page " + str(page_id))
    url = "http://big-boobs.blogterest.net/?word=&page=" + str(page_id)
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
            'source': title_link,
            'title': title,
            'date': None
        }, ignore_index=True)
    logging.info("Get data from http://big-boobs.blogterest.net/ at page " + str(page_id) + " completed")
    return page_df


def get_title_from_link(link):
    logging.info("Get title from link %s" % link)
    browser.get(link)
    time.sleep(2)
    parser = BeautifulSoup(browser.page_source, 'html.parser')
    div_item = parser.find('div', {'class': 'erKokItem'})

    if div_item is not None:
        logging.info("Get title from link %s completed" % link)
        if div_item.find('div', {'class': 'itemTitle'}) is not None:
            return div_item.find('div', {'class': 'itemTitle'}).text
    return ''


atashi_data = get_all_from_blogterest(1, 3)
atashi_data.to_csv('data/target/blogterest_1_3.csv')