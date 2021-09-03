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

def get_all_from_atashi():
    logging.info('Get all video title from https://zinguide.com/')
    data = requests.get("https://zinguide.com/")
    parser = BeautifulSoup(data.text, 'html.parser')

    # page_a_tags = parser.find('ul', {'class': 'pagination'}).find_all('li')
    # last_page = int(page_a_tags[-1].find('').text.replace(',', ''))
    last_page = 2
    logging.info('Total page from https://zinguide.com/ is %s' % str(last_page))
    page_ids = [i + 1 for i in range(last_page)]
    dfs = []
    for page_id in page_ids:
        logging.info('Get page %(page_id)s from https://zinguide.com/ ' % {"page_id": page_id})
        page_data = get_zinguide_page(page_id)
        dfs.append(page_data)
        logging.info('Get page %(page_id)s from https://zinguide.com/ completed' % {"page_id": page_id})
        # if page_data is not None:
    return pd.concat(dfs, ignore_index=True)

def get_zinguide_page(page_id):
    logging.info("Get data from https://zinguide.com/ at page " + str(page_id))
    url = "https://zinguide.com/page/" + str(page_id)
    data = None
    response = None
    while response is None:
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except Exception as e:
            print(str(e))
    parser = BeautifulSoup(response.text, 'html.parser')
    page_df = pd.DataFrame(columns=['source', 'title', 'date'])

    h2s = parser.find('div', {'id': 'list'}).find_all('h2')
    for h2 in h2s:

        title_link = h2.find('a').get('href')
        title = get_title_from_link(title_link)
        page_df = page_df.append({
            'source': title_link,
            'title': title,
            'date': None
        }, ignore_index=True)
    logging.info("Get data from https://zinguide.com/ at page " + str(page_id) + " completed")
    return page_df

def get_title_from_link(link):
    logging.info("Get title from link %s" % link)
    browser.get(link)
    time.sleep(2)
    parser = BeautifulSoup(browser.page_source, 'html.parser')
    div_item = parser.find('div', {'class': 'erKokItem'})

    if div_item is not None:
        logging.info("Get title from link %s completed" % link)
        return div_item.find('div', {'class': 'itemTitle'}).text
    return ''

atashi_data = get_all_from_atashi()
atashi_data.to_csv('data/target/zinguide.csv')