#!/usr/bin/python3.6

import os
import csv
import time
import random
import requests
from bs4 import BeautifulSoup as bs


def main():

    total_pages = 2551
    scrape(total_pages, 2, 6)


def scrape(total_pages, interval, offset):

    currentPath = os.getcwd()
    csv_file = currentPath + "/data/data_{}.csv".format(int(time.time()))

    time_start = time.time()

    # for each page, collect data and append to csv file

    for page in range(1, total_pages):
        print("Scraping page {} out of {}: {}% complete... time elapsed: {}".format(page, total_pages, ((page / total_pages)*100),
              time.strftime("%H:%M:%S", time.gmtime(time.time()-time_start))))

        # sleep for a random time interval so we dont get banned
        time.sleep(interval + random.randint(0, offset))

        resp = requests.get("https://store.steampowered.com/search/?hide_filtered_results_warning=1&ignore_preferences=1&page={}".format(page))
        html = bs(resp.content, "html.parser")

        links = collect_links(html)
        titles = collect_titles(html)

        csv_data_list = []

        for x in range(0, len(titles)):
            csv_data_list.append([titles[x], links[x]])

        write_to_csv(csv_file, csv_data_list)

    print("Done!")


def write_to_csv(csv_file, data_list):
    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.writer(csvfile, dialect='excel',
                                quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
            for data in data_list:
                writer.writerow(data)
    except IOError as strerror:
        print("I/O error({0})".format(strerror))
    return


def collect_titles(html):
    result = []
    for title in html.findAll('span', {'class': 'title'}):
        result.append(title.getText())

    return result


def collect_links(html):
    result = []
    for link in html.findAll('a', {'class': 'search_result_row'}):
        item = link['href'].rsplit('?', 1)[0]
        result.append(item)

    return result


if __name__ == "__main__":
    main()
