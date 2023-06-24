import json
import bs4.element
import requests
import time
import progressbar
from collections import defaultdict

from bs4 import BeautifulSoup

HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }


def extract_item_data(href: str, info_block: bs4.Tag) -> dict:
    item_url = "https://rustlabs.com" + href

    appending = {
        "name": info_block.find_all(class_="r-cell")[0].getText(),
        "image": "https:" + info_block.find_all("img")[0]["src"],
        "id": "N/A",
        "stack_size": "N/A",
        "despawn_time": "N/A"
    }

    try:
        item = requests.get(item_url, headers=HEADERS)

        if item.status_code != 200:
            return appending

        bs = BeautifulSoup(item.content, "html.parser")
        td = bs.find_all(class_="stats-table")[0].find_all("td")
    except Exception as e:
        print(f"Error occurred while trying to scrape {item_url} for ID. Exception {e}")
        return appending

    if td != [] and len(td) >= 6:
        appending["id"] = td[1].getText()
        appending["stack_size"] = td[3].getText().replace("×", "")
        appending["despawn_time"] = td[5].getText().replace("min ", "mins").replace("hour ", "hour")

    return appending


def main() -> None:

    response = requests.get('https://rustlabs.com/group=itemlist', headers=HEADERS)

    if response.status_code != 200:
        print("An Error Has Occurred with request")
        quit(1)

    output_json = defaultdict(list)
    output_markdown = "|Name|Image|ID|Stack Size|Despawn Time|\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    soup = BeautifulSoup(response.content, 'html.parser')
    info_blocks = soup.find_all('div', class_='info-block group')

    current_heading = ""
    blocks = info_blocks[0].find_all(recursive=False)
    bar = progressbar.ProgressBar(maxval=len(blocks), widgets=[progressbar.Bar('=', '[', ']'), ' ',
                                                               progressbar.Percentage()])
    bar.start()

    for i, info_block in enumerate(blocks):
        if info_block.name == "h2":
            current_heading = info_block.getText()
        else:
            data = extract_item_data(info_block.get_attribute_list("href")[0], info_block)

            output_json[current_heading].append(data)
            output_markdown += f"|{data['name']}|![]({data['image']})|{data['id']}|{data['stack_size']}|" \
                               f"{data['despawn_time']}|\n"
            bar.update(i + 1)
            time.sleep(0.5)

    bar.finish()

    with open("data/items.md", "w") as md_out:
        md_out.write(output_markdown)

    with open("data/items.json", "w") as json_out:
        json_out.write(json.dumps(output_json, indent=3))


if __name__ == '__main__':
    main()
