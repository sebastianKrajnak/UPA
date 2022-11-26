import requests
from bs4 import BeautifulSoup
from pandas import DataFrame


def get_urls_from_args():
    # TODO
    pass


# jen pro testovaci ucely, nakonec smazat
def get_10_urls_from_file():
    with open('urls.txt', 'r') as f:
        urls = [line[:-1] for line in f.readlines()]
    return urls[:10]


def get_data_from_urls(urls):
    data = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        game_name = soup.find("h1", class_="title-h1").contents[0]
        price = soup.find("div", class_="detail__price").contents[0]
        data.append((url, game_name, price))
    return data


def write_data(data):
    df = DataFrame.from_records(data)
    df.to_csv("data.tsv", sep="\t", header=False, index=False)
        

if __name__ == "__main__":
    # urls = get_urls_from_args()
    urls = get_10_urls_from_file()
    data = get_data_from_urls(urls)
    write_data(data)
    

