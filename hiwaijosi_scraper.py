import requests
import time
from bs4 import BeautifulSoup
import logging
import logging.handlers
import re
import pandas as pd
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

def get_all_from_hiwajosi(from_page, to_page):
    logging.info('Get all video title from https://hiwaijosi.net/ from page %(from_page)s to page %(to_page)s',
                 {'from_page': from_page, 'to_page': to_page})
    data = requests.get("https://hiwaijosi.net/", headers=headers)
    parser = BeautifulSoup(data.text, 'html.parser')
    page_numbers = parser.find_all('a', {'class': 'page-numbers'})
    last_page = int(page_numbers[len(page_numbers) - 2].text.replace(',', ''))
    # last_page = 3
    if from_page > last_page: return
    if to_page > last_page: to_page = last_page
    logging.info('Total page from https://hiwaijosi.net/ is %s' % str(to_page - from_page + 1))
    page_ids = [i for i in range(from_page, to_page + 1)]
    dfs = []
    for page_id in page_ids:
        logging.info('Get page %(page_id)s from https://hiwaijosi.net/ ' % {"page_id": page_id})
        page_data = get_hiwajosi_page(page_id)
        dfs.append(page_data)
        logging.info('Get page %(page_id)s from https://hiwaijosi.net/ completed' % {"page_id": page_id})
        # if page_data is not None:
    return pd.concat(dfs, ignore_index=True)


def get_hiwajosi_page(page_id):
    logging.info("Get data from https://hiwaijosi.net/ at page " + str(page_id))
    url = "https://hiwaijosi.net/page/" + str(page_id)
    data = None
    response = None
    while response is None:
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except Exception as e:
            print(str(e))
    parser = BeautifulSoup(response.text, 'html.parser')
    page_df = pd.DataFrame(columns=['source', 'title', 'date'])

    dd = parser.find_all('dd')
    for d in dd:
        title_elem = d.find('p', {'class': 'kanren-t'})

        time_elem = d.find('div').find('p')

        if title_elem is not None and time_elem is not None:
            title_link = title_elem.find('a').get('href')
            title = get_title_from_link(title_link)
            title_time = re.search("[0-9|/]+", time_elem.text).group()
            page_df = page_df.append({
                'source': title_link,
                'title': title,
                'date': title_time
            }, ignore_index=True)
    logging.info("Get data from https://hiwaijosi.net/ at page " + str(page_id) + " completed")
    return page_df


def get_title_from_link(link):
    logging.info("Get title from link %s" % link)
    browser.get(link)
    parser = BeautifulSoup(browser.page_source, 'html.parser')
    div_item = parser.find('div', {'class': 'erKokOrigin'})
    if div_item is not None:
        logging.info("Get title from link %s completed" % link)
        if div_item.find('a') is not None:
            return div_item.find('a').text
    return ''


hiwajosi_data = get_all_from_hiwajosi(1, 2)
hiwajosi_data.to_csv('data/target/hiwaijosi_1_5.csv')
browser.close()