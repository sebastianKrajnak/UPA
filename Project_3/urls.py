import requests
from bs4 import BeautifulSoup


def get_games():
    page = 1
    has_next = True
    games = []

    while (len(games) < 300 and has_next):
        r = requests.get(f"https://www.key4you.cz/hry/akcni/stranka/{page}/")
        soup = BeautifulSoup(r.content, "html.parser")
        items = soup.find_all("div", class_="product")
        games += items    
        page += 1
        
        next_button = soup.find("a", attrs={"rel": "next"})
        if not next_button:
            has_next = False               
    return games


def write_urls(urls):
    with open('urls.txt', 'w') as f:
        f.write('\n'.join(urls))
        

if __name__ == "__main__":
    games = get_games()
    urls = [game.find("a")["href"] for game in games]
    write_urls(urls)