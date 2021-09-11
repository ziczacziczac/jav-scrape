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
import wget
from pathlib import Path

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

# browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
browser = webdriver.Chrome("chromedriver", options=chrome_options)

mysql_conn = create_engine(
    "mysql://root:Realkage55!@103.155.93.154:33306/jav_scrape?charset=utf8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            "debug.log", maxBytes=10000 * 1024, backupCount=5, encoding='utf-8')
    ]
)

def clean_browser(current_browser):
    current_browser_id = current_browser.current_window_handle
    handles = current_browser.window_handles
    size = len(handles)

    for x in range(size):
        if handles[x] != current_browser_id:
            current_browser.switch_to.window(handles[x])
            current_browser.close()
    current_browser.switch_to.window(current_browser_id)

def get_video_link(link):
    logging.info("Get video link from %s" % link)
    retry_count = 0
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


def download_video(link):
    logging.info("Download video from %(link)s",
                 {"link": link})
    # filename = wget.download(link, out="data/download")
    filename = 'smt'
    logging.info("Download video from %(link)s with name %(name)s completed",
                 {"link": link, "name": filename})
    return filename


def get_video_info(page_source):
    logging.info("Get video infor from page source")
    video_info_details = {
        'title': '',
        'meta': [],
        'cast': [],
        'maker': [],
        'genre': [],
        'img': [],
    }
    page_soup = BeautifulSoup(page_source, "html.parser")

    video_info = page_soup.find('div', {'class': 'video-info'})
    video_detail = page_soup.find('div', {'class': 'video-details'})
    video_image = page_soup.find('div', {'class': 'content-image'})

    video_info_details['title'] = video_info.find('h1').text

    metas = video_detail.find_all('span', {'class': 'meta'})
    for meta in metas:
        classes = meta.attrs['class']
        if len(classes) == 1:
            video_info_details['meta'] = [a.text for a in meta.find_all('a')]
        elif classes[1] == 'cast-info':
            video_info_details['cast'] = [cast.text for cast in meta.find_all('a')]
        elif classes[1] == 'maker-info':
            video_info_details['maker'] = [maker.text for maker in meta.find_all('a')]
        elif classes[1] == 'genre-info':
            video_info_details['genre'] = [genre.text for genre in meta.find_all('a')]
    if video_image is not None:
        imgs = video_image.find_all('img')
        if imgs is not None:
            video_info_details['img'] = [img.attrs['src'] for img in imgs]
    logging.info("Get video infor from page source completed")
    return video_info_details


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


def get_indirect_by_selenium(link):
    while True:
        logging.info("Get indirect link from %s" % link)
        try:
            browser.get(link)
            browser.set_page_load_timeout(5)
            time.sleep(5)
            final_url = browser.current_url
            if not is_forbiden(final_url):
                logging.info("Get indirect link from %(indirect_link)s completed with result %(mp4_link)s",
                             {'indirect_link': link, 'mp4_link': final_url})
                return final_url
            logging.info("Url %s is forbiden, retry to get another link" % final_url)
            time.sleep(5)
        except:
            pass


def is_forbiden(link):
    logging.info("Check link %s" % link)
    try:
        browser.get(link)
        return '403' in browser.page_source
    except:
        logging.warning("Link %s need to check more" % link)
        return False

def get_original_video_link(page_source, ):
    parser = BeautifulSoup(page_source, 'html.parser')

    video_element = parser.find('iframe', {'id': 'video'})
    if video_element is not None:
        return video_element.get('src')
        # indirect_link = get_video_link(video_element.get('src'))
        # if indirect_link is not None:
        #     return get_indirect_by_selenium(indirect_link)


def get_video_info_detail(link):
    logging.info("Get video detail from %s" % link)
    while True:
        try:
            response = requests.get(link, headers=headers)
            #print(response.content)
            #browser.get(link)
            video_info = get_video_info(response.content)
            logging.info("Get video basic info from %s completed" % link)

            video_link = get_original_video_link(response.content)
            logging.info("Get video link from %s completed" % link)

            video_info['link'] = video_link
            video_info['source'] = link
            logging.info("Get video detail from %s completed" % link)

            return video_info
        except Exception as e:
            print(str(e))
    return {}


def is_match(data, title):
    for idx, row in data.iterrows():
        data_title = row.title
        if data_title in title:
            return True

    return False


def get_matched_video_from_sql():
    video_link_query = text('''
            SELECT distinct(link) FROM jav_scrape.free_jav_matched_title;
        ''')

    video_links = mysql_conn.execute(video_link_query).fetchall()
    video_links = [video_link[0] for video_link in video_links]
    return video_links


def get_matched_video_from_csv():
    matched_video = pd.read_csv('data/matched.csv', encoding='utf-8')

    return matched_video['link'].unique().tolist()


def crawl_video_data(from_idx, to_idx):

    video_links = get_matched_video_from_csv()
    if to_idx >= len(video_links): to_idx = len(video_links) - 1
    video_links = video_links[from_idx:(to_idx + 1)]
    print(video_links)

    detail_data = pd.DataFrame(columns=['title', 'meta', 'cast', 'maker', 'genre', 'img', 'source', 'link'])
    for link in video_links:
        video_data = get_video_info_detail(link)

        detail_data = detail_data.append(video_data, ignore_index=True)

    return detail_data


def crawl_video_link(from_idx, to_idx):

    video_links = load_data("data/crawl/*.csv")['link'].values.tolist()
    if to_idx >= len(video_links): to_idx = len(video_links) - 1
    video_links = video_links[from_idx:(to_idx + 1)]

    detail_data = pd.DataFrame(columns=['link', 'mp4', 'video'])
    detail_file_name = 'data/video/crawled_mp4_' + str(from_idx) + '_' + str(to_idx) + '.csv'
    if Path(detail_file_name).is_file():
        detail_data = pd.read_csv(detail_file_name)
    existed_videos = detail_data['link'].values.tolist()
    for link in video_links:
        if link not in existed_videos:
            if 'mm9842' in link:
                browser.get("https://www.google.com.vn/")
                indirect_link = get_video_link(link)
                if indirect_link is not None:
                    mp4_link = get_indirect_link(indirect_link)
                    mp4_video = download_video(mp4_link)
                    video_mp4 = {
                        'link': link,
                        'mp4': mp4_link,
                        'video': mp4_video
                    }
                    detail_data = detail_data.append(video_mp4, ignore_index=True)

                else:
                    video_mp4 = {
                        'link': link,
                        'mp4': link,
                        'video': link
                    }
                    detail_data = detail_data.append(video_mp4, ignore_index=True)
            else:
                video_mp4 = {
                    'link': link,
                    'mp4': link,
                    'video': link
                }
                detail_data = detail_data.append(video_mp4, ignore_index=True)
        detail_data.to_csv(detail_file_name)


def load_data(pattern):
    target_files = glob.glob(pattern)
    target_df_list = []
    for file in target_files:
        df = pd.read_csv(file, encoding="utf-8")
        target_df_list.append(df)
    return pd.concat(target_df_list, ignore_index=True)


# x = get_video_link("https://mm9842.com/v/13n0najr--m12xe")
# print(x)
# browser.quit()
if __name__ == '__main__':
    from_idx = sys.argv[1]
    to_idx = sys.argv[2]
    crawl_video_link(int(from_idx), int(to_idx))
    browser.quit()