import pandas as pd
import glob
from sqlalchemy import *
import logging
import logging.handlers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            "matching.log", maxBytes=10000 * 1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
mysql_conn = create_engine(
    "mysql://root:Realkage55!@103.155.93.154:33306/jav_scrape?charset=utf8")
def load_data(pattern):
    target_files = glob.glob(pattern)
    target_df_list = []
    for file in target_files:
        df = pd.read_csv(file, encoding="utf-8")
        target_df_list.append(df)
    return pd.concat(target_df_list, ignore_index=True)

def load_to_database():
    target_df = load_data("data/target/*.csv")
    target_df = target_df[target_df["title"] != '']
    target_df.to_sql(con=mysql_conn, name="target_video_title", if_exists="replace")
    source_df = load_data("data/source/*.csv")
    source_df.to_sql(con=mysql_conn, name="free_jav_video_title", if_exists="replace")


def matching():
    logging.info("Matching target titles to freejav.video titles")
    target_title_query = '''
        SELECT distinct(title) FROM jav_scrape.target_video_title where title is not NULL;
    '''

    target_titles = mysql_conn.execute(target_title_query).fetchall()
    target_titles = [target_title[0] for target_title in target_titles]
    logging.info("Got %s titles from target" % str(len(target_titles)))

    free_jav_titles = pd.read_sql_table(table_name="free_jav_video_title", con=mysql_conn)

    matched_index = []
    for index, row in free_jav_titles.iterrows():
        title = row.title

        for target_title in target_titles:
            if (target_title in title and len(target_title) > 5) \
                    or target_title == title:
                logging.info("Matched title %(target_title)s in target titles and title %(source_title)s in freejava.video",
                             {'target_title': target_title, 'source_title': title})
                matched_index.append(index)
                break

    logging.info("Matching target titles to freejav.video titles completed with %s pairs matched" % str(len(matched_index)))
    free_jav_titles = free_jav_titles.iloc[matched_index]
    free_jav_titles.to_csv("data/matched.csv")
    while True:
        try:
            free_jav_titles.to_sql(con=mysql_conn, name="free_jav_matched_title", if_exists="replace")
            break
        except:
            pass

# matching()
crawled_data = load_data("data/crawl/*.csv")
crawled_data.to_sql(con=mysql_conn, name="free_jav_video_detail", if_exists="replace")