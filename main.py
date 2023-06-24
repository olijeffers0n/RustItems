import json, time, requests
from collections import defaultdict
from bs4 import BeautifulSoup

def main() -> None:
    headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    response = requests.get('https://rustlabs.com/group=itemlist', headers=headers)

    output_json = defaultdict(list)
    output_markdown = "|Name|Image|ID|Stack Size|Despawn Time|\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    soup = BeautifulSoup(response.content, 'html.parser')
    info_blocks = soup.find_all('div', class_='info-block group')

    current_heading = ""
    for info_block in info_blocks[0].find_all(recursive=False):
        if info_block.name == "h2":
            current_heading = info_block.getText()
        else:
            item_url = "https://rustlabs.com" + info_block.get_attribute_list("href")[0]
            td = []
            try:
                item = requests.get(item_url, headers=headers)
                bs = BeautifulSoup(item.content, "html.parser")
                td = bs.find_all(class_="stats-table")[0].find_all("td")
            except Exception as e: print(f"Error occured while trying to scrape {item_url} for ID. Exception {e}")
            name = info_block.find_all(class_="r-cell")[0].getText()
            image = "https:" + info_block.find_all("img")[0]["src"]
            appending = {
                "name": name,
                "image": image,
                "id": "N/A",
                "stacksize": "N/A",
                "despawntime": "N/A"
            }
            if td != [] and len(td) >= 6:
                appending["id"] = str(td[1]).replace("<td>", "").replace("</td>", "")
                appending["stacksize"] = str(td[3]).replace("<td>", "").replace("</td>", "").replace("×", "x")
                appending["despawntime"] = str(td[5]).replace("<td>", "").replace("</td>", "").replace("min ", "mins").replace("hour ", "hour")
            output_json[current_heading].append(appending)

            output_markdown += f"|{name}|![]({image})|{appending['id']}|{appending['stacksize']}|{appending['despawntime']}|\n"
            time.sleep(1)

    with open("data/items.md", "w") as md_out:
        md_out.write(output_markdown)

    with open("data/items.json", "w") as json_out:
        json_out.write(json.dumps(output_json, indent=3))

if __name__ == '__main__':
    main()
