import sys
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame


def get_urls_from_stdin():
    return [line[:-1] for line in sys.stdin.readlines()]


def get_data_from_urls(urls):
    data = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        game_name = soup.find("h1", class_="title-h1").contents[0]
        price = soup.find("div", class_="detail__price").contents[0]
        priceFloat = float(str(price).replace("\xa0", "")[:-3])
        data.append((url, game_name, priceFloat))
    return data


def write_data(data):
    df = DataFrame.from_records(data)
    df.to_csv("dataDemo20.tsv", sep="\t", header=False, index=False)


if __name__ == "__main__":
    urls = get_urls_from_stdin()
    data = get_data_from_urls(urls)
    write_data(data)
