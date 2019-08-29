from steam.scraper import Scraper
from bs4 import BeautifulSoup as soup
from rethinkdb import RethinkDB
import requests
import json
import os


def main():

    # load the config
    config_interval = int(os.environ['SCRAPE_INTERVAL'])
    config_offset = int(os.environ['SCRAPE_OFFSET'])
    config_rethink_host = os.environ['RETHINK_HOST']
    config_rethink_port = int(os.environ['RETHINK_PORT'])
    config_rethink_db = os.environ['RETHINK_DB']
    config_rethink_table = os.environ['RETHINK_TABLE']
    config_rethink_user = os.environ['RETHINK_USER']
    config_rethink_pass = os.environ['RETHINK_PASS']

    # load the scraper
    scraper = Scraper(config_interval, config_offset)

    # try to establish database connection
    db = RethinkDB()
    db.connect(host=config_rethink_host,
               port=config_rethink_port,
               db=config_rethink_db,
               user=config_rethink_user,
               password=config_rethink_pass).repl()

    # migrate database if necessary
    setup_db(db, config_rethink_db, config_rethink_table)

    while True:
        # get total amount of search pages
        print("querying the total amount of pages to scrape from the steam store search...")

        total_pages = get_total_pages()
        print("found {} pages to scrape... starting now!".format(total_pages))
        for page in range(1, total_pages):

            print("scraping page {} out of {}: {}% complete...".format(page,
                                                                       total_pages,
                                                                       ((page /
                                                                         total_pages)*100)))
            urls = get_product_urls(page)
            if len(urls) == 0:
                continue

            products = scraper.scrape_all(urls)
            json_string = json.dumps(products, default=lambda x: x.__dict__)
            data = json.loads(json_string)
            db.table(config_rethink_table).insert(data).run()

def get_product_urls(page):
    """
    returns a list of urls from a steam store search page to be scraped by the
    scraper
    """

    resp = requests.get("https://store.steampowered.com/search/?hide_filtered_results_warning=1&ignore_preferences=1&page={}".format(page))
    html = soup(resp.content, "html.parser")

    result = []
    for link in html.findAll('a', {'class': 'search_result_row'}):
        item = link['href'].rsplit('?', 1)[0]
        result.append(item)

    return result


def get_total_pages():
    """
    returns the total amount of pages from the steam store search
    """
    resp = requests.get("https://store.steampowered.com/search/?hide_filtered_results_warning=1&ignore_preferences=1&page=1") 
    html = soup(resp.content, "html.parser")

    total_pages = html.find('div', {'class': 'search_pagination'}).find('div', {'class': 'search_pagination_right'}).findAll('a')[-2].text
    return int(total_pages)


def setup_db(db, db_name, db_table):
    """
    creates database and table if not exists
    """
    print("checking if database {} and table {} are present...".format(db_name, db_table))
    try:
        exists = False

        databases = db.db_list().run()
        for database in databases:
            if database == db_name:
                exists = True
                break

        if not exists:
            print("creating database {}...".format(db_name))
            db.db_create(db_name).run()
    except RethinkDB.ReqlRuntimeError:
        print("database {} already exists... skipping".format(db_name))

    try:
        exists = False

        tables = db.db(db_name).table_list().run()
        for table in tables:
            if table == db_table:
                exists = True
                break

        if not exists:
            print("creating table {} in database {}...".format(db_table,
                                                                    db_name))
            db.db(db_name).table_create(db_table).run()
    except RethinkDB.ReqlOpFailedError:
        print("table {} already exists... skipping".format(db_table))


if __name__ == "__main__":
    main()
