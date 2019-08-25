#!/usr/bin/python3.6

import requests
from datetime import datetime
import time
import random
from steam.models import Product
from steam.date_formatter import DateFormatter
from bs4 import BeautifulSoup


class Scraper:
    base_url = 'http://store.steampowered.com/'
    urls = ''
    interval = 1
    offset = 0

    def __init__(self, interval, offset):
        self.interval = interval
        self.offset = offset

        self.date_formatter = DateFormatter("%Y-%m-%d")
        self.date_formatter.add_input_format("%b %d, %Y")
        self.date_formatter.add_input_format("%B %d, %Y")
        self.date_formatter.add_input_format("%d %b, %Y")
        self.date_formatter.add_input_format("%d %B, %Y")
        self.date_formatter.add_input_format("%b %d %Y")
        self.date_formatter.add_input_format("%B %d %Y")
        self.date_formatter.add_input_format("%d %b %Y")
        self.date_formatter.add_input_format("%d %B %Y")
        self.date_formatter.add_input_format("%b %Y")

    def set_urls(self, urls):
        self.urls = urls

    def set_url(self, url):
        self.urls = [url]

    def scrape_all(self):

        # run preflight checks
        if not self.urls:
            raise RuntimeError('no urls to scrape provided')

        products = []

        for url in self.urls:
            product = self.scrape(url)
            if product is not None:
                products.append(product)

            # wait before next request
            time.sleep(self.interval + random.randint(0, self.offset))

        return products

    def scrape(self, url):
        # check if url is valid

        # use a cookie to skip age verification and mature content confirmation
        cookies = {'birthtime': '568022401', 'mature_content': '1'}
        product = Product()

        # get the html data and parse it
        response = requests.get(url, cookies=cookies, headers={'User-Agent': 'Mozilla/5.0'})
        html = BeautifulSoup(response.content, 'html.parser')

        if not len(html.text) > 0:
            print('failed')
            return None

        # try to parse every attribute from the content
        product.id = self.__get_id(url)
        product.app_name = self.__get_app_name(html)
        product.url = self.__get_product_url(url)
        product.image_url = self.__get_image_url(html)
        product.release_date = self.__get_release_date(html)

        product.developers = self.__get_developers(html)
        product.publisher = self.__get_publisher(html)

        product.genres = self.__get_genres(html)
        product.tags = self.__get_tags(html)
        product.categories = self.__get_categories(html)

        product.price = 0.00
        product.price_discount = 0.00
        product.languages = self.__get_languages(html)

        product.review_summary = 'missing'
        product.reviews_total = 0
        product.metacritic_score = ''

        return product

    def __get_app_name(self, soup):
        return soup.findAll('div', {"class": "apphub_AppName"})[0].text.strip()

    def __get_image_url(self, soup):
        return soup.find('img', {"class": "game_header_image_full"})['src']

    def __get_product_url(self, url):
        return url.rstrip('/').rsplit('/', 1)[0]

    def __get_id(self, url):
        return url.rstrip('/').rsplit('/', 2)[-2]

    def __get_developers(self, soup):
        result = []
        for link in soup.findAll('div', {"id": "developers_list"})[0].findAll('a', href=True):
            result.append(link.text)
        return result

    def __get_publisher(self, soup):
        return soup.findAll('div', {"class": "dev_row"})[1].find('a', href=True).text

    def __get_release_date(self, soup):
        datestring = soup.find('div', {"class": "release_date"}).find('div', {"class": "date"}).text
        date = self.date_formatter.format_date(datestring)

        return date

    def __get_genres(self, soup):
        result = []
        detail = soup.find('div', {"class": "details_block"})

        if "Genre" in detail:
            splitted_links = detail.split('</b>')[1].split(", <a")
            for link in splitted_links:
                result.append(link.split("\">")[1].replace('</a>', ''))

        return result

    def __get_tags(self, soup):
        result = []
        for link in soup.find('div', {"class": "glance_tags popular_tags"}).findAll('a', {'class': 'app_tag'}):
            result.append(link.text.strip())
        return result

    def __get_languages(self, soup):
        result = []
        for row in soup.find('table', {"class": "game_language_options"}).findAll('td', {'class': 'ellipsis'}):
            result.append(row.text.strip())
        return result

    def __get_categories(self, soup):
        result = []
        for row in soup.find('div', {"id": "category_block"}).findAll('div', {'class': 'game_area_details_specs'}):
            category = row.find('a', {"class": "name"}).text.strip()
            if category:
                result.append(category)
        return result
