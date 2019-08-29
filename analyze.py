from rethinkdb import RethinkDB
from datetime import datetime
import matplotlib.pyplot as plt
import os


def main():

    # load the config
    config_rethink_host = os.environ['RETHINK_HOST']
    config_rethink_port = int(os.environ['RETHINK_PORT'])
    config_rethink_user = os.environ['RETHINK_USER']
    config_rethink_pass = os.environ['RETHINK_PASS']

    db_name = 'steam'
    db_table = 'products'

    r = RethinkDB()
    r.connect(host=config_rethink_host,
               port=config_rethink_port,
               db=db_name,
               user=config_rethink_user,
               password=config_rethink_pass).repl()

    cursor = r.db('steam').table('products').pluck('release_date').run()

    releases = {}
    for doc in cursor:
        if doc['release_date'] == "":
            continue
        try:
            rel = datetime.strptime(doc['release_date'],
                                         '%Y-%m-%d')
            if rel.year in releases:
                releases[rel.year] += 1
            else:
                releases[rel.year] = 1
        except Exception:
            pass

    # start building the plot
    # https://matplotlib.org/examples/api/date_demo.html

    x = []
    y = []
 
    for key in sorted(releases.keys()):
        x.append(key)
        y.append(releases[key])


    plt.grid(True)
    plt.xticks(list(date for date in range(1987,2019)))
    plt.xlabel('years')
    plt.ylabel('releases')
    plt.plot(x, y)
    plt.show()


if __name__ == "__main__":
    main()
