from steam.scraper import Scraper
import json


def main():

    # load the config
    test_urls = [
        "https://store.steampowered.com/app/812140/Assassins_Creed_Odyssey/",  # Outlast 2
        "https://store.steampowered.com/sub/354231/",
        "https://store.steampowered.com/app/351640/Eternal_Senia/",
        "https://store.steampowered.com/app/819780/The_Singularity_Wish/",
        "https://store.steampowered.com/app/937891/Assassins_Creed_Odyssey__Legacy_of_the_First_Blade/",
        "https://store.steampowered.com/app/1091500/Cyberpunk_2077",
    ]

    # create a new scraper
    scraper = Scraper(1, 0)
    products = scraper.scrape_all(test_urls)

    print(json.dumps(products, default=lambda o: o.__dict__))


if __name__ == "__main__":
    main()
