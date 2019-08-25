from steam.scraper import Scraper
import json

def main():

    # load the config
    test_urls = [
        #"http://store.steampowered.com/app/316790/",  # Grim Fandango
        #"http://store.steampowered.com/app/207610/",  # The Walking Dead
        "https://store.steampowered.com/app/812140/Assassins_Creed_Odyssey/"   # Outlast 2
    ]

    # create a new scraper
    scraper = Scraper(1, 0)
    scraper.set_urls(test_urls)

    products = scraper.scrape_all()

    print(json.dumps(products, default=lambda o: o.__dict__))


if __name__ == "__main__":
    main()
