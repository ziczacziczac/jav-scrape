from flask import Flask, jsonify, request
import requests
from sqlalchemy import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging
import logging.handlers
import pandas as pd
import glob
import urllib.request
from selenium.webdriver.common.action_chains import ActionChains
import sys

# specify the URL of the archive here

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Host': 'www.google.com',
    'Referer': 'https://www.google.com/'
}

chrome_options = Options()
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")  # Hides the browser window

browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            "debug.log", maxBytes=10000 * 1024, backupCount=5, encoding='utf-8')
    ]
)

app = Flask(__name__)


def get_video_link(link):
    logging.info("Get video link from %s" % link)
    retry_count = 0
    browser.get("https://www.google.com.vn/")
    while retry_count < 5:
        try:
            browser.get(link)
            time.sleep(5)
            # logging.info("Load page %s completed" % link)
            try:
                link_add_1 = browser.find_element_by_xpath('//a[@target="_blank"]')
                link_add_1.click()
            except:
                return None
            # logging.info("Ad 1 of link %s clicked" % link)
            try:
                link_add_2 = browser.find_element_by_xpath('//div[@id="loading"]')
                link_add_2.click()
            except:
                return None
            time.sleep(5)
            # logging.info("Ad 2 of link %s clicked" % link)

            video_page = BeautifulSoup(browser.page_source, "html.parser")
            video_element = video_page.find('video')

            result = video_element.attrs['src']
            # logging.info("Get video from %(link)s completed with result %(result)s" %
            #              {
            #                  "link": link,
            #                  "result": result
            #              })
            clean_browser(browser)
            return result
        except Exception as e:
            logging.error("Get indirect link from %(link) and retry count is %(retry)s",
                          {"link": link, "retry": str(retry_count)})
            clean_browser(browser)
        retry_count = retry_count + 1
    clean_browser(browser)
    return None


def clean_browser(current_browser):
    current_browser_id = current_browser.current_window_handle
    handles = current_browser.window_handles
    size = len(handles)

    for x in range(size):
        if handles[x] != current_browser_id:
            current_browser.switch_to.window(handles[x])
            current_browser.close()
    current_browser.switch_to.window(current_browser_id)


def get_indirect_link(link):
    logging.info("Get indirect link from %s" % link)
    retry_count = 0
    while retry_count < 5:
        retry_count = retry_count + 1
        try:
            res = urllib.request.urlopen(link, timeout=5)
            final_url = res.geturl()
            logging.info("Got mp4 link %s" % final_url)
            return final_url
        except Exception as e:
            logging.info("Get indirect link from %(link)s has error %(error)s, retry to get anothher link",
                         {"link": link, "error": str(e)})


@app.route("/mp4")
def get_mp4_link():
    link = request.args.get('link')
    if link is not None and link != '':
        if 'mm9842' in link:
            indirect_link = get_video_link(link)
            if indirect_link is not None:
                mp4_link = get_indirect_link(indirect_link)
                return jsonify({
                    "code": 1,
                    "data": {
                        "link": link,
                        "mp4": mp4_link
                    }
                })
            else:
                return jsonify({
                    "code": 0,
                    "error": "Unable to get redirect link from {}".format(indirect_link)
                })
        else:
            return jsonify({
                "code": 0,
                "error": "Unsupported link {}".format(link)
            })
    return jsonify(400, {
        "code": 0,
        "error": "Bad request"
    })

if __name__ == "__main__":
    app.run()