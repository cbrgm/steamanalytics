#!/usr/bin/python3.6

import requests
from datetime import datetime
import time
import random
import re
from steam.models import Product
from steam.date_formatter import DateFormatter
from bs4 import BeautifulSoup


class Scraper:
    interval = 5
    offset = 3

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

    def scrape_all(self, urls):

        # run preflight checks
        if len(urls) == 0 or urls is None:
            raise RuntimeError('no urls to scrape provided')

        products = []

        for url in urls:
            product = self.scrape(url)
            if product is not None:
                products.append(product)

            # wait before next request
            time.sleep(self.interval + random.randint(0, self.offset))

        return products

    def scrape(self, url):
        """
        scrape receives an url and parses the result into a json object.
        """

        # check if url is valid
        if url == "":
            print('url provided was empty... skipping')
            return None

        # only allow steam app urls
        pattern = re.compile("https://store.steampowered.com/app/[\d]*/.+")
        if not pattern.match(url):
            print('url {} does not match the allowed url format... skipping)'.format(url))
            return None

        # use a cookie to skip age verification and mature content confirmation
        cookies = {'birthtime': '568022401', 'mature_content': '1'}
        product = Product()

        # get the html data and parse it
        response = requests.get(url, cookies=cookies, headers={'User-Agent': 'Mozilla/5.0'})
        html = BeautifulSoup(response.content, 'html.parser')

        if not len(html.text) > 0:
            print('failed to query page content... skipping')
            return None

        # try to parse every attribute from the content
        product.id = self.__get_id(url)
        product.app_name = self.__get_app_name(html)
        product.url = self.__get_product_url(url)
        product.image_url = self.__get_image_url(html)
        product.is_dlc = self.__is_dlc(html)
        product.description = self.__get_description(html)
        product.release_date = self.__get_release_date(html)

        product.developers = self.__get_developers(html)
        product.publisher = self.__get_publisher(html)

        product.genres = self.__get_genres(html)
        product.tags = self.__get_tags(html)
        product.categories = self.__get_categories(html)

        product.price = self.__get_price(html)
        product.price_discount = self.__get_price_discount(html)
        product.languages = self.__get_languages(html)

        product.review_summary = self.__get_review_summary(html)
        product.reviews_total = self.__get_reviews_total(html)

        return product

    def __get_app_name(self, soup):
        """
        returns the games app name
        """
        try:
            return soup.findAll('div', {"class": "apphub_AppName"})[0].text.strip()
        except Exception:
            return ""

    def __get_image_url(self, soup):
        """
        returns the games image url
        """
        try:
            return soup.find('img', {"class": "game_header_image_full"})['src']
        except Exception:
            return ""

    def __get_product_url(self, url):
        """
        returns the product id from the games url
        """
        try:
            return url.rstrip('/').rsplit('/', 1)[0]
        except Exception:
            return ""

    def __get_id(self, url):
        """
        returns the games steamapp id
        """
        try:
            return int(url.rstrip('/').rsplit('/', 2)[-2])
        except Exception:
            return -1

    def __get_developers(self, soup):
        """
        returns all developers for the given game
        """

        result = []
        try:
            for link in soup.findAll('div', {"id": "developers_list"})[0].findAll('a', href=True):
                result.append(link.text)
            return result
        except Exception:
            return result

    def __get_publisher(self, soup):
        """
        returns the publisher of the given game
        """
        try:
            return soup.findAll('div', {"class": "dev_row"})[1].find('a', href=True).text
        except Exception:
            return ""

    def __get_release_date(self, soup):
        """
        returns the release date of the game
        """
        try:
            datestring = soup.find('div', {"class": "release_date"}).find('div', {"class": "date"}).text
            date = self.date_formatter.format_date(datestring)
            return date
        except Exception:
            return ""

    def __get_genres(self, soup):
        """
        returns all genres for the given game
        """

        result = []
        try:
            details = soup.find('div', {"class": "details_block"})

            genre = details.find('a').get_text()
            result.append(genre)

            genreNext = details.find('a')
            while True:
                if genreNext.next_sibling.next_sibling.name == 'a':
                    result.append(genreNext.next_sibling.next_sibling.get_text())
                    genreNext = genreNext.next_sibling.next_sibling
                else:
                    break
            return result
        except Exception:
            return result

    def __get_tags(self, soup):
        """
        return all tags for the given game
        """
        result = []
        try:
            for link in soup.find('div', {"class": "glance_tags popular_tags"}).findAll('a', {'class': 'app_tag'}):
                result.append(link.text.strip())
            return result
        except Exception:
            return result

    def __get_languages(self, soup):
        """
        return all languages for the given game
        """
        result = []
        try:
            for row in soup.find('table', {"class": "game_language_options"}).findAll('td', {'class': 'ellipsis'}):
                result.append(row.text.strip())
            return result
        except Exception:
            return result

    def __get_categories(self, soup):
        """
        returns all categories for the given game
        """

        result = []
        try:
            for row in soup.find('div', {"id": "category_block"}).findAll('div', {'class': 'game_area_details_specs'}):
                category = row.find('a', {"class": "name"}).text.strip()
                if category:
                    result.append(category)
            return result
        except Exception:
            return result

    def __get_price(self, soup):
        """
        returns the original game price without any discounts
        """
        price = 0.00

        # try to find the normal price from discount
        try:
            result = soup.find('div', {"class":
                                      "discount_original_price"}).text.strip()
            price = self.formatPrice(result)
            return price
        except Exception:
            pass

        if price is not 0.00:
            return price

        # try to find the normal price without discount
        try:
            result = soup.find('div', {"class": "game_purchase_price price"}).text.strip()
            price = self.formatPrice(result)
            return price
        except Exception:
            pass

        return 0.00

    def formatPrice(self, price_string):
        """
        formats the price and returns a float with format 0.00
        """
        parsed_string = ''.join(filter(lambda i: i.isdigit() or i == "-", price_string))
        parsed_string.replace('-', '0')
        if parsed_string is not "":
            parsed_string = parsed_string.replace('-', '0')
            price = parsed_string[:-2] + "." + parsed_string[-2:]
            return float(price)
        else:
            return 0.00

    def __get_price_discount(self, soup):
        """
        returns the games discounted price.
        if no discount is available, the original price will be returned
        """

        # try to find the discounted price
        try:
            result = soup.find('div', {"class":
                                      "discount_final_price"}).text.strip()
            price = self.formatPrice(result)
            return price
        except Exception:
            pass

        return self.__get_price(soup)

    def __get_reviews_total(self, soup):
        """
        returns the total amount of reviews as an int
        """
        result = 0
        try:
            result = soup.findAll('div', {"class": "summary column"})[1].find('span', {"class": "responsive_hidden"}).text.strip()
            result = result.replace(",", "").replace("(", "").replace(")", "")
            return int(result)
        except Exception:
            return int(result)

    def __get_review_summary(self, soup):
        """
        returns the review summary string
        """
        result = "None"
        try:
            result = soup.findAll('div', {"class": "summary column"})[1].find('span', {"class": "game_review_summary"}).text.strip()
            return result
        except Exception:
            return result

    def __get_description(self, soup):
        """
        returns the games description
        """
        result = ""
        try:
            result = soup.find('div', {"class":
                                       "game_description_snippet"}).text.split()
            return ' '.join(result)
        except Exception:
            return result

    def __is_dlc(self, soup):
        """
        returns true if the game is a dlc, false if not
        """
        is_dlc = False
        try:
            dlc = soup.find('div', {"class": "game_area_dlc_bubble"}).find('h1').text
            if dlc == "Downloadable Content":
                is_dlc = True
            return is_dlc
        except Exception:
            return is_dlc
